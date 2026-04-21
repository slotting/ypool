"""
ypool Language Server — pure-Python LSP (no pygls / lsprotocol needed)
Speaks JSON-RPC 2.0 over stdio, publishes diagnostics from the real Lexer+Parser.
"""
import sys
import json
import os
import re

# ── add ypool root to path so we can import src.* ─────────────────────────────
_here       = os.path.abspath(__file__)              # .../server/server.py
_ext_root   = os.path.dirname(os.path.dirname(_here))  # .../vscode-extension/
_ypool_root = os.path.dirname(_ext_root)             # .../ypool/
if _ypool_root not in sys.path:
    sys.path.insert(0, _ypool_root)

try:
    from src.lexer  import Lexer,  YPoolError
    from src.parser import Parser
    HAS_YPOOL = True
except Exception:
    HAS_YPOOL = False

# ── LSP transport ──────────────────────────────────────────────────────────────
def _read_message():
    headers = {}
    while True:
        raw = sys.stdin.buffer.readline()
        if not raw or raw in (b'\r\n', b'\n'):
            break
        line = raw.decode('utf-8').strip()
        if ':' in line:
            k, _, v = line.partition(':')
            headers[k.strip().lower()] = v.strip()
    length = int(headers.get('content-length', 0))
    if length == 0:
        return None
    body = sys.stdin.buffer.read(length)
    return json.loads(body.decode('utf-8'))

def _send(obj):
    body   = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    header = f'Content-Length: {len(body)}\r\n\r\n'.encode('utf-8')
    sys.stdout.buffer.write(header + body)
    sys.stdout.buffer.flush()

def _respond(req_id, result):
    _send({'jsonrpc': '2.0', 'id': req_id, 'result': result})

def _notify(method, params):
    _send({'jsonrpc': '2.0', 'method': method, 'params': params})

# ── diagnostics ────────────────────────────────────────────────────────────────
def _strip_line_tag(msg):
    return re.sub(r'^\[Line\s+\d+\]\s*', '', str(msg)).strip()

def _validate(uri, text):
    diagnostics = []
    if HAS_YPOOL and text:
        try:
            tokens = Lexer(text).tokenize()
            Parser(tokens).parse()
        except YPoolError as e:
            line = max(0, (getattr(e, 'line', None) or 1) - 1)
            lines = text.splitlines()
            end_ch = len(lines[line]) if line < len(lines) else 0
            diagnostics.append({
                'range': {
                    'start': {'line': line, 'character': 0},
                    'end':   {'line': line, 'character': end_ch},
                },
                'severity': 1,
                'source':   'ypool',
                'message':  _strip_line_tag(e),
            })
        except Exception as e:
            diagnostics.append({
                'range': {
                    'start': {'line': 0, 'character': 0},
                    'end':   {'line': 0, 'character': 0},
                },
                'severity': 1,
                'source':   'ypool',
                'message':  str(e),
            })
    _notify('textDocument/publishDiagnostics', {'uri': uri, 'diagnostics': diagnostics})

