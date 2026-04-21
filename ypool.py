#!/usr/bin/env python3
"""
ypool — command-line interface

  ypool                   start the interactive REPL
  ypool script.yp         run a file
  ypool -c "SHOW 42"      run inline code
  ypool -i script.yp      run file then drop into REPL
  ypool --version         print version
"""
import sys
import argparse

# Ensure Unicode output works on Windows terminals
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

VERSION = 'ypool 1.0'


def _run_source(source: str, interp, filename='<inline>'):
    import asyncio
    from src.lexer       import Lexer, YPoolError
    from src.parser      import Parser
    try:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        asyncio.run(interp.run(ast))
    except YPoolError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(
        prog='ypool',
        description='The ypool language interpreter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  ypool                      open the REPL
  ypool hello.yp             run a file
  ypool -c "SHOW 2 PLUS 2"   run one-liner
  ypool -i hello.yp          run file then open REPL with its scope
""",
    )
    ap.add_argument('file',      nargs='?',      help='.yp file to run')
    ap.add_argument('-c',        metavar='CODE', help='run a single line of ypool code')
    ap.add_argument('-i',        action='store_true',
                                               help='inspect: drop into REPL after running file / -c')
    ap.add_argument('--version', action='version', version=VERSION)

    args = ap.parse_args()

    from src.interpreter import Interpreter
    from src.lexer       import YPoolError

    interp = Interpreter()

    if args.c:
        _run_source(args.c, interp)
        if args.i:
            from repl import run_repl
            run_repl(interp)
        return

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                source = f.read()
        except FileNotFoundError:
            print(f'ypool: no such file: {args.file}', file=sys.stderr)
            sys.exit(1)
        _run_source(source, interp, filename=args.file)
        if args.i:
            from repl import run_repl
            run_repl(interp)
        return

    # No file or -c → REPL
    from repl import run_repl
    run_repl()


if __name__ == '__main__':
    main()
