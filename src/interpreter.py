import math
import random as _random
import json as _json
import datetime as _dt
import os as _os
import re as _re
from .lexer import YPoolError


# ── signals ────────────────────────────────────────────────────────────────────

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass

class ThrowSignal(Exception):
    def __init__(self, value): self.value = value


# ── environment (scope) ────────────────────────────────────────────────────────

class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.consts = set()
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise YPoolError(f'Unknown name "{name}"')

    def set(self, name, value):
        if name in self.vars:
            if name in self.consts:
                raise YPoolError(f'Cannot reassign constant "{name}"')
            self.vars[name] = value
            return
        if self.parent and self.parent.has(name):
            self.parent.set(name, value)
            return
        self.vars[name] = value

    def define(self, name, value):
        self.vars[name] = value

    def define_const(self, name, value):
        self.vars[name]  = value
        self.consts.add(name)

    def has(self, name):
        return name in self.vars or (self.parent is not None and self.parent.has(name))


# ── function object ────────────────────────────────────────────────────────────

class YPoolFunction:
    def __init__(self, name, params, body, closure, variadic=None):
        self.name     = name
        self.params   = params    # list of (param_name, default_node_or_None)
        self.body     = body
        self.closure  = closure
        self.variadic = variadic  # str name for rest args, or None

    def __repr__(self):
        return f'<function {self.name}>'


