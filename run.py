import sys
from src.lexer import Lexer, YPoolError
from src.parser import Parser
from src.interpreter import Interpreter

if len(sys.argv) < 2:
    print('Usage: python run.py <file.yp>')
    sys.exit(1)

with open(sys.argv[1], 'r') as f:
    source = f.read()

try:
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
    Interpreter().run(ast)
except YPoolError as e:
    print(e)
    sys.exit(1)
