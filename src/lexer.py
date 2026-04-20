from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List


class TT(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    INTERP_STRING = auto()   # $"hello {name}"
    IDENTIFIER = auto()
    SPREAD = auto()          # ...
    # Symbols
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()
    NEWLINE = auto()
    EOF = auto()
    # Variables / IO
    MAKE = auto()
    BE = auto()
    FIX = auto()             # constant declaration
    SHOW = auto()
    ASK = auto()
    # Control flow
    CHECK = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()            # ternary else
    OTHERWISE = auto()
    KEEP = auto()
    GOING = auto()
    WHILE = auto()
    FOR = auto()
    EACH = auto()
    IN = auto()
    COUNT = auto()
    FROM = auto()
    TO = auto()
    AS = auto()
    STOP = auto()
    SKIP = auto()
    MATCH = auto()           # match / switch
    # Functions
    TEACH = auto()
    USING = auto()
    DEFAULT = auto()         # default param value
    CALL = auto()
    WITH = auto()
    GIVE = auto()
    BACK = auto()
    # Modules
    BRING = auto()           # BRING IN "file"
    # Combine
    COMBINE = auto()
    IT = auto()
    # Comparison
    IS = auto()
    NOT = auto()
    MORE = auto()
    LESS = auto()
    THAN = auto()
    AT = auto()
    LEAST = auto()
    MOST = auto()
    BETWEEN = auto()
    CONTAINS = auto()
    FITS = auto()            # str FITS "regex"
    STARTS = auto()
    ENDS = auto()
    # Logical
    ALSO = auto()
    OR = auto()
    EITHER = auto()          # null coalescing: EITHER x OR y
    # Arithmetic
    PLUS = auto()
    MINUS = auto()
    TIMES = auto()
    DIVIDED = auto()
    SLASH = auto()
    BY = auto()
    MOD = auto()
    POWER = auto()
    AND = auto()
    # Arrays / Dicts
    PUSH = auto()
    INTO = auto()
    POP = auto()
    GET = auto()
    UPDATE = auto()
    KEYS = auto()
    VALUES = auto()
    HAS = auto()
    JOIN = auto()
    SORT = auto()
    REVERSE = auto()
    REMOVE = auto()
    # String / Math builtins
    LENGTH = auto()
    OF = auto()
    UPCASE = auto()
    DOWNCASE = auto()
    FLOOR = auto()
    CEIL = auto()
    SQRT = auto()
    ABS = auto()
    SPLIT = auto()
    TRIM = auto()
    RANDOM = auto()
    KIND = auto()
    ROUND = auto()
    SLICE = auto()
    REPLACE = auto()
    FORMAT = auto()
    FIRST = auto()
    LAST = auto()
    # Array operations
    AVERAGE = auto()
    TOTAL = auto()
    FIND = auto()
    ALL = auto()
    WHERE = auto()
    MAP = auto()
    FILTER = auto()
    REDUCE = auto()
    START = auto()
    PIPE = auto()
    # Control / misc
    REPEAT = auto()
    EXISTS = auto()
    ASSERT = auto()
    # Math constants / trig
    LOG = auto()
    SIN = auto()
    COS = auto()
    TAN = auto()
    PI  = auto()
    E   = auto()
    # Dict
    MERGE = auto()
    # HTTP
    FETCH = auto()
    # Filesystem
    LIST  = auto()
    FILES = auto()
    PATH  = auto()
    # System
    ENV   = auto()
    # Typed errors
    ERROR = auto()
    # File / JSON / Date
    READ = auto()
    WRITE = auto()
    PARSE = auto()
    DUMP = auto()
    JSON = auto()
    TODAY = auto()
    NOW = auto()
    # Error handling
    TRY = auto()
    CATCH = auto()
    THROW = auto()
    # Values
    YEAH = auto()
    NAH = auto()
    NOTHING = auto()
    # Comments
    NOTE = auto()


KEYWORDS = {
    'MAKE': TT.MAKE, 'BE': TT.BE, 'FIX': TT.FIX,
    'SHOW': TT.SHOW, 'ASK': TT.ASK,
    'CHECK': TT.CHECK, 'IF': TT.IF, 'THEN': TT.THEN, 'ELSE': TT.ELSE,
    'OTHERWISE': TT.OTHERWISE,
    'KEEP': TT.KEEP, 'GOING': TT.GOING, 'WHILE': TT.WHILE,
    'FOR': TT.FOR, 'EACH': TT.EACH, 'IN': TT.IN,
    'COUNT': TT.COUNT, 'FROM': TT.FROM, 'TO': TT.TO, 'AS': TT.AS,
    'STOP': TT.STOP, 'SKIP': TT.SKIP, 'MATCH': TT.MATCH,
    'TEACH': TT.TEACH, 'USING': TT.USING, 'DEFAULT': TT.DEFAULT,
    'CALL': TT.CALL, 'WITH': TT.WITH,
    'GIVE': TT.GIVE, 'BACK': TT.BACK,
    'BRING': TT.BRING,
    'COMBINE': TT.COMBINE, 'IT': TT.IT,
    'IS': TT.IS, 'NOT': TT.NOT, 'MORE': TT.MORE, 'LESS': TT.LESS,
    'THAN': TT.THAN, 'AT': TT.AT, 'LEAST': TT.LEAST, 'MOST': TT.MOST,
    'BETWEEN': TT.BETWEEN, 'CONTAINS': TT.CONTAINS,
    'FITS': TT.FITS, 'STARTS': TT.STARTS, 'ENDS': TT.ENDS,
    'ALSO': TT.ALSO, 'OR': TT.OR, 'EITHER': TT.EITHER,
    'PLUS': TT.PLUS, 'MINUS': TT.MINUS, 'TIMES': TT.TIMES,
    'DIVIDED': TT.DIVIDED, 'BY': TT.BY, 'MOD': TT.MOD,
    'POWER': TT.POWER, 'AND': TT.AND,
    'PUSH': TT.PUSH, 'INTO': TT.INTO, 'POP': TT.POP,
    'GET': TT.GET, 'UPDATE': TT.UPDATE,
    'KEYS': TT.KEYS, 'VALUES': TT.VALUES, 'HAS': TT.HAS,
    'JOIN': TT.JOIN, 'SORT': TT.SORT, 'REVERSE': TT.REVERSE,
    'REMOVE': TT.REMOVE,
    'LENGTH': TT.LENGTH, 'OF': TT.OF,
    'UPCASE': TT.UPCASE, 'DOWNCASE': TT.DOWNCASE,
    'FLOOR': TT.FLOOR, 'CEIL': TT.CEIL,
    'SQRT': TT.SQRT, 'ABS': TT.ABS, 'ROUND': TT.ROUND,
    'SPLIT': TT.SPLIT, 'TRIM': TT.TRIM,
    'RANDOM': TT.RANDOM, 'KIND': TT.KIND,
    'SLICE': TT.SLICE, 'REPLACE': TT.REPLACE,
    'FORMAT': TT.FORMAT, 'FIRST': TT.FIRST, 'LAST': TT.LAST,
    'AVERAGE': TT.AVERAGE, 'TOTAL': TT.TOTAL,
    'FIND': TT.FIND, 'ALL': TT.ALL, 'WHERE': TT.WHERE,
    'MAP': TT.MAP, 'FILTER': TT.FILTER, 'REDUCE': TT.REDUCE,
    'START': TT.START, 'PIPE': TT.PIPE,
    'REPEAT': TT.REPEAT, 'EXISTS': TT.EXISTS, 'ASSERT': TT.ASSERT,
    'LOG': TT.LOG, 'SIN': TT.SIN, 'COS': TT.COS, 'TAN': TT.TAN,
    'PI': TT.PI, 'E': TT.E,
    'MERGE': TT.MERGE, 'FETCH': TT.FETCH,
    'LIST': TT.LIST, 'FILES': TT.FILES, 'PATH': TT.PATH,
    'ENV': TT.ENV, 'ERROR': TT.ERROR,
    'READ': TT.READ, 'WRITE': TT.WRITE,
    'PARSE': TT.PARSE, 'DUMP': TT.DUMP, 'JSON': TT.JSON,
    'TODAY': TT.TODAY, 'NOW': TT.NOW,
    'TRY': TT.TRY, 'CATCH': TT.CATCH, 'THROW': TT.THROW,
    'YEAH': TT.YEAH, 'NAH': TT.NAH, 'NOTHING': TT.NOTHING,
    'NOTE': TT.NOTE,
}


class YPoolError(Exception):
    def __init__(self, msg, line=None):
        self.line = line
        super().__init__(f'[ypool line {line}] {msg}' if line else f'[ypool] {msg}')


@dataclass
class Token:
    type: TT
    value: Any
    line: int


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1

    def current(self):
        return self.source[self.pos] if self.pos < len(self.source) else '\0'

    def peek(self, offset=1):
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else '\0'

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def skip_whitespace(self):
        while self.current() in ' \t\r':
            self.advance()

    def read_number(self):
        start_line = self.line
        num = ''
        while self.current().isdigit() or self.current() == '.':
            num += self.advance()
        if num.count('.') > 1:
            raise YPoolError(f'Invalid number: {num}', start_line)
        val = float(num) if '.' in num else int(num)
        return Token(TT.NUMBER, val, start_line)

    def read_string(self, quote, interp=False):
        start_line = self.line
        self.advance()  # opening quote
        s = ''
        while self.pos < len(self.source) and self.current() != quote:
            if self.current() == '\\':
                self.advance()
                esc = self.advance()
                s += {'n': '\n', 't': '\t', '\\': '\\', '"': '"', "'": "'"}.get(esc, '\\' + esc)
            else:
                s += self.advance()
        if self.pos >= len(self.source):
            raise YPoolError('Unterminated string', start_line)
        self.advance()  # closing quote
        tt = TT.INTERP_STRING if interp else TT.STRING
        return Token(tt, s, start_line)

    def read_word(self):
        start_line = self.line
        word = ''
        while self.current().isalnum() or self.current() == '_':
            word += self.advance()
        if word.replace('_', '').isupper() and word.replace('_', ''):
            tt = KEYWORDS.get(word)
            if tt:
                return Token(tt, word, start_line)
        return Token(TT.IDENTIFIER, word, start_line)

    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < len(self.source):
            self.skip_whitespace()
            if self.pos >= len(self.source):
                break

            ch = self.current()

            if ch == '\n':
                tokens.append(Token(TT.NEWLINE, '\n', self.line))
                self.advance()
                continue

            # Interpolated string:  $"hello {name}"
            if ch == '$' and self.peek() in ('"', "'"):
                self.advance()  # skip $
                tokens.append(self.read_string(self.current(), interp=True))
                continue

            if ch.isdigit():
                tokens.append(self.read_number())
                continue

            if ch in ('"', "'"):
                tokens.append(self.read_string(ch))
                continue

            # Spread operator: ...
            if ch == '.' and self.peek() == '.' and self.peek(2) == '.':
                self.advance(); self.advance(); self.advance()
                tokens.append(Token(TT.SPREAD, '...', self.line))
                continue

            if ch.isalpha() or ch == '_':
                tok = self.read_word()
                if tok.type == TT.NOTE:
                    while self.pos < len(self.source) and self.current() != '\n':
                        self.advance()
                    continue
                tokens.append(tok)
                continue

            sym = {
                '{': TT.LBRACE, '}': TT.RBRACE,
                '(': TT.LPAREN, ')': TT.RPAREN,
                '[': TT.LBRACKET, ']': TT.RBRACKET,
                ',': TT.COMMA,  ':': TT.COLON,
                '+': TT.PLUS,   '-': TT.MINUS,
                '*': TT.TIMES,  '/': TT.SLASH,
                '%': TT.MOD,
            }
            if ch in sym:
                tokens.append(Token(sym[ch], ch, self.line))
                self.advance()
                continue

            raise YPoolError(f'Unknown character "{ch}"', self.line)

        tokens.append(Token(TT.EOF, None, self.line))
        return tokens