# ── interpreter ────────────────────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self._setup_builtins()

    def _setup_builtins(self):
        g = self.globals
        # type conversions
        g.define('asNumber', lambda args: float(args[0]) if args else 0)
        g.define('asText',   lambda args: self.ypool_str(args[0]) if args else '')
        g.define('asBool',   lambda args: bool(args[0]) if args else False)
        # math helpers
        g.define('max',      lambda args: max(args))
        g.define('min',      lambda args: min(args))
        g.define('sum',      lambda args: sum(args[0]) if args and isinstance(args[0], list) else sum(args))
        # regex helpers (callable from ypool via CALL)
        g.define('regex_test',    lambda args: bool(_re.search(str(args[1]), str(args[0]))))
        g.define('regex_find',    lambda args: (m.group(0) if (m := _re.search(str(args[1]), str(args[0]))) else None))
        g.define('regex_all',     lambda args: _re.findall(str(args[1]), str(args[0])))
        g.define('regex_replace', lambda args: _re.sub(str(args[1]), str(args[2]), str(args[0])))

    def run(self, program, env=None):
        env = env or self.globals
        result = None
        for stmt in program['body']:
            result = self.exec_stmt(stmt, env)
        return result

    def exec_block(self, stmts, env):
        result = None
        for stmt in stmts:
            result = self.exec_stmt(stmt, env)
        return result

    # ── statements ─────────────────────────────────────────────────────────────

    def exec_stmt(self, stmt, env):
        t = stmt['type']

        if t == 'Make':
            val = self.eval(stmt['value'], env)
            name = stmt['name']
            if env.has(name):
                env.set(name, val)
            else:
                env.define(name, val)

        elif t == 'Fix':
            val = self.eval(stmt['value'], env)
            env.define_const(stmt['name'], val)

        elif t == 'Show':
            print(self.ypool_str(self.eval(stmt['value'], env)))

        elif t == 'Check':
            if self.truthy(self.eval(stmt['condition'], env)):
                self.exec_block(stmt['then'], Environment(env))
            elif stmt['otherwise']:
                self.exec_block(stmt['otherwise'], Environment(env))

        elif t == 'Keep':
            while self.truthy(self.eval(stmt['condition'], env)):
                try:
                    self.exec_block(stmt['body'], Environment(env))
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        elif t == 'ForEach':
            iterable = self.eval(stmt['iterable'], env)
            if not isinstance(iterable, (list, str)):
                raise YPoolError('FOR EACH requires an array or string')
            for item in iterable:
                loop_env = Environment(env)
                loop_env.define(stmt['var'], item)
                try:
                    self.exec_block(stmt['body'], loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        elif t == 'Count':
            start = int(self.eval(stmt['start'], env))
            end   = int(self.eval(stmt['end'],   env))
            step  = 1 if end >= start else -1
            for i in range(start, end + step, step):
                loop_env = Environment(env)
                if stmt['var']:
                    loop_env.define(stmt['var'], i)
                loop_env.define('it', i)
                try:
                    self.exec_block(stmt['body'], loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        elif t == 'Match':
            subject = self.eval(stmt['subject'], env)
            matched = False
            for case in stmt['cases']:
                op = case.get('op', '==')
                if op == 'between':
                    low  = self.eval(case['low'],  env)
                    high = self.eval(case['high'], env)
                    hit  = low <= subject <= high
                else:
                    pattern_val = self.eval(case['value'], env)
                    hit = self._match_op(subject, op, pattern_val)
                if hit:
                    self.exec_block(case['body'], Environment(env))
                    matched = True
                    break
            if not matched and stmt.get('default'):
                self.exec_block(stmt['default'], Environment(env))

        elif t == 'Teach':
            fn = YPoolFunction(
                stmt['name'],
                stmt['params'],
                stmt['body'],
                env,
                stmt.get('variadic')
            )
            env.define(stmt['name'], fn)

        elif t == 'CallStmt':
            return self.eval(stmt['call'], env)

        elif t == 'Give':
            raise ReturnSignal(self.eval(stmt['value'], env))

        elif t == 'Combine':
            result = self._smart_add(
                self.eval(stmt['left'],  env),
                self.eval(stmt['right'], env)
            )
            if stmt['action'] == 'show':
                print(self.ypool_str(result))
            else:
                name = stmt['name']
                if env.has(name):
                    env.set(name, result)
                else:
                    env.define(name, result)

        elif t == 'Push':
            val = self.eval(stmt['value'], env)
            arr = env.get(stmt['name'])
            if not isinstance(arr, list):
                raise YPoolError(f'"{stmt["name"]}" is not an array')
            arr.append(val)

        elif t == 'Pop':
            arr = env.get(stmt['name'])
            if not isinstance(arr, list):
                raise YPoolError(f'"{stmt["name"]}" is not an array')
            if not arr:
                raise YPoolError('Cannot POP from empty array')
            arr.pop()

        elif t == 'UpdateIndex':
            arr   = env.get(stmt['name'])
            index = int(self.eval(stmt['index'], env))
            value = self.eval(stmt['value'], env)
            if not isinstance(arr, list):
                raise YPoolError(f'"{stmt["name"]}" is not an array')
            if index < 0 or index >= len(arr):
                raise YPoolError(f'Index {index} out of range (length {len(arr)})')
            arr[index] = value

        elif t == 'UpdateKey':
            obj   = env.get(stmt['name'])
            value = self.eval(stmt['value'], env)
            if not isinstance(obj, dict):
                raise YPoolError(f'"{stmt["name"]}" is not a dict')
            obj[stmt['key']] = value

        elif t == 'RemoveAt':
            arr   = env.get(stmt['name'])
            index = int(self.eval(stmt['index'], env))
            if not isinstance(arr, list):
                raise YPoolError(f'"{stmt["name"]}" is not an array')
            if index < 0 or index >= len(arr):
                raise YPoolError(f'Index {index} out of range')
            arr.pop(index)

        elif t == 'ReverseArr':
            arr = env.get(stmt['name'])
            if not isinstance(arr, list):
                raise YPoolError(f'"{stmt["name"]}" is not an array')
            arr.reverse()

        elif t == 'Stop':
            raise BreakSignal()

        elif t == 'Skip':
            raise ContinueSignal()

        elif t == 'Try':
            try:
                self.exec_block(stmt['body'], Environment(env))
            except (ThrowSignal, YPoolError) as e:
                catch_env = Environment(env)
                msg = e.value if isinstance(e, ThrowSignal) else str(e)
                catch_env.define(stmt['err_var'], msg)
                self.exec_block(stmt['handler'], catch_env)

        elif t == 'Throw':
            raise ThrowSignal(self.eval(stmt['value'], env))

        elif t == 'WriteFile':
            path    = self.ypool_str(self.eval(stmt['path'],    env))
            content = self.ypool_str(self.eval(stmt['content'], env))
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except OSError as e:
                raise YPoolError(f'Cannot write "{path}": {e}')

        elif t == 'SortArr':
            arr = env.get(stmt['name'])
            if not isinstance(arr, list):
                raise YPoolError(f'"{stmt["name"]}" is not an array')
            if stmt.get('field') is not None:
                field = self.ypool_str(self.eval(stmt['field'], env))
                arr.sort(key=lambda x: x.get(field, '') if isinstance(x, dict) else x)
            else:
                arr.sort(key=lambda x: (isinstance(x, str), x))

        elif t == 'DestructureArray':
            source = self.eval(stmt['source'], env)
            if not isinstance(source, list):
                raise YPoolError('Array destructuring requires an array')
            for i, name in enumerate(stmt['names']):
                val = source[i] if i < len(source) else None
                if env.has(name):
                    env.set(name, val)
                else:
                    env.define(name, val)

        elif t == 'DestructureDict':
            source = self.eval(stmt['source'], env)
            if not isinstance(source, dict):
                raise YPoolError('Dict destructuring requires a dict')
            for key in stmt['keys']:
                val = source.get(key)
                if env.has(key):
                    env.set(key, val)
                else:
                    env.define(key, val)

        elif t == 'BringIn':
            self._bring_in(stmt['path'], env)

        elif t == 'Repeat':
            count = int(self.eval(stmt['count'], env))
            for i in range(count):
                loop_env = Environment(env)
                if stmt['var']:
                    loop_env.define(stmt['var'], i)
                try:
                    self.exec_block(stmt['body'], loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        else:
            raise YPoolError(f'Unknown statement type: {t}')

        return None

    # ── expressions ────────────────────────────────────────────────────────────

    def eval(self, node, env):
        t = node['type']

        if t == 'Number':     return node['value']
        if t == 'String':     return node['value']
        if t == 'Bool':       return node['value']
        if t == 'Nothing':    return None
        if t == 'Identifier': return env.get(node['name'])

        if t == 'Exists':
            try:
                env.get(node['name'])
                return True
            except YPoolError:
                return False

        if t == 'SafeGet':
            obj = self.eval(node['obj'], env)
            if isinstance(obj, dict):
                if node['key'] in obj:
                    return obj[node['key']]
            return self.eval(node['fallback'], env)

        if t == 'InterpString':
            return self._interpolate(node['value'], env)

        if t == 'Ternary':
            cond = self.eval(node['condition'], env)
            return self.eval(node['then'], env) if self.truthy(cond) else self.eval(node['else'], env)

        if t == 'NullCoalesce':
            val = self.eval(node['left'], env)
            return val if val is not None else self.eval(node['right'], env)

        if t == 'ArrayLiteral':
            result = []
            for item in node['items']:
                if item['type'] == 'Spread':
                    spread_val = self.eval(item['value'], env)
                    if not isinstance(spread_val, list):
                        raise YPoolError('SPREAD requires an array')
                    result.extend(spread_val)
                else:
                    result.append(self.eval(item, env))
            return result

        if t == 'DictLiteral':
            return {key: self.eval(val, env) for key, val in node['pairs']}

        if t == 'Index':
            obj   = self.eval(node['obj'], env)
            index = self.eval(node['index'], env)
            if isinstance(obj, list):
                i = int(index)
                if i < 0 or i >= len(obj):
                    raise YPoolError(f'Index {i} out of range (length {len(obj)})')
                return obj[i]
            if isinstance(obj, str):
                i = int(index)
                return obj[i]
            if isinstance(obj, dict):
                if index not in obj:
                    raise YPoolError(f'Key "{index}" not found in dict')
                return obj[index]
            raise YPoolError('AT indexing requires an array, string, or dict')

        if t == 'DictGet':
            obj = self.eval(node['obj'], env)
            if not isinstance(obj, dict):
                raise YPoolError('GET requires a dict')
            key = node['key']
            if key not in obj:
                raise YPoolError(f'Key "{key}" not found in dict')
            return obj[key]

        if t == 'BinOp':
            op = node['op']
            if op == 'and':
                return self.truthy(self.eval(node['left'], env)) and self.truthy(self.eval(node['right'], env))
            if op == 'or':
                return self.truthy(self.eval(node['left'], env)) or self.truthy(self.eval(node['right'], env))

            left  = self.eval(node['left'],  env)
            right = self.eval(node['right'], env)

            if op == '+':   return left + right
            if op == 'AND': return self._smart_add(left, right)
            if op == '-':   return left - right
            if op == '*':
                if isinstance(left, str) and isinstance(right, (int, float)):
                    return left * int(right)
                if isinstance(left, list) and isinstance(right, (int, float)):
                    return left * int(right)
                return left * right
            if op == '/':
                if right == 0: raise YPoolError('Cannot divide by zero')
                return left / right
            if op == '%':
                if right == 0: raise YPoolError('Cannot mod by zero')
                return left % right
            if op == '**':  return left ** right
            if op == '==':  return left == right
            if op == '!=':  return left != right
            if op == '<':   return left < right
            if op == '>':   return left > right
            if op == '<=':  return left <= right
            if op == '>=':  return left >= right
            raise YPoolError(f'Unknown operator: {op}')

        if t == 'UnaryOp':
            op  = node['op']
            val = self.eval(node['operand'], env)
            if op == '-':   return -val
            if op == 'not': return not self.truthy(val)
            raise YPoolError(f'Unknown unary operator: {op}')

        if t == 'Contains':
            left  = self.eval(node['left'],  env)
            right = self.eval(node['right'], env)
            if isinstance(left, (list, str)):
                return right in left
            if isinstance(left, dict):
                return right in left
            raise YPoolError('CONTAINS requires an array, string, or dict')

        if t == 'Between':
            val  = self.eval(node['value'], env)
            low  = self.eval(node['low'],   env)
            high = self.eval(node['high'],  env)
            return low <= val <= high

        if t == 'Call':
            fn   = env.get(node['name'])
            args = [self.eval(a, env) for a in node['args']]
            return self._call(fn, args, node['name'])

        if t == 'Ask':
            prompt = self.ypool_str(self.eval(node['prompt'], env))
            return input(prompt + ' ')

        if t == 'Builtin':
            return self._builtin(node['op'], node['args'], env)

        raise YPoolError(f'Unknown expression type: {t}')

    # ── function call helper ───────────────────────────────────────────────────

    def _call(self, fn, args, name='?'):
        if callable(fn):
            return fn(args)
        if isinstance(fn, YPoolFunction):
            fn_env = Environment(fn.closure)
            for i, (pname, default_node) in enumerate(fn.params):
                if i < len(args):
                    fn_env.define(pname, args[i])
                elif default_node is not None:
                    fn_env.define(pname, self.eval(default_node, fn.closure))
                else:
                    fn_env.define(pname, None)
            if fn.variadic is not None:
                fn_env.define(fn.variadic, list(args[len(fn.params):]))
            try:
                self.exec_block(fn.body, fn_env)
                return None
            except ReturnSignal as r:
                return r.value
        raise YPoolError(f'"{name}" is not a function')

    # ── string interpolation ───────────────────────────────────────────────────

    def _interpolate(self, s, env):
        def replacer(m):
            name = m.group(1)
            try:
                return self.ypool_str(env.get(name))
            except YPoolError:
                return m.group(0)
        return _re.sub(r'\{([a-zA-Z_]\w*)\}', replacer, s)

    # ── match helper ───────────────────────────────────────────────────────────

    def _match_op(self, subject, op, pattern):
        if op == '==':  return subject == pattern
        if op == '!=':  return subject != pattern
        if op == '>':   return subject >  pattern
        if op == '<':   return subject <  pattern
        if op == '>=':  return subject >= pattern
        if op == '<=':  return subject <= pattern
        return subject == pattern

    # ── module import ──────────────────────────────────────────────────────────

    def _bring_in(self, path, env):
        from .lexer  import Lexer
        from .parser import Parser
        try:
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
        except OSError as e:
            raise YPoolError(f'Cannot import "{path}": {e}')
        tokens  = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        self.run(program, env)

    # ── builtins ───────────────────────────────────────────────────────────────

    def _builtin(self, op, arg_nodes, env):
        args = [self.eval(a, env) for a in arg_nodes]

        if op == 'length':
            val = args[0]
            if isinstance(val, (list, str, dict)):
                return len(val)
            raise YPoolError('LENGTH OF requires array, string, or dict')

        if op == 'upcase':
            if not isinstance(args[0], str): raise YPoolError('UPCASE requires a string')
            return args[0].upper()

        if op == 'downcase':
            if not isinstance(args[0], str): raise YPoolError('DOWNCASE requires a string')
            return args[0].lower()

        if op == 'trim':
            if not isinstance(args[0], str): raise YPoolError('TRIM requires a string')
            return args[0].strip()

        if op == 'split':
            s, sep = args
            if not isinstance(s, str): raise YPoolError('SPLIT requires a string')
            return s.split(sep)

        if op == 'join':
            arr, sep = args
            if not isinstance(arr, list): raise YPoolError('JOIN requires an array')
            return sep.join(self.ypool_str(x) for x in arr)

        if op == 'floor':   return math.floor(args[0])
        if op == 'ceil':    return math.ceil(args[0])
        if op == 'sqrt':
            if args[0] < 0: raise YPoolError('SQRT of negative number')
            return math.sqrt(args[0])
        if op == 'abs':     return abs(args[0])
        if op == 'round':   return round(args[0])

        if op == 'kind':
            v = args[0]
            if v is None:                    return 'nothing'
            if isinstance(v, bool):          return 'bool'
            if isinstance(v, (int, float)):  return 'number'
            if isinstance(v, str):           return 'text'
            if isinstance(v, list):          return 'array'
            if isinstance(v, dict):          return 'dict'
            if isinstance(v, YPoolFunction): return 'function'
            return 'unknown'

        if op == 'keys':
            if not isinstance(args[0], dict): raise YPoolError('KEYS OF requires a dict')
            return list(args[0].keys())

        if op == 'values':
            if not isinstance(args[0], dict): raise YPoolError('VALUES OF requires a dict')
            return list(args[0].values())

        if op == 'has':
            obj, key = args
            if isinstance(obj, dict):  return key in obj
            if isinstance(obj, list):  return key in obj
            if isinstance(obj, str):   return key in obj
            raise YPoolError('HAS requires a dict, array, or string')

        if op == 'random':
            return _random.random()

        if op == 'random_range':
            start, end = int(args[0]), int(args[1])
            return _random.randint(min(start, end), max(start, end))

        # ── string ops ──────────────────────────────────────────────────────────

        if op == 'starts_with':
            s, prefix = args
            if not isinstance(s, str): raise YPoolError('STARTS WITH requires a string')
            return str(s).startswith(str(prefix))

        if op == 'ends_with':
            s, suffix = args
            if not isinstance(s, str): raise YPoolError('ENDS WITH requires a string')
            return str(s).endswith(str(suffix))

        if op == 'slice':
            s, start, end = args
            start, end = int(start), int(end)
            if isinstance(s, (str, list)):
                return s[start:end]
            raise YPoolError('SLICE requires a string or array')

        if op == 'replace':
            s, old, new = self.ypool_str(args[0]), self.ypool_str(args[1]), self.ypool_str(args[2])
            return s.replace(old, new)

        if op == 'format_num':
            num, digits = args[0], int(args[1])
            return f'{num:.{digits}f}'

        if op == 'fits':
            text, pattern = args
            return bool(_re.search(str(pattern), str(text)))

        # ── array ops ───────────────────────────────────────────────────────────

        if op == 'first':
            val = args[0]
            if isinstance(val, (list, str)) and len(val) > 0:
                return val[0]
            raise YPoolError('FIRST OF requires a non-empty array or string')

        if op == 'last':
            val = args[0]
            if isinstance(val, (list, str)) and len(val) > 0:
                return val[-1]
            raise YPoolError('LAST OF requires a non-empty array or string')

        if op == 'average':
            arr = args[0]
            if not isinstance(arr, list) or not arr:
                raise YPoolError('AVERAGE OF requires a non-empty array')
            return sum(arr) / len(arr)

        if op == 'total':
            arr = args[0]
            if not isinstance(arr, list):
                raise YPoolError('TOTAL OF requires an array')
            return sum(arr)

        if op == 'find':
            arr, fn = args
            if not isinstance(arr, list): raise YPoolError('FIND requires an array')
            for item in arr:
                if self.truthy(self._call(fn, [item], 'WHERE')):
                    return item
            return None

        if op == 'find_all':
            arr, fn = args
            if not isinstance(arr, list): raise YPoolError('FIND ALL requires an array')
            return [item for item in arr if self.truthy(self._call(fn, [item], 'WHERE'))]

        if op == 'map':
            arr, fn = args
            if not isinstance(arr, list): raise YPoolError('MAP requires an array')
            return [self._call(fn, [item], 'MAP') for item in arr]

        if op == 'filter':
            arr, fn = args
            if not isinstance(arr, list): raise YPoolError('FILTER requires an array')
            return [item for item in arr if self.truthy(self._call(fn, [item], 'FILTER'))]

        if op == 'reduce':
            arr, fn, acc = args
            if not isinstance(arr, list): raise YPoolError('REDUCE requires an array')
            for item in arr:
                acc = self._call(fn, [acc, item], 'REDUCE')
            return acc

        # ── file / json / date ──────────────────────────────────────────────────

        if op == 'read_file':
            path = self.ypool_str(args[0])
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except OSError as e:
                raise YPoolError(f'Cannot read "{path}": {e}')

        if op == 'parse_json':
            text = args[0]
            if not isinstance(text, str): raise YPoolError('PARSE JSON requires a string')
            try:
                return _json.loads(text)
            except _json.JSONDecodeError as e:
                raise YPoolError(f'Invalid JSON: {e}')

        if op == 'dump_json':
            def _serialize(v):
                if v is None:            return None
                if isinstance(v, bool):  return v
                if isinstance(v, (int, float, str, list, dict)): return v
                if isinstance(v, YPoolFunction): return f'<function {v.name}>'
                return str(v)
            try:
                return _json.dumps(args[0], default=_serialize, ensure_ascii=False, indent=2)
            except Exception as e:
                raise YPoolError(f'Cannot serialize to JSON: {e}')

        if op == 'today':
            return str(_dt.date.today())

        if op == 'now':
            return _dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        raise YPoolError(f'Unknown builtin: {op}')

    # ── helpers ────────────────────────────────────────────────────────────────

    def _smart_add(self, left, right):
        if isinstance(left, str) or isinstance(right, str):
            return self.ypool_str(left) + self.ypool_str(right)
        if isinstance(left, list) and isinstance(right, list):
            return left + right
        return left + right

    def truthy(self, val):
        if val is None or val is False:
            return False
        if isinstance(val, (int, float)) and val == 0:
            return False
        if isinstance(val, (str, list, dict)) and len(val) == 0:
            return False
        return True

    def ypool_str(self, val):
        if val is None:             return 'nothing'
        if val is True:             return 'yeah'
        if val is False:            return 'nah'
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        if isinstance(val, list):
            return '[' + ', '.join(self.ypool_str(x) for x in val) + ']'
        if isinstance(val, dict):
            pairs = ', '.join(f'{k}: {self.ypool_str(v)}' for k, v in val.items())
            return '{' + pairs + '}'
        if isinstance(val, YPoolFunction):
            return f'<function {val.name}>'
        return str(val)
