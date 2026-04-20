import os
import sys
import types as _types

# ── ANSI colors (no third-party deps) ─────────────────────────────────────────
if sys.platform == 'win32':
    os.system('')           # enable VT100 on Windows 10+

_USE_COLOR = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

def _c(text, code=''):
    return f'\033[{code}m{text}\033[0m' if (_USE_COLOR and code) else text

CYAN   = '96'
GREEN  = '92'
RED    = '91'
DIM    = '2'
YELLOW = '93'
BOLD   = '1'

def _prompt(text):
    """Wrap prompt text so readline counts width correctly on Unix."""
    if not _USE_COLOR:
        return text
    return f'\001\033[{CYAN}m\002{text}\001\033[0m\002'

# ── readline / history ─────────────────────────────────────────────────────────
try:
    import readline as _rl
    _HIST = os.path.join(os.path.expanduser('~'), '.ypool_history')
    try:
        _rl.read_history_file(_HIST)
    except FileNotFoundError:
        pass
    import atexit
    atexit.register(_rl.write_history_file, _HIST)
    _HAS_RL = True
except ImportError:
    try:
        import pyreadline3 as _rl          # type: ignore
        _HAS_RL = True
    except ImportError:
        _rl      = None
        _HAS_RL  = False

from src.lexer       import Lexer, KEYWORDS, YPoolError
from src.parser      import Parser
from src.interpreter import Interpreter, YPoolFunction

# ── session history (for :save / :history) ────────────────────────────────────
_session_history: list[str] = []

# ── statement-starting keywords (skip expression mode for these) ──────────────
_STMT_STARTS = {
    'MAKE', 'FIX', 'SHOW', 'CHECK', 'MATCH', 'KEEP', 'FOR', 'COUNT',
    'TEACH', 'GIVE', 'COMBINE', 'PUSH', 'POP', 'UPDATE', 'REMOVE',
    'SORT', 'REVERSE', 'STOP', 'SKIP', 'TRY', 'THROW', 'WRITE', 'BRING',
    'REPEAT', 'ASSERT', 'MEMOIZE', 'BRIDGE',
}

# ── brace-depth counter ────────────────────────────────────────────────────────
def _brace_depth(text: str) -> int:
    depth, in_str, qc = 0, False, ''
    for ch in text:
        if in_str:
            if ch == qc: in_str = False
        elif ch in ('"', "'"):
            in_str, qc = True, ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
    return depth

# ── tab completion ─────────────────────────────────────────────────────────────
def _setup_completion(interp: Interpreter) -> None:
    if not _HAS_RL:
        return
    kw_list = sorted(KEYWORDS.keys())
    cmd_list = [':help', ':vars', ':clear', ':run', ':save', ':history', ':type', ':quit']

    def _complete(text, state):
        candidates = []
        # REPL commands
        if text.startswith(':'):
            candidates = [c for c in cmd_list if c.startswith(text)]
        else:
            # Keywords (if text looks like it might be a keyword)
            upper = text.upper()
            candidates += [k + ' ' for k in kw_list if k.startswith(upper) and text == text.upper()]
            # User variables
            candidates += [n for n in sorted(interp.globals.vars)
                           if n.startswith(text) and not isinstance(interp.globals.vars[n], _types.FunctionType)]
        try:
            return candidates[state]
        except IndexError:
            return None

    _rl.set_completer(_complete)
    _rl.parse_and_bind('tab: complete')

# ── input collection (handles multi-line blocks) ───────────────────────────────
def _collect_input() -> str | None:
    try:
        line = input(_prompt('ypool> '))
    except (KeyboardInterrupt, EOFError):
        return None
    source = line
    depth  = _brace_depth(line)
    while depth > 0:
        try:
            cont   = input(_prompt('  ...> '))
            source += '\n' + cont
            depth  += _brace_depth(cont)
        except (KeyboardInterrupt, EOFError):
            print()
            return None
    return source

# ── error display ──────────────────────────────────────────────────────────────
def _print_error(e: YPoolError, source: str = '') -> None:
    print(_c(str(e), RED))
    if e.line is not None and source:
        lines = source.splitlines()
        idx   = e.line - 1
        if 0 <= idx < len(lines):
            print(_c(f'  {lines[idx]}', DIM))
            print(_c('  ^', RED))
    stack = getattr(e, '_ypool_stack', None)
    if stack:
        print(_c('  traceback:', DIM))
        for frame in reversed(stack):
            print(_c(f'    in {frame}()', DIM))

# ── :vars display ──────────────────────────────────────────────────────────────
def _show_vars(interp: Interpreter) -> None:
    user = {k: v for k, v in interp.globals.vars.items()
            if not isinstance(v, _types.FunctionType)}
    if not user:
        print(_c('  (nothing defined yet)', DIM))
        return
    width = max(len(k) for k in user)
    for name in sorted(user):
        val   = user[name]
        tag   = _c(' [const]', YELLOW) if name in interp.globals.consts else ''
        kind  = _c(interp._kind_of(val), DIM)
        value = _c(interp.ypool_str(val), GREEN)
        print(f'  {_c(name, CYAN):<{width + 10}}{tag}  {kind}  {value}')

