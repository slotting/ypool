import os
import sys
import types as _types

# ── readline (history + arrow keys across sessions) ────────────────────────────
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
        import pyreadline3 as _rl  # type: ignore
        _HAS_RL = True
    except ImportError:
        _HAS_RL = False

from src.lexer   import Lexer, YPoolError
from src.parser  import Parser
from src.interpreter import Interpreter, YPoolFunction

# ── keywords that begin a statement (not bare expressions) ─────────────────────
_STMT_STARTS = {
    'MAKE', 'FIX', 'SHOW', 'CHECK', 'MATCH', 'KEEP', 'FOR', 'COUNT',
    'TEACH', 'GIVE', 'COMBINE', 'PUSH', 'POP', 'UPDATE', 'REMOVE',
    'SORT', 'REVERSE', 'STOP', 'SKIP', 'TRY', 'THROW', 'WRITE', 'BRING',
    'REPEAT',
}


def _brace_depth(text: str) -> int:
    """Count net open braces, ignoring those inside string literals."""
    depth = 0
    in_str, qchar = False, ''
    for ch in text:
        if in_str:
            if ch == qchar:
                in_str = False
        elif ch in ('"', "'"):
            in_str, qchar = True, ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
    return depth


def _collect_input() -> str | None:
    """Prompt for input, continuing across lines until braces are balanced."""
    try:
        line = input('ypool> ')
    except (KeyboardInterrupt, EOFError):
        return None

    source = line
    depth  = _brace_depth(line)

    while depth > 0:
        try:
            cont   = input('  ...> ')
            source += '\n' + cont
            depth  += _brace_depth(cont)
        except (KeyboardInterrupt, EOFError):
            print()
            return None

    return source


def _show_vars(interp: Interpreter) -> None:
    user = {
        k: v for k, v in interp.globals.vars.items()
        if not isinstance(v, _types.FunctionType)
    }
    if not user:
        print('  (nothing defined yet)')
        return
    max_len = max(len(k) for k in user)
    for name, val in sorted(user.items()):
        tag    = ' [const]' if name in interp.globals.consts else ''
        kind   = interp.ypool_str(val) if not isinstance(val, YPoolFunction) else repr(val)
        print(f'  {name:<{max_len}}{tag}  =  {kind}')


def _run_command(cmd_line: str, interp: Interpreter) -> tuple[bool, Interpreter]:
    """Handle :commands. Returns (should_exit, interp)."""
    parts = cmd_line[1:].split(None, 1)
    cmd   = parts[0].lower() if parts else ''
    arg   = parts[1].strip() if len(parts) > 1 else ''

    if cmd in ('q', 'quit', 'exit'):
        return True, interp

    if cmd == 'help':
        print("""
  :vars           list all user-defined variables and their values
  :clear          wipe the scope and start fresh
  :run <file>     load and execute a .yp file into the current scope
  :help           show this message
  :quit           exit the REPL
""".rstrip())

    elif cmd == 'vars':
        _show_vars(interp)

    elif cmd == 'clear':
        interp = Interpreter()
        print('  scope cleared.')

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
            except FileNotFoundError:
                print(f'  not found: {arg}')
            except YPoolError as e:
                print(e)
    else:
        print(f'  unknown command "{cmd}"  —  type :help')

    return False, interp


def _try_as_expr(source: str, interp: Interpreter) -> bool:
    """
    If source looks like a pure expression (not a statement), eval it
    and print the result. Returns True if we handled it this way.
    """
    first = source.strip().split()[0].upper() if source.strip() else ''
    if first in _STMT_STARTS:
        return False
    try:
        tokens = Lexer(source).tokenize()
        p      = Parser(tokens)
        expr   = p.parse_condition()
        if not p.at_end():
            return False          # leftover tokens — not a clean expression
        val = interp.eval(expr, interp.globals)
        if val is not None:
            print(f'=> {interp.ypool_str(val)}')
        return True
    except Exception:
        return False


def run_repl() -> None:
    interp = Interpreter()

    rl_note = '' if _HAS_RL else '  (install pyreadline3 for cross-session history)'
    print(f'ypool v1.0 REPL  —  :help for commands  •  Ctrl+C to quit{rl_note}')
    print()

    while True:
        source = _collect_input()
        if source is None:
            print('\ngoodbye.')
            break

        source = source.strip()
        if not source:
            continue

        # ── REPL commands ─────────────────────────────────────────────────────
        if source.startswith(':'):
            should_exit, interp = _run_command(source, interp)
            if should_exit:
                print('goodbye.')
                break
            continue

        # ── run as expression or full program ─────────────────────────────────
        try:
            if _try_as_expr(source, interp):
                continue

            tokens = Lexer(source).tokenize()
            ast    = Parser(tokens).parse()
            result = interp.run(ast)

            # Surface return value of bare CALL statements
            if result is not None:
                print(f'=> {interp.ypool_str(result)}')

        except YPoolError as e:
            print(e)
        except RecursionError:
            print('[ypool] recursion limit reached')


if __name__ == '__main__':
    run_repl()
