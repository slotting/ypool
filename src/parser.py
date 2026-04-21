from typing import List, Optional
from .lexer import TT, Token, YPoolError


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TT.NEWLINE]
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset=1) -> Token:
        p = self.pos + offset
        return self.tokens[p] if p < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return t

    def expect(self, *types) -> Token:
        if self.current().type not in types:
            names = ' or '.join(t.name for t in types)
            raise YPoolError(
                f'Expected {names} but got "{self.current().value}"',
                self.current().line
            )
        return self.advance()

    def match(self, *types) -> Optional[Token]:
        if self.current().type in types:
            return self.advance()
        return None

    def at_end(self) -> bool:
        return self.current().type == TT.EOF

    # ── entry ──────────────────────────────────────────────────────────────────

    def parse(self) -> dict:
        body = []
        while not self.at_end():
            body.append(self.parse_statement())
        return {'type': 'Program', 'body': body}

    # ── statements ─────────────────────────────────────────────────────────────

    def parse_statement(self) -> dict:
        t = self.current().type
        if t == TT.MAKE:    return self.parse_make()
        if t == TT.FIX:     return self.parse_fix()
        if t == TT.SHOW:    return self.parse_show()
        if t == TT.CHECK:   return self.parse_check()
        if t == TT.MATCH:   return self.parse_match()
        if t == TT.KEEP:    return self.parse_keep()
        if t == TT.FOR:     return self.parse_for_each()
        if t == TT.COUNT:   return self.parse_count()
        if t == TT.TEACH:   return self.parse_teach()
        if t == TT.CALL:    return {'type': 'CallStmt', 'call': self.parse_call_expr()}
        if t == TT.GIVE:    return self.parse_give()
        if t == TT.COMBINE: return self.parse_combine()
        if t == TT.PUSH:    return self.parse_push()
        if t == TT.POP:     return self.parse_pop()
        if t == TT.UPDATE:  return self.parse_update()
        if t == TT.REMOVE:  return self.parse_remove()
        if t == TT.SORT:    return self.parse_sort()
        if t == TT.REVERSE: return self.parse_reverse_stmt()
        if t == TT.STOP:    self.advance(); return {'type': 'Stop'}
        if t == TT.SKIP:    self.advance(); return {'type': 'Skip'}
        if t == TT.TRY:     return self.parse_try()
        if t == TT.THROW:   return self.parse_throw()
        if t == TT.WRITE:   return self.parse_write()
        if t == TT.BRING:   return self.parse_bring()
        if t == TT.REPEAT:  return self.parse_repeat()
        if t == TT.ASSERT:  return self.parse_assert()
        if t == TT.FETCH:   return {'type': 'CallStmt', 'call': self._parse_fetch_expr()}
        if t == TT.LIST:    return {'type': 'CallStmt', 'call': self._parse_list_files()}
        if t == TT.MEMOIZE: return self.parse_memoize()
        if t == TT.BRIDGE:  return self.parse_bridge()
        raise YPoolError(
            f'Unknown statement "{self.current().value}"',
            self.current().line
        )

    def parse_make(self) -> dict:
        line = self.current().line
        self.advance()  # MAKE

        # Array destructure: MAKE [a, b, c] FROM expr
        if self.current().type == TT.LBRACKET:
            self.advance()
            names = []
            while self.current().type != TT.RBRACKET and not self.at_end():
                names.append(self.expect(TT.IDENTIFIER).value)
                self.match(TT.COMMA)
            self.expect(TT.RBRACKET)
            self.expect(TT.FROM)
            source = self.parse_condition()
            return {'type': 'DestructureArray', 'names': names, 'source': source, 'line': line}

        # Dict destructure: MAKE {name, age} FROM expr
        if self.current().type == TT.LBRACE:
            self.advance()
            keys = []
            while self.current().type != TT.RBRACE and not self.at_end():
                keys.append(self.expect(TT.IDENTIFIER).value)
                self.match(TT.COMMA)
            self.expect(TT.RBRACE)
            self.expect(TT.FROM)
            source = self.parse_condition()
            return {'type': 'DestructureDict', 'keys': keys, 'source': source, 'line': line}

        name = self.expect(TT.IDENTIFIER).value

        # MAKE arr AT index BE value
        if self.current().type == TT.AT:
            self.advance()
            index = self.parse_expr()
            self.expect(TT.BE)
            value = self.parse_condition()
            return {'type': 'UpdateIndex', 'name': name, 'index': index, 'value': value}

        # MAKE dict key BE value  (two identifiers before BE)
        if self.current().type == TT.IDENTIFIER and self.peek().type == TT.BE:
            key = self.advance().value
            self.expect(TT.BE)
            value = self.parse_condition()
            return {'type': 'UpdateKey', 'name': name, 'key': key, 'value': value}

        self.expect(TT.BE)
        value = self.parse_condition()
        return {'type': 'Make', 'name': name, 'value': value, 'line': line}

    def parse_fix(self) -> dict:
        line = self.current().line
        self.advance()  # FIX
        name = self.expect(TT.IDENTIFIER).value
        self.expect(TT.BE)
        value = self.parse_condition()
        return {'type': 'Fix', 'name': name, 'value': value, 'line': line}

    def parse_show(self) -> dict:
        self.advance()
        return {'type': 'Show', 'value': self.parse_condition()}

    def parse_check(self) -> dict:
        self.advance()  # CHECK
        self.expect(TT.IF)
        condition = self.parse_condition()
        then = self.parse_block()
        otherwise = None
        if self.match(TT.OTHERWISE):
            otherwise = self.parse_block()
        return {'type': 'Check', 'condition': condition, 'then': then, 'otherwise': otherwise}

    def parse_match(self) -> dict:
        self.advance()  # MATCH
        subject = self.parse_expr()
        self.expect(TT.LBRACE)
        cases = []
        default_body = None
        while self.current().type != TT.RBRACE and not self.at_end():
            if self.current().type == TT.OTHERWISE:
                self.advance()
                default_body = self.parse_block()
            else:
                self.expect(TT.IS)
                case = self._parse_match_case()
                case['body'] = self.parse_block()
                cases.append(case)
        self.expect(TT.RBRACE)
        return {'type': 'Match', 'subject': subject, 'cases': cases, 'default': default_body}

    def _parse_match_case(self) -> dict:
        if self.current().type == TT.MORE:
            self.advance(); self.expect(TT.THAN)
            return {'op': '>', 'value': self.parse_expr()}
        if self.current().type == TT.LESS:
            self.advance(); self.expect(TT.THAN)
            return {'op': '<', 'value': self.parse_expr()}
        if self.current().type == TT.AT and self.peek().type == TT.LEAST:
            self.advance(); self.advance()
            return {'op': '>=', 'value': self.parse_expr()}
        if self.current().type == TT.AT and self.peek().type == TT.MOST:
            self.advance(); self.advance()
            return {'op': '<=', 'value': self.parse_expr()}
        if self.current().type == TT.NOT:
            self.advance()
            return {'op': '!=', 'value': self.parse_expr()}
        if self.current().type == TT.BETWEEN:
            self.advance()
            low = self.parse_term()
            self.expect(TT.AND)
            high = self.parse_term()
            return {'op': 'between', 'low': low, 'high': high}
        return {'op': '==', 'value': self.parse_expr()}

    def parse_keep(self) -> dict:
        self.advance()
        self.expect(TT.GOING)
        self.expect(TT.WHILE)
        condition = self.parse_condition()
        body = self.parse_block()
        return {'type': 'Keep', 'condition': condition, 'body': body}

    def parse_for_each(self) -> dict:
        self.advance()
        self.expect(TT.EACH)
        var = self.expect(TT.IDENTIFIER).value
        self.expect(TT.IN)
        iterable = self.parse_expr()
        body = self.parse_block()
        return {'type': 'ForEach', 'var': var, 'iterable': iterable, 'body': body}

    def parse_count(self) -> dict:
        self.advance()
        self.expect(TT.FROM)
        start = self.parse_expr()
        self.expect(TT.TO)
        end = self.parse_expr()
        var = None
        if self.match(TT.AS):
            var = self.expect(TT.IDENTIFIER).value
        body = self.parse_block()
        return {'type': 'Count', 'start': start, 'end': end, 'var': var, 'body': body}

    def parse_teach(self) -> dict:
        self.advance()  # TEACH
        name = self.expect(TT.IDENTIFIER).value
        params = []    # list of (param_name, default_node_or_None)
        variadic = None
        if self.match(TT.USING):
            while True:
                # Variadic: ...rest
                if self.current().type == TT.SPREAD:
                    self.advance()
                    variadic = self.expect(TT.IDENTIFIER).value
                    self.match(TT.COMMA)
                    break
                pname = self.expect(TT.IDENTIFIER).value
                default = None
                if self.match(TT.DEFAULT):
                    default = self.parse_unary()
                params.append((pname, default))
                if not self.match(TT.COMMA):
                    break
        body = self.parse_block()
        return {'type': 'Teach', 'name': name, 'params': params, 'variadic': variadic, 'body': body}

    def parse_give(self) -> dict:
        self.advance()
        self.expect(TT.BACK)
        values = [self.parse_condition()]
        while self.match(TT.COMMA):
            values.append(self.parse_condition())
        if len(values) == 1:
            return {'type': 'Give', 'value': values[0]}
        return {'type': 'Give', 'value': {'type': 'ArrayLiteral', 'items': values}}

    def parse_repeat(self) -> dict:
        self.advance()  # REPEAT
        count = self.parse_expr()
        var = None
        if self.match(TT.AS):
            var = self.expect(TT.IDENTIFIER).value
        body = self.parse_block()
        return {'type': 'Repeat', 'count': count, 'var': var, 'body': body}

    def parse_combine(self) -> dict:
        self.advance()
        left = self.parse_term()
        self.expect(TT.AND)
        right = self.parse_concat()
        self.expect(TT.THEN)
        if self.current().type == TT.SHOW:
            self.advance(); self.expect(TT.IT)
            return {'type': 'Combine', 'left': left, 'right': right, 'action': 'show', 'name': None}
        if self.current().type == TT.KEEP:
            self.advance(); self.expect(TT.IT); self.expect(TT.AS)
            name = self.expect(TT.IDENTIFIER).value
            return {'type': 'Combine', 'left': left, 'right': right, 'action': 'keep', 'name': name}
        raise YPoolError('Expected SHOW IT or KEEP IT AS after THEN', self.current().line)

    def parse_push(self) -> dict:
        self.advance()
        value = self.parse_condition()
        self.expect(TT.INTO)
        name = self.expect(TT.IDENTIFIER).value
        return {'type': 'Push', 'value': value, 'name': name}

    def parse_pop(self) -> dict:
        self.advance()
        self.expect(TT.FROM)
        name = self.expect(TT.IDENTIFIER).value
        return {'type': 'Pop', 'name': name}

    def parse_update(self) -> dict:
        self.advance()
        name = self.expect(TT.IDENTIFIER).value
        if self.current().type == TT.AT:
            self.advance()
            index = self.parse_expr()
            self.expect(TT.TO)
            value = self.parse_condition()
            return {'type': 'UpdateIndex', 'name': name, 'index': index, 'value': value}
        key = self.expect(TT.IDENTIFIER).value
        self.expect(TT.TO)
        value = self.parse_condition()
        return {'type': 'UpdateKey', 'name': name, 'key': key, 'value': value}

    def parse_remove(self) -> dict:
        self.advance()
        name = self.expect(TT.IDENTIFIER).value
        self.expect(TT.AT)
        index = self.parse_expr()
        return {'type': 'RemoveAt', 'name': name, 'index': index}

    def parse_sort(self) -> dict:
        self.advance()
        name = self.expect(TT.IDENTIFIER).value
        field = None
        if self.match(TT.BY):
            field = self.parse_primary()
        return {'type': 'SortArr', 'name': name, 'field': field}

    def parse_reverse_stmt(self) -> dict:
        self.advance()
        name = self.expect(TT.IDENTIFIER).value
        return {'type': 'ReverseArr', 'name': name}

    def parse_try(self) -> dict:
        self.advance()  # TRY
        body = self.parse_block()
        catches = []
        while self.current().type == TT.CATCH:
            self.advance()  # CATCH
            if self.current().type == TT.STRING:
                err_type = self.advance().value
                err_var  = self.expect(TT.IDENTIFIER).value
            else:
                err_type = None
                err_var  = self.expect(TT.IDENTIFIER).value
            handler = self.parse_block()
            catches.append({'err_type': err_type, 'err_var': err_var, 'body': handler})
            if err_type is None:
                break  # catch-all must be last
        if not catches:
            raise YPoolError('TRY requires at least one CATCH', self.current().line)
        return {'type': 'Try', 'body': body, 'catches': catches}

    def parse_throw(self) -> dict:
        self.advance()
        return {'type': 'Throw', 'value': self.parse_condition()}

    def parse_write(self) -> dict:
        self.advance()
        path = self.parse_primary()
        self.expect(TT.WITH)
        content = self.parse_condition()
        return {'type': 'WriteFile', 'path': path, 'content': content}

    def parse_bring(self) -> dict:
        self.advance()  # BRING
        self.expect(TT.IN)
        path = self.parse_primary()
        namespace = None
        if self.match(TT.AS):
            namespace = self.expect(TT.IDENTIFIER).value
        return {'type': 'BringIn', 'path': path, 'namespace': namespace}

    def parse_memoize(self) -> dict:
        self.advance()  # MEMOIZE
        name = self.expect(TT.IDENTIFIER).value
        self.expect(TT.AS)
        alias = self.expect(TT.IDENTIFIER).value
        return {'type': 'Memoize', 'name': name, 'alias': alias}

    def parse_bridge(self) -> dict:
        self.advance()  # BRIDGE
        module = self.parse_primary()
        self.expect(TT.AS)
        alias = self.expect(TT.IDENTIFIER).value
        return {'type': 'Bridge', 'module': module, 'alias': alias}

    def parse_assert(self) -> dict:
        line = self.current().line
        self.advance()  # ASSERT
        condition = self.parse_condition()
        self.expect(TT.ELSE)
        message = self.parse_primary()
        return {'type': 'Assert', 'condition': condition, 'message': message, 'line': line}

    # ── block ──────────────────────────────────────────────────────────────────

    def parse_block(self) -> list:
        self.expect(TT.LBRACE)
        stmts = []
        while self.current().type != TT.RBRACE and not self.at_end():
            stmts.append(self.parse_statement())
        self.expect(TT.RBRACE)
        return stmts

    # ── conditions ─────────────────────────────────────────────────────────────

    def parse_condition(self) -> dict:
        return self.parse_pipe()

    def parse_pipe(self) -> dict:
        left = self.parse_or()
        while self.current().type == TT.PIPE:
            self.advance()
            left = self._parse_pipe_rhs(left)
        return left

    def _parse_pipe_rhs(self, collection: dict) -> dict:
        t = self.current().type
        if t == TT.MAP:
            self.advance(); self.expect(TT.USING)
            fn = self.parse_primary()
            return {'type': 'Builtin', 'op': 'map', 'args': [collection, fn]}
        if t == TT.FILTER:
            self.advance(); self.expect(TT.WHERE)
            fn = self.parse_primary()
            return {'type': 'Builtin', 'op': 'filter', 'args': [collection, fn]}
        if t == TT.REDUCE:
            self.advance(); self.expect(TT.USING)
            fn = self.parse_primary()
            self.expect(TT.START)
            init = self.parse_primary()
            return {'type': 'Builtin', 'op': 'reduce', 'args': [collection, fn, init]}
        if t == TT.UNIQUE:
            self.advance()
            return {'type': 'Builtin', 'op': 'unique', 'args': [collection]}
        if t == TT.FLATTEN:
            self.advance()
            return {'type': 'Builtin', 'op': 'flatten', 'args': [collection]}
        if t == TT.TALLY:
            self.advance()
            return {'type': 'Builtin', 'op': 'tally', 'args': [collection]}
        if t == TT.GROUP:
            self.advance(); self.expect(TT.BY)
            fn = self.parse_primary()
            return {'type': 'Builtin', 'op': 'group_by', 'args': [collection, fn]}
        raise YPoolError(f'Expected MAP, FILTER, REDUCE, UNIQUE, FLATTEN, TALLY, or GROUP after PIPE', self.current().line)

    def parse_or(self) -> dict:
        left = self.parse_and()
        while self.match(TT.OR):
            right = self.parse_and()
            left = {'type': 'BinOp', 'op': 'or', 'left': left, 'right': right}
        return left

    def parse_and(self) -> dict:
        left = self.parse_not()
        while self.match(TT.ALSO):
            right = self.parse_not()
            left = {'type': 'BinOp', 'op': 'and', 'left': left, 'right': right}
        return left

    def parse_not(self) -> dict:
        if self.match(TT.NOT):
            return {'type': 'UnaryOp', 'op': 'not', 'operand': self.parse_not()}
        return self.parse_comparison()

    def parse_comparison(self) -> dict:
        left = self.parse_concat()

        if self.current().type == TT.CONTAINS:
            self.advance()
            return {'type': 'Contains', 'left': left, 'right': self.parse_concat()}

        if self.current().type == TT.FITS:
            self.advance()
            return {'type': 'Builtin', 'op': 'fits', 'args': [left, self.parse_concat()]}

        if self.current().type == TT.STARTS:
            self.advance(); self.expect(TT.WITH)
            return {'type': 'Builtin', 'op': 'starts_with', 'args': [left, self.parse_concat()]}

        if self.current().type == TT.ENDS:
            self.advance(); self.expect(TT.WITH)
            return {'type': 'Builtin', 'op': 'ends_with', 'args': [left, self.parse_concat()]}

        if self.current().type != TT.IS:
            return left

        self.advance()  # IS

        if self.match(TT.NOTHING):
            return {'type': 'BinOp', 'op': '==', 'left': left, 'right': {'type': 'Nothing'}}

        if self.current().type == TT.NOT and self.peek().type == TT.NOTHING:
            self.advance(); self.advance()
            return {'type': 'BinOp', 'op': '!=', 'left': left, 'right': {'type': 'Nothing'}}

        if self.match(TT.NOT):
            return {'type': 'BinOp', 'op': '!=', 'left': left, 'right': self.parse_concat()}

        if self.current().type == TT.MORE:
            self.advance(); self.expect(TT.THAN)
            return {'type': 'BinOp', 'op': '>', 'left': left, 'right': self.parse_concat()}

        if self.current().type == TT.LESS:
            self.advance(); self.expect(TT.THAN)
            return {'type': 'BinOp', 'op': '<', 'left': left, 'right': self.parse_concat()}

        if self.current().type == TT.AT and self.peek().type == TT.LEAST:
            self.advance(); self.advance()
            return {'type': 'BinOp', 'op': '>=', 'left': left, 'right': self.parse_concat()}

        if self.current().type == TT.AT and self.peek().type == TT.MOST:
            self.advance(); self.advance()
            return {'type': 'BinOp', 'op': '<=', 'left': left, 'right': self.parse_concat()}

        if self.current().type == TT.BETWEEN:
            self.advance()
            low = self.parse_term()
            self.expect(TT.AND)
            high = self.parse_term()
            return {'type': 'Between', 'value': left, 'low': low, 'high': high}

        return {'type': 'BinOp', 'op': '==', 'left': left, 'right': self.parse_concat()}

    # ── expressions ────────────────────────────────────────────────────────────

    def parse_concat(self) -> dict:
        """String/list concatenation with AND — lower precedence than + and -."""
        left = self.parse_expr()
        while self.current().type == TT.AND:
            self.advance()
            right = self.parse_expr()
            left = {'type': 'BinOp', 'op': 'AND', 'left': left, 'right': right}
        return left

    def parse_expr(self) -> dict:
        left = self.parse_term()
        while self.current().type in (TT.PLUS, TT.MINUS):
            op = {TT.PLUS: '+', TT.MINUS: '-'}[self.advance().type]
            right = self.parse_term()
            left = {'type': 'BinOp', 'op': op, 'left': left, 'right': right}
        return left

    def parse_term(self) -> dict:
        left = self.parse_power()
        while self.current().type in (TT.TIMES, TT.DIVIDED, TT.SLASH, TT.MOD):
            t = self.current().type
            self.advance()
            if t == TT.DIVIDED:
                self.expect(TT.BY); op = '/'
            elif t == TT.SLASH:
                op = '/'
            elif t == TT.MOD:
                op = '%'
            else:
                op = '*'
            right = self.parse_power()
            left = {'type': 'BinOp', 'op': op, 'left': left, 'right': right}
        return left

    def parse_power(self) -> dict:
        base = self.parse_unary()
        if self.match(TT.POWER):
            return {'type': 'BinOp', 'op': '**', 'left': base, 'right': self.parse_power()}
        return base

    def parse_unary(self) -> dict:
        if self.match(TT.MINUS):
            return {'type': 'UnaryOp', 'op': '-', 'operand': self.parse_unary()}
        return self.parse_postfix()

    def parse_postfix(self) -> dict:
        expr = self.parse_primary()
        while True:
            if self.current().type == TT.EXISTS:
                self.advance()
                if expr['type'] != 'Identifier':
                    raise YPoolError('EXISTS requires an identifier', self.current().line)
                return {'type': 'Exists', 'name': expr['name']}
            elif self.current().type == TT.AT:
                self.advance()
                expr = {'type': 'Index', 'obj': expr, 'index': self.parse_primary()}
            elif self.current().type == TT.GET:
                self.advance()
                key = self.expect(TT.IDENTIFIER).value
                if self.match(TT.ELSE):
                    fallback = self.parse_primary()
                    expr = {'type': 'SafeGet', 'obj': expr, 'key': key, 'fallback': fallback}
                else:
                    expr = {'type': 'DictGet', 'obj': expr, 'key': key}
            else:
                break
        return expr

    def parse_primary(self) -> dict:
        t = self.current()

        # Unary minus at primary level (for builtin args like ABS OF -5)
        if t.type == TT.MINUS:
            self.advance()
            return {'type': 'UnaryOp', 'op': '-', 'operand': self.parse_primary()}

        if t.type == TT.NUMBER:      self.advance(); return {'type': 'Number',      'value': t.value}
        if t.type == TT.STRING:      self.advance(); return {'type': 'String',      'value': t.value}
        if t.type == TT.INTERP_STRING: self.advance(); return {'type': 'InterpString', 'value': t.value}
        if t.type == TT.YEAH:        self.advance(); return {'type': 'Bool',        'value': True}
        if t.type == TT.NAH:         self.advance(); return {'type': 'Bool',        'value': False}
        if t.type == TT.NOTHING:     self.advance(); return {'type': 'Nothing'}
        if t.type == TT.IDENTIFIER:  self.advance(); return {'type': 'Identifier',  'name': t.value}

        if t.type == TT.CALL:        return self.parse_call_expr()
        if t.type == TT.ASK:         return self.parse_ask()

        # Ternary:  IF cond THEN val ELSE other
        if t.type == TT.IF:
            self.advance()
            cond = self.parse_condition()
            self.expect(TT.THEN)
            then_val = self.parse_expr()
            self.expect(TT.ELSE)
            else_val = self.parse_expr()
            return {'type': 'Ternary', 'condition': cond, 'then': then_val, 'else': else_val}

        # Null coalescing:  EITHER x OR y
        if t.type == TT.EITHER:
            self.advance()
            left = self.parse_expr()
            self.expect(TT.OR)
            right = self.parse_expr()
            return {'type': 'NullCoalesce', 'left': left, 'right': right}

        # Array literal with optional spread: [1, ...arr, 2]
        if t.type == TT.LBRACKET:
            return self.parse_array_literal()

        # Dict literal
        if t.type == TT.LBRACE:
            return self.parse_dict_literal()

        # Grouped
        if t.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TT.RPAREN)
            return expr

        # ── builtins ──────────────────────────────────────────────────────────

        if t.type == TT.LENGTH:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'length', 'args': [self.parse_primary()]}

        if t.type == TT.UPCASE:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'upcase', 'args': [self.parse_primary()]}

        if t.type == TT.DOWNCASE:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'downcase', 'args': [self.parse_primary()]}

        if t.type == TT.TRIM:
            self.advance()
            return {'type': 'Builtin', 'op': 'trim', 'args': [self.parse_primary()]}

        if t.type == TT.SPLIT:
            self.advance()
            s = self.parse_primary()
            self.expect(TT.BY)
            sep = self.parse_primary()
            return {'type': 'Builtin', 'op': 'split', 'args': [s, sep]}

        if t.type == TT.JOIN:
            self.advance()
            arr = self.parse_primary()
            self.expect(TT.BY)
            sep = self.parse_primary()
            return {'type': 'Builtin', 'op': 'join', 'args': [arr, sep]}

        if t.type in (TT.FLOOR, TT.CEIL, TT.SQRT, TT.ABS, TT.ROUND):
            op = t.type.name.lower(); self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': op, 'args': [self.parse_primary()]}

        if t.type == TT.KIND:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'kind', 'args': [self.parse_primary()]}

        if t.type == TT.KEYS:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'keys', 'args': [self.parse_primary()]}

        if t.type == TT.VALUES:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'values', 'args': [self.parse_primary()]}

        if t.type == TT.HAS:
            self.advance()
            obj = self.parse_primary()
            key = self.parse_primary()
            return {'type': 'Builtin', 'op': 'has', 'args': [obj, key]}

        if t.type == TT.RANDOM:
            self.advance()
            if self.current().type == TT.FROM:
                self.advance()
                start = self.parse_expr()
                self.expect(TT.TO)
                end = self.parse_expr()
                return {'type': 'Builtin', 'op': 'random_range', 'args': [start, end]}
            return {'type': 'Builtin', 'op': 'random', 'args': []}

        if t.type == TT.FIRST:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'first', 'args': [self.parse_primary()]}

        if t.type == TT.LAST:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'last', 'args': [self.parse_primary()]}

        if t.type == TT.AVERAGE:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'average', 'args': [self.parse_primary()]}

        if t.type == TT.TOTAL:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'total', 'args': [self.parse_primary()]}

        if t.type == TT.FIND:
            self.advance()
            all_mode = bool(self.match(TT.ALL))
            self.expect(TT.IN)
            arr = self.parse_primary()
            self.expect(TT.WHERE)
            func = self.parse_primary()
            return {'type': 'Builtin', 'op': 'find_all' if all_mode else 'find', 'args': [arr, func]}

        if t.type == TT.SLICE:
            self.advance()
            s = self.parse_primary()
            self.expect(TT.FROM)
            start = self.parse_expr()
            self.expect(TT.TO)
            end = self.parse_expr()
            return {'type': 'Builtin', 'op': 'slice', 'args': [s, start, end]}

        if t.type == TT.REPLACE:
            self.advance(); self.expect(TT.IN)
            s = self.parse_primary()
            self.expect(TT.FROM)
            old = self.parse_primary()
            self.expect(TT.TO)
            new = self.parse_primary()
            return {'type': 'Builtin', 'op': 'replace', 'args': [s, old, new]}

        if t.type == TT.FORMAT:
            self.advance()
            num = self.parse_primary()
            self.expect(TT.TO)
            digits = self.parse_primary()
            return {'type': 'Builtin', 'op': 'format_num', 'args': [num, digits]}

        if t.type == TT.READ:
            self.advance()
            return {'type': 'Builtin', 'op': 'read_file', 'args': [self.parse_primary()]}

        if t.type == TT.PARSE:
            self.advance(); self.expect(TT.JSON)
            return {'type': 'Builtin', 'op': 'parse_json', 'args': [self.parse_primary()]}

        if t.type == TT.DUMP:
            self.advance(); self.expect(TT.JSON)
            return {'type': 'Builtin', 'op': 'dump_json', 'args': [self.parse_primary()]}

        if t.type == TT.TODAY:
            self.advance(); return {'type': 'Builtin', 'op': 'today', 'args': []}

        if t.type == TT.NOW:
            self.advance(); return {'type': 'Builtin', 'op': 'now', 'args': []}

        # ── math ──────────────────────────────────────────────────────────────
        if t.type in (TT.LOG, TT.SIN, TT.COS, TT.TAN):
            op = t.type.name.lower(); self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': op, 'args': [self.parse_primary()]}

        if t.type == TT.PI:
            self.advance(); return {'type': 'Builtin', 'op': 'pi', 'args': []}

        if t.type == TT.E:
            self.advance(); return {'type': 'Builtin', 'op': 'e_const', 'args': []}

        # ── MERGE ─────────────────────────────────────────────────────────────
        if t.type == TT.MERGE:
            self.advance()
            left = self.parse_primary()
            self.expect(TT.WITH)
            right = self.parse_primary()
            return {'type': 'Builtin', 'op': 'merge', 'args': [left, right]}

        # ── FETCH ─────────────────────────────────────────────────────────────
        if t.type == TT.FETCH:
            return self._parse_fetch_expr()

        # ── filesystem ────────────────────────────────────────────────────────
        if t.type == TT.LIST:
            return self._parse_list_files()

        if t.type == TT.PATH:
            self.advance(); self.expect(TT.EXISTS)
            return {'type': 'Builtin', 'op': 'path_exists', 'args': [self.parse_primary()]}

        # ── ENV ───────────────────────────────────────────────────────────────
        if t.type == TT.ENV:
            self.advance()
            return {'type': 'Builtin', 'op': 'env_var', 'args': [self.parse_primary()]}

        # ── ERROR ─────────────────────────────────────────────────────────────
        if t.type == TT.ERROR:
            self.advance()
            err_type = self.parse_primary()
            self.expect(TT.WITH)
            err_msg = self.parse_primary()
            return {'type': 'Builtin', 'op': 'make_error', 'args': [err_type, err_msg]}

        if t.type == TT.MAP:
            self.advance()
            arr = self.parse_primary()
            self.expect(TT.USING)
            fn = self.parse_primary()
            return {'type': 'Builtin', 'op': 'map', 'args': [arr, fn]}

        if t.type == TT.FILTER:
            self.advance()
            arr = self.parse_primary()
            self.expect(TT.WHERE)
            fn = self.parse_primary()
            return {'type': 'Builtin', 'op': 'filter', 'args': [arr, fn]}

        if t.type == TT.REDUCE:
            self.advance()
            arr = self.parse_primary()
            self.expect(TT.USING)
            fn = self.parse_primary()
            self.expect(TT.START)
            init = self.parse_primary()
            return {'type': 'Builtin', 'op': 'reduce', 'args': [arr, fn, init]}

        # ── new array / function ops ──────────────────────────────────────────

        if t.type == TT.UNIQUE:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'unique', 'args': [self.parse_primary()]}

        if t.type == TT.FLATTEN:
            self.advance()
            return {'type': 'Builtin', 'op': 'flatten', 'args': [self.parse_primary()]}

        if t.type == TT.ZIP:
            self.advance()
            a = self.parse_primary()
            self.expect(TT.WITH)
            b = self.parse_primary()
            return {'type': 'Builtin', 'op': 'zip', 'args': [a, b]}

        if t.type == TT.TALLY:
            self.advance(); self.expect(TT.OF)
            return {'type': 'Builtin', 'op': 'tally', 'args': [self.parse_primary()]}

        if t.type == TT.CLAMP:
            self.advance()
            val = self.parse_primary()
            self.expect(TT.FROM)
            lo = self.parse_expr()
            self.expect(TT.TO)
            hi = self.parse_expr()
            return {'type': 'Builtin', 'op': 'clamp', 'args': [val, lo, hi]}

        if t.type == TT.GROUP:
            self.advance()
            arr = self.parse_primary()
            self.expect(TT.BY)
            fn = self.parse_primary()
            return {'type': 'Builtin', 'op': 'group_by', 'args': [arr, fn]}

        if t.type == TT.PARTIAL:
            self.advance()
            fn = self.parse_primary()
            self.expect(TT.WITH)
            partial_args = [self.parse_expr()]
            while self.match(TT.COMMA):
                partial_args.append(self.parse_expr())
            return {'type': 'Builtin', 'op': 'partial', 'args': [fn] + partial_args}

        raise YPoolError(f'Unexpected "{t.value}"', t.line)

    def parse_ask(self) -> dict:
        self.advance()
        return {'type': 'Ask', 'prompt': self.parse_primary()}

    def parse_call_expr(self) -> dict:
        self.advance()  # CALL
        name = self.expect(TT.IDENTIFIER).value
        keys = []
        while self.current().type == TT.GET:
            self.advance()
            keys.append(self.expect(TT.IDENTIFIER).value)
        args = []
        if self.match(TT.WITH):
            # Use parse_expr so args can contain full arithmetic like n MINUS 1
            args.append(self.parse_expr())
            while self.match(TT.COMMA):
                args.append(self.parse_expr())
        return {'type': 'Call', 'name': name, 'keys': keys, 'args': args}

    def _parse_fetch_expr(self) -> dict:
        self.advance()  # FETCH
        url = self.parse_primary()
        if self.current().type == TT.AS:
            self.advance()
            self.expect(TT.JSON)
            return {'type': 'Builtin', 'op': 'fetch_json', 'args': [url]}
        return {'type': 'Builtin', 'op': 'fetch', 'args': [url]}

    def _parse_list_files(self) -> dict:
        self.advance()  # LIST
        self.expect(TT.FILES)
        self.expect(TT.IN)
        return {'type': 'Builtin', 'op': 'list_files', 'args': [self.parse_primary()]}

    def parse_array_literal(self) -> dict:
        self.advance()  # [
        items = []
        while self.current().type != TT.RBRACKET and not self.at_end():
            if self.current().type == TT.SPREAD:
                self.advance()
                items.append({'type': 'Spread', 'value': self.parse_primary()})
            else:
                items.append(self.parse_concat())
            self.match(TT.COMMA)
        self.expect(TT.RBRACKET)
        return {'type': 'ArrayLiteral', 'items': items}

    def parse_dict_literal(self) -> dict:
        self.advance()  # {
        pairs = []
        while self.current().type != TT.RBRACE and not self.at_end():
            key = self.expect(TT.IDENTIFIER).value
            self.expect(TT.COLON)
            value = self.parse_concat()
            pairs.append((key, value))
            self.match(TT.COMMA)
        self.expect(TT.RBRACE)
        return {'type': 'DictLiteral', 'pairs': pairs}