# ── hover docs ─────────────────────────────────────────────────────────────────
_HOVER_DOCS = {
    'MAKE':      '**MAKE** — Create or update a variable.\n\n`MAKE name BE value`',
    'FIX':       '**FIX** — Declare a constant (cannot be reassigned).\n\n`FIX name BE value`',
    'BE':        '**BE** — Assignment operator used with MAKE / FIX.',
    'TEACH':     '**TEACH** — Define a named function.\n\n`TEACH name USING params { ... }`',
    'ASYNC':     '**ASYNC** — Mark a function as asynchronous.\n\n`ASYNC TEACH name USING params { ... }`',
    'CALL':      '**CALL** — Invoke a function.\n\n`CALL name WITH arg1, arg2`',
    'AWAIT':     '**AWAIT** — Run a coroutine and wait for its result.\n\n`MAKE x BE AWAIT CALL fn WITH arg`',
    'GIVE':      '**GIVE** — Return a value from a function (used with BACK).\n\n`GIVE BACK value`',
    'SHOW':      '**SHOW** — Print a value to standard output.\n\n`SHOW value`',
    'ASK':       '**ASK** — Read a line of input from the user.\n\n`MAKE answer BE ASK "prompt"`',
    'FETCH':     '**FETCH** — HTTP GET request, returns body string.\n\n`MAKE data BE FETCH "https://example.com"`',
    'CHECK':     '**CHECK** — Conditional branch.\n\n`CHECK IF cond { ... } OTHERWISE { ... }`',
    'IF':        '**IF** — Used after CHECK for conditional.\n\n`CHECK IF cond { ... }`',
    'OTHERWISE': '**OTHERWISE** — Else branch of CHECK IF.\n\n`OTHERWISE { ... }`',
    'KEEP':      '**KEEP** — While loop.\n\n`KEEP GOING WHILE condition { ... }`',
    'FOR':       '**FOR** — Iterate over a collection.\n\n`FOR EACH item IN list { ... }`',
    'REPEAT':    '**REPEAT** — Loop n times.\n\n`REPEAT n TIMES { ... }`',
    'MATCH':     '**MATCH** — Pattern match a value.\n\n`MATCH value { WHEN x { } }`',
    'TRY':       '**TRY** — Begin error-handling block.\n\n`TRY { ... } CATCH err { ... }`',
    'CATCH':     '**CATCH** — Handle an error from TRY.\n\n`CATCH err { ... }`',
    'THROW':     '**THROW** — Raise a runtime error.\n\n`THROW "something went wrong"`',
    'ASSERT':    '**ASSERT** — Raise error if condition is false.\n\n`ASSERT condition`',
    'BRING':     '**BRING** — Import a ypool file.\n\n`BRING "module.yp"`',
    'BRIDGE':    '**BRIDGE** — Import a Python module.\n\n`BRIDGE "os" AS os`',
    'MAP':       '**MAP** — Transform every item in a list.\n\n`MAP list USING fn`',
    'FILTER':    '**FILTER** — Keep items where fn returns YEAH.\n\n`FILTER list WHERE fn`',
    'REDUCE':    '**REDUCE** — Fold a list to one value.\n\n`REDUCE list USING fn FROM start`',
    'LENGTH':    '**LENGTH** — Number of items or characters.\n\n`LENGTH OF expr`',
    'PUSH':      '**PUSH** — Append to a list.\n\n`PUSH val INTO list`',
    'POP':       '**POP** — Remove and return last item.\n\n`POP FROM list`',
    'RACE':      '**RACE** — Return whichever coroutine finishes first.\n\n`AWAIT RACE list_of_coros`',
    'YEAH':      '**YEAH** — Boolean true',
    'NAH':       '**NAH** — Boolean false',
    'NOTHING':   '**NOTHING** — Null / None value',
    'MEMOIZE':   '**MEMOIZE** — Cache a function\'s results.\n\n`MEMOIZE fnName`',
}

def _hover_for_word(word):
    doc = _HOVER_DOCS.get(word.upper())
    if not doc:
        return None
    return {'contents': {'kind': 'markdown', 'value': doc}}

# ── main loop ──────────────────────────────────────────────────────────────────
def main():
    while True:
        try:
            msg = _read_message()
        except Exception:
            break
        if msg is None:
            continue

        method = msg.get('method', '')
        mid    = msg.get('id')
        params = msg.get('params') or {}

        if method == 'initialize':
            _respond(mid, {
                'capabilities': {
                    'textDocumentSync': 1,    # full-document sync on every change
                    'hoverProvider':    True,
                }
            })

        elif method == 'initialized':
            pass

        elif method == 'shutdown':
            _respond(mid, None)

        elif method == 'exit':
            break

        elif method == 'textDocument/didOpen':
            td = params.get('textDocument', {})
            _validate(td.get('uri', ''), td.get('text', ''))

        elif method == 'textDocument/didChange':
            td      = params.get('textDocument', {})
            changes = params.get('contentChanges', [])
            text    = changes[-1].get('text', '') if changes else ''
            _validate(td.get('uri', ''), text)

        elif method == 'textDocument/didSave':
            td   = params.get('textDocument', {})
            text = td.get('text') or ''
            _validate(td.get('uri', ''), text)

        elif method == 'textDocument/hover':
            td     = params.get('textDocument', {})
            pos    = params.get('position', {})
            result = None
            try:
                path = td.get('uri', '').replace('file:///', '').replace('file://', '')
                if os.name == 'nt':
                    path = path.lstrip('/')
                if os.path.isfile(path):
                    lines = open(path, encoding='utf-8').readlines()
                    row   = pos.get('line', 0)
                    col   = pos.get('character', 0)
                    if row < len(lines):
                        line = lines[row]
                        s = col
                        while s > 0 and line[s-1].isalpha():
                            s -= 1
                        e = col
                        while e < len(line) and line[e].isalpha():
                            e += 1
                        result = _hover_for_word(line[s:e])
            except Exception:
                pass
            _respond(mid, result)

        elif mid is not None:
            _respond(mid, None)


if __name__ == '__main__':
    main()