# ── :commands ──────────────────────────────────────────────────────────────────
def _run_command(cmd_line: str, interp: Interpreter) -> tuple[bool, Interpreter]:
    parts = cmd_line[1:].split(None, 1)
    cmd   = parts[0].lower() if parts else ''
    arg   = parts[1].strip() if len(parts) > 1 else ''

    if cmd in ('q', 'quit', 'exit'):
        return True, interp

    elif cmd == 'help':
        print(f"""
  {_c(':vars',    CYAN)}               list all user-defined variables
  {_c(':type',    CYAN)} <name>        show the type of a variable
  {_c(':clear',   CYAN)}               wipe the scope and start fresh
  {_c(':run',     CYAN)} <file>        load and run a .yp file into current scope
  {_c(':save',    CYAN)} <file>        save this session to a .yp file
  {_c(':history', CYAN)} [n]           show last n commands (default: all)
  {_c(':help',    CYAN)}               show this message
  {_c(':quit',    CYAN)}               exit the REPL
""".rstrip())

    elif cmd == 'vars':
        _show_vars(interp)

    elif cmd == 'type':
        if not arg:
            print('  usage: :type <varname>')
        else:
            try:
                val  = interp.globals.get(arg)
                kind = interp._kind_of(val)
                print(f'  {_c(arg, CYAN)} : {_c(kind, YELLOW)}')
            except YPoolError:
                print(_c(f'  "{arg}" is not defined', RED))

    elif cmd == 'clear':
        interp = Interpreter()
        _setup_completion(interp)
        print(_c('  scope cleared.', DIM))

    elif cmd == 'run':
        if not arg:
            print('  usage: :run <filename.yp>')
        else:
            try:
                with open(arg, 'r', encoding='utf-8') as f:
                    src = f.read()
                tokens = Lexer(src).tokenize()
                ast    = Parser(tokens).parse()
                interp.run(ast)
                _setup_completion(interp)
            except FileNotFoundError:
                print(_c(f'  not found: {arg}', RED))
            except YPoolError as e:
                _print_error(e, arg)

    elif cmd == 'save':
        if not arg:
            print('  usage: :save <filename.yp>')
        else:
            fname = arg if arg.endswith('.yp') else arg + '.yp'
            try:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(_session_history) + '\n')
                print(_c(f'  saved {len(_session_history)} entries to {fname}', GREEN))
            except OSError as e:
                print(_c(f'  cannot save: {e}', RED))

    elif cmd == 'history':
        n = int(arg) if arg.isdigit() else len(_session_history)
        entries = _session_history[-n:]
        start   = max(1, len(_session_history) - n + 1)
        for i, entry in enumerate(entries, start=start):
            first_line = entry.split('\n')[0]
            suffix     = _c(' ...', DIM) if '\n' in entry else ''
            print(f'  {_c(str(i).rjust(4), DIM)}  {first_line}{suffix}')

    else:
        print(_c(f'  unknown command ":{cmd}"  —  type :help', RED))

    return False, interp

# ── expression mode ────────────────────────────────────────────────────────────
def _try_as_expr(source: str, interp: Interpreter) -> bool:
    first = source.strip().split()[0].upper() if source.strip() else ''
    if first in _STMT_STARTS:
        return False
    try:
        tokens = Lexer(source).tokenize()
        p      = Parser(tokens)
        expr   = p.parse_condition()
        if not p.at_end():
            return False
        val = interp.eval(expr, interp.globals)
        if val is not None:
            print(_c(f'=> {interp.ypool_str(val)}', GREEN))
        return True
    except Exception:
        return False

# ── main REPL loop ─────────────────────────────────────────────────────────────
def run_repl(interp: Interpreter = None) -> None:
    global _session_history
    if interp is None:
        interp = Interpreter()

    # Load ~/.ypool_rc
    rc_path = os.path.join(os.path.expanduser('~'), '.ypool_rc')
    if os.path.isfile(rc_path):
        try:
            with open(rc_path, 'r', encoding='utf-8') as f:
                rc_src = f.read()
            tokens = Lexer(rc_src).tokenize()
            interp.run(Parser(tokens).parse())
            print(_c(f'  loaded ~/.ypool_rc', DIM))
        except Exception as e:
            print(_c(f'[rc error] {e}', RED))

    _setup_completion(interp)

    rl_note = '' if _HAS_RL else _c('  (pip install pyreadline3 for persistent history)', DIM)
    print(f'{_c("ypool v1.0 REPL", CYAN + ";1")}  —  :help for commands  •  Ctrl+C to quit')
    if rl_note:
        print(rl_note)
    print()

    while True:
        source = _collect_input()
        if source is None:
            print('\ngoodbye.')
            break

        source = source.strip()
        if not source:
            continue

        # REPL commands
        if source.startswith(':'):
            should_exit, interp = _run_command(source, interp)
            if should_exit:
                print('goodbye.')
                break
            continue

        # Record to session history
        _session_history.append(source)

        try:
            if _try_as_expr(source, interp):
                _setup_completion(interp)
                continue

            tokens = Lexer(source).tokenize()
            ast    = Parser(tokens).parse()
            result = interp.run(ast)

            if result is not None:
                print(_c(f'=> {interp.ypool_str(result)}', GREEN))

            _setup_completion(interp)

        except YPoolError as e:
            _print_error(e, source)
        except RecursionError:
            print(_c('[ypool] recursion limit reached', RED))


if __name__ == '__main__':
    run_repl()
