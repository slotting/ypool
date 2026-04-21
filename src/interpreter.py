import asyncio
import math
import random as _random
import json as _json
import datetime as _dt
import os as _os
import inspect as _inspect
import re as _re
import urllib.request as _urllib_req
import urllib.error   as _urllib_err
from .lexer import YPoolError


# ── signals ────────────────────────────────────────────────────────────────────

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass

class ThrowSignal(Exception):
    def __init__(self, value): self.value = value


# ── Python bridge wrapper ──────────────────────────────────────────────────────

class PyBridge:
    """Wraps a Python module/object so ypool can call its attributes."""
    def __init__(self, module, name='<bridge>'):
        self.module = module
        self.name   = name

    def get_attr(self, attr):
        val = getattr(self.module, attr, _MISSING)
        if val is _MISSING:
            raise YPoolError(f'Bridge "{self.name}" has no attribute "{attr}"')
        if _is_bridgeable(val):
            return PyBridge(val, f'{self.name}.{attr}')
        if callable(val):
            sub_name = f'{self.name}.{attr}'
            def _make_caller(fn, name):
                def _caller(args):
                    result = fn(*args)
                    if _is_bridgeable(result):
                        return PyBridge(result, name + '()')
                    return result
                return _caller
            return _make_caller(val, sub_name)
        return val

    def __call__(self, args):
        result = self.module(*args)
        if _is_bridgeable(result):
            return PyBridge(result, self.name + '()')
        return result

    def _unwrap(self, other):
        return other.module if isinstance(other, PyBridge) else other

    def _wrap(self, result):
        return PyBridge(result, '<bridge>') if _is_bridgeable(result) else result

    def __add__(self, other):   return self._wrap(self.module + self._unwrap(other))
    def __radd__(self, other):  return self._wrap(self._unwrap(other) + self.module)
    def __sub__(self, other):   return self._wrap(self.module - self._unwrap(other))
    def __rsub__(self, other):  return self._wrap(self._unwrap(other) - self.module)
    def __mul__(self, other):   return self._wrap(self.module * self._unwrap(other))
    def __truediv__(self, other): return self._wrap(self.module / self._unwrap(other))
    def __lt__(self, other):    return self.module <  self._unwrap(other)
    def __le__(self, other):    return self.module <= self._unwrap(other)
    def __gt__(self, other):    return self.module >  self._unwrap(other)
    def __ge__(self, other):    return self.module >= self._unwrap(other)
    def __eq__(self, other):    return self.module == self._unwrap(other)
    def __ne__(self, other):    return self.module != self._unwrap(other)
    def __str__(self):          return str(self.module)
    def __repr__(self):         return f'<bridge {self.name}: {self.module!r}>'

_MISSING = object()

_PRIMITIVE_TYPES = (int, float, str, bool, bytes, bytearray,
                    list, tuple, dict, set, frozenset, type(None))

def _is_bridgeable(val):
    if isinstance(val, _PRIMITIVE_TYPES):
        return False
    if _inspect.ismodule(val) or _inspect.isclass(val):
        return True
    if callable(val):
        return False
    return True


# ── async coroutine wrapper ────────────────────────────────────────────────────

class YPoolCoroutine:
    """
    Returned when an ASYNC TEACH function is called without AWAIT.
    Wrap the Python coroutine so ypool can inspect and await it later.
    """
    def __init__(self, coro):
        self.coro = coro

    def __repr__(self):
        return '<coroutine>'


# ── partial application wrapper ────────────────────────────────────────────────

class YPoolPartial:
    def __init__(self, fn, partial_args):
        self.fn           = fn
        self.partial_args = list(partial_args)
        self.name         = (getattr(fn, 'name', None) or '?') + '/partial'

    def __repr__(self):
        return f'<partial {self.name}>'


# ── memoized wrapper ───────────────────────────────────────────────────────────

class YPoolMemoized:
    def __init__(self, fn):
        self.fn    = fn
        self.cache = {}
        self.name  = (getattr(fn, 'name', None) or '?') + '/memoized'

    def __repr__(self):
        return f'<memoized {self.name}>'


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
    def __init__(self, name, params, body, closure, variadic=None, is_async=False):
        self.name     = name
        self.params   = params
        self.body     = body
        self.closure  = closure
        self.variadic = variadic
        self.is_async = is_async

    def __repr__(self):
        prefix = 'async function' if self.is_async else 'function'
        return f'<{prefix} {self.name}>'


# ── interpreter ────────────────────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.globals    = Environment()
        self.call_stack = []
        self._setup_builtins()

    def _setup_builtins(self):
        g = self.globals
        g.define('asNumber', lambda args: float(args[0]) if args else 0)
        g.define('asText',   lambda args: self.ypool_str(args[0]) if args else '')
        g.define('asBool',   lambda args: bool(args[0]) if args else False)
        g.define('max',      lambda args: max(args))
        g.define('min',      lambda args: min(args))
        g.define('sum',      lambda args: sum(args[0]) if args and isinstance(args[0], list) else sum(args))
        g.define('regex_test',    lambda args: bool(_re.search(str(args[1]), str(args[0]))))
        g.define('regex_find',    lambda args: (m.group(0) if (m := _re.search(str(args[1]), str(args[0]))) else None))
        g.define('regex_all',     lambda args: _re.findall(str(args[1]), str(args[0])))
        g.define('regex_replace', lambda args: _re.sub(str(args[1]), str(args[2]), str(args[0])))

    # ── top-level entry ────────────────────────────────────────────────────────

    async def run(self, program, env=None):
        env = env or self.globals
        result = None
        for stmt in program['body']:
            result = await self.exec_stmt(stmt, env)
        return result

    async def exec_block(self, stmts, env):
        result = None
        for stmt in stmts:
            result = await self.exec_stmt(stmt, env)
        return result

    # ── statements ─────────────────────────────────────────────────────────────

    async def exec_stmt(self, stmt, env):
        t = stmt['type']

        if t == 'Make':
            val  = await self.eval(stmt['value'], env)
            name = stmt['name']
            if env.has(name):
                env.set(name, val)
            else:
                env.define(name, val)

        elif t == 'Fix':
            val = await self.eval(stmt['value'], env)
            env.define_const(stmt['name'], val)

        elif t == 'Show':
            print(self.ypool_str(await self.eval(stmt['value'], env)))

        elif t == 'Check':
            if self.truthy(await self.eval(stmt['condition'], env)):
                await self.exec_block(stmt['then'], Environment(env))
            elif stmt['otherwise']:
                await self.exec_block(stmt['otherwise'], Environment(env))

        elif t == 'Keep':
            while self.truthy(await self.eval(stmt['condition'], env)):
                try:
                    await self.exec_block(stmt['body'], Environment(env))
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        elif t == 'ForEach':
            iterable = await self.eval(stmt['iterable'], env)
            if not isinstance(iterable, (list, str)):
                raise YPoolError('FOR EACH requires an array or string')
            for item in iterable:
                loop_env = Environment(env)
                loop_env.define(stmt['var'], item)
                try:
                    await self.exec_block(stmt['body'], loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        elif t == 'Count':
            start = int(await self.eval(stmt['start'], env))
            end   = int(await self.eval(stmt['end'],   env))
            step  = 1 if end >= start else -1
            for i in range(start, end + step, step):
                loop_env = Environment(env)
                if stmt['var']:
                    loop_env.define(stmt['var'], i)
                loop_env.define('it', i)
                try:
                    await self.exec_block(stmt['body'], loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        elif t == 'Match':
            subject = await self.eval(stmt['subject'], env)
            matched = False
            for case in stmt['cases']:
                op = case.get('op', '==')
                if op == 'between':
                    low  = await self.eval(case['low'],  env)
                    high = await self.eval(case['high'], env)
                    hit  = low <= subject <= high
                else:
                    pattern_val = await self.eval(case['value'], env)
                    hit = self._match_op(subject, op, pattern_val)
                if hit:
                    await self.exec_block(case['body'], Environment(env))
                    matched = True
                    break
            if not matched and stmt.get('default'):
                await self.exec_block(stmt['default'], Environment(env))

        elif t == 'Teach':
            fn = YPoolFunction(
                stmt['name'], stmt['params'], stmt['body'], env,
                stmt.get('variadic'), is_async=False
            )
            env.define(stmt['name'], fn)

        elif t == 'AsyncTeach':
            fn = YPoolFunction(
                stmt['name'], stmt['params'], stmt['body'], env,
                stmt.get('variadic'), is_async=True
            )
            env.define(stmt['name'], fn)

        elif t == 'CallStmt':
            return await self.eval(stmt['call'], env)

        elif t == 'Give':
            raise ReturnSignal(await self.eval(stmt['value'], env))

        elif t == 'Combine':
            result = self._smart_add(
                await self.eval(stmt['left'],  env),
                await self.eval(stmt['right'], env)
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
            val = await self.eval(stmt['value'], env)
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
            obj   = env.get(stmt['name'])
            index = await self.eval(stmt['index'], env)
            value = await self.eval(stmt['value'], env)
            if isinstance(obj, dict):
                obj[index] = value
            elif isinstance(obj, list):
                i = int(index)
                if i < 0: i = len(obj) + i
                if i < 0 or i >= len(obj):
                    raise YPoolError(f'Index {i} out of range (length {len(obj)})')
                obj[i] = value
            else:
                raise YPoolError(f'"{stmt["name"]}" is not an array or dict')

        elif t == 'UpdateKey':
            obj   = env.get(stmt['name'])
            value = await self.eval(stmt['value'], env)
            if not isinstance(obj, dict):
                raise YPoolError(f'"{stmt["name"]}" is not a dict')
            obj[stmt['key']] = value

        elif t == 'RemoveAt':
            arr   = env.get(stmt['name'])
            index = int(await self.eval(stmt['index'], env))
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
                await self.exec_block(stmt['body'], Environment(env))
            except (ThrowSignal, YPoolError) as e:
                err_val = e.value if isinstance(e, ThrowSignal) else str(e)
                if not hasattr(e, '_ypool_stack'):
                    e._ypool_stack = list(self.call_stack)
                matched = False
                for catch in stmt['catches']:
                    et = catch['err_type']
                    if et is not None:
                        if not (isinstance(err_val, dict) and err_val.get('type') == et):
                            continue
                    catch_env = Environment(env)
                    catch_env.define(catch['err_var'], err_val)
                    await self.exec_block(catch['body'], catch_env)
                    matched = True
                    break
                if not matched:
                    raise

        elif t == 'Throw':
            raise ThrowSignal(await self.eval(stmt['value'], env))

        elif t == 'WriteFile':
            path    = self.ypool_str(await self.eval(stmt['path'],    env))
            content = self.ypool_str(await self.eval(stmt['content'], env))
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
                field = self.ypool_str(await self.eval(stmt['field'], env))
                arr.sort(key=lambda x: x.get(field, '') if isinstance(x, dict) else x)
            else:
                arr.sort(key=lambda x: (isinstance(x, str), x))

        elif t == 'DestructureArray':
            source = await self.eval(stmt['source'], env)
            if not isinstance(source, list):
                raise YPoolError('Array destructuring requires an array')
            for i, name in enumerate(stmt['names']):
                val = source[i] if i < len(source) else None
                if env.has(name):
                    env.set(name, val)
                else:
                    env.define(name, val)

        elif t == 'DestructureDict':
            source = await self.eval(stmt['source'], env)
            if not isinstance(source, dict):
                raise YPoolError('Dict destructuring requires a dict')
            for key in stmt['keys']:
                val = source.get(key)
                if env.has(key):
                    env.set(key, val)
                else:
                    env.define(key, val)

        elif t == 'Assert':
            if not self.truthy(await self.eval(stmt['condition'], env)):
                msg = self.ypool_str(await self.eval(stmt['message'], env))
                raise ThrowSignal({'type': 'AssertionError', 'msg': msg})

        elif t == 'BringIn':
            path_str = self.ypool_str(await self.eval(stmt['path'], env))
            ns = stmt.get('namespace')
            if ns:
                ns_env = Environment()
                await self._bring_in(path_str, ns_env)
                module = dict(ns_env.vars)
                if env.has(ns):
                    env.set(ns, module)
                else:
                    env.define(ns, module)
            else:
                await self._bring_in(path_str, env)

        elif t == 'Repeat':
            count = int(await self.eval(stmt['count'], env))
            for i in range(count):
                loop_env = Environment(env)
                if stmt['var']:
                    loop_env.define(stmt['var'], i)
                try:
                    await self.exec_block(stmt['body'], loop_env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        elif t == 'Memoize':
            fn = env.get(stmt['name'])
            if not isinstance(fn, (YPoolFunction, YPoolPartial, YPoolMemoized)) and not callable(fn):
                raise YPoolError(f'MEMOIZE requires a function, got {self._kind_of(fn)}')
            memoized = YPoolMemoized(fn)
            alias = stmt['alias']
            if env.has(alias):
                env.set(alias, memoized)
            else:
                env.define(alias, memoized)

        elif t == 'Bridge':
            import importlib
            module_name = self.ypool_str(await self.eval(stmt['module'], env))
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                raise YPoolError(f'Cannot bridge "{module_name}": {e}')
            bridge = PyBridge(module, module_name)
            alias  = stmt['alias']
            if env.has(alias):
                env.set(alias, bridge)
            else:
                env.define(alias, bridge)

        else:
            raise YPoolError(f'Unknown statement type: {t}')

        return None

    # ── expressions ────────────────────────────────────────────────────────────

    async def eval(self, node, env):
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
            obj = await self.eval(node['obj'], env)
            if isinstance(obj, dict) and node['key'] in obj:
                return obj[node['key']]
            return await self.eval(node['fallback'], env)

        if t == 'InterpString':
            return await self._interpolate(node['value'], env)

        if t == 'Ternary':
            cond = await self.eval(node['condition'], env)
            return await self.eval(node['then'], env) if self.truthy(cond) \
                   else await self.eval(node['else'], env)

        if t == 'NullCoalesce':
            val = await self.eval(node['left'], env)
            return val if val is not None else await self.eval(node['right'], env)

        if t == 'ArrayLiteral':
            result = []
            for item in node['items']:
                if item['type'] == 'Spread':
                    spread_val = await self.eval(item['value'], env)
                    if not isinstance(spread_val, list):
                        raise YPoolError('SPREAD requires an array')
                    result.extend(spread_val)
                else:
                    result.append(await self.eval(item, env))
            return result

        if t == 'DictLiteral':
            result = {}
            for key, val in node['pairs']:
                result[key] = await self.eval(val, env)
            return result

        if t == 'Index':
            obj   = await self.eval(node['obj'], env)
            index = await self.eval(node['index'], env)
            if isinstance(obj, list):
                i = int(index)
                if i < 0: i = len(obj) + i
                if i < 0 or i >= len(obj):
                    raise YPoolError(f'Index {int(index)} out of range (length {len(obj)})')
                return obj[i]
            if isinstance(obj, tuple):
                i = int(index)
                if i < 0: i = len(obj) + i
                return obj[i]
            if isinstance(obj, str):
                i = int(index)
                if i < 0: i = len(obj) + i
                return obj[i]
            if isinstance(obj, dict):
                if index not in obj:
                    raise YPoolError(f'Key "{index}" not found in dict')
                return obj[index]
            if isinstance(obj, PyBridge):
                inner = obj.module
                if isinstance(inner, (list, tuple)):
                    i = int(index)
                    if i < 0: i = len(inner) + i
                    result = inner[i]
                    return PyBridge(result, f'{obj.name}[{i}]') if _is_bridgeable(result) else result
                if isinstance(inner, dict):
                    return inner[index]
                if isinstance(index, str):
                    return obj.get_attr(index)
            raise YPoolError('AT indexing requires an array, string, or dict')

        if t == 'DictGet':
            obj = await self.eval(node['obj'], env)
            key = node['key']
            if isinstance(obj, PyBridge):
                return obj.get_attr(key)
            if not isinstance(obj, dict):
                raise YPoolError('GET requires a dict or bridge')
            if key not in obj:
                raise YPoolError(f'Key "{key}" not found in dict')
            return obj[key]

        if t == 'BinOp':
            op = node['op']
            if op == 'and':
                left = await self.eval(node['left'], env)
                return self.truthy(left) and self.truthy(await self.eval(node['right'], env))
            if op == 'or':
                left = await self.eval(node['left'], env)
                return self.truthy(left) or self.truthy(await self.eval(node['right'], env))

            left  = await self.eval(node['left'],  env)
            right = await self.eval(node['right'], env)

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
            val = await self.eval(node['operand'], env)
            if op == '-':   return -val
            if op == 'not': return not self.truthy(val)
            raise YPoolError(f'Unknown unary operator: {op}')

        if t == 'Contains':
            left  = await self.eval(node['left'],  env)
            right = await self.eval(node['right'], env)
            if isinstance(left, (list, str)):
                return right in left
            if isinstance(left, dict):
                return right in left
            raise YPoolError('CONTAINS requires an array, string, or dict')

        if t == 'Between':
            val  = await self.eval(node['value'], env)
            low  = await self.eval(node['low'],   env)
            high = await self.eval(node['high'],  env)
            return low <= val <= high

        if t == 'Call':
            fn = env.get(node['name'])
            for key in node.get('keys', []):
                if isinstance(fn, PyBridge):
                    fn = fn.get_attr(key)
                elif isinstance(fn, dict):
                    if key not in fn:
                        raise YPoolError(f'"{key}" not found in namespace "{node["name"]}"')
                    fn = fn[key]
                else:
                    raise YPoolError(f'"{node["name"]}" is not a namespace or bridge')
            args = []
            for a in node['args']:
                args.append(await self.eval(a, env))
            return await self._call(fn, args, node['name'])

        if t == 'Ask':
            prompt = self.ypool_str(await self.eval(node['prompt'], env))
            return input(prompt + ' ')

        if t == 'Builtin':
            return await self._builtin(node['op'], node['args'], env)

        # ── async nodes ──────────────────────────────────────────────────────────

        if t == 'Await':
            val = await self.eval(node['expr'], env)
            if isinstance(val, YPoolCoroutine):
                return await val.coro
            return val  # awaiting a plain value is a no-op

        if t == 'AwaitAll':
            # expr must evaluate to a list of YPoolCoroutine objects (or plain values)
            items = await self.eval(node['expr'], env)
            if not isinstance(items, list):
                items = [items]
            coros = []
            for item in items:
                if isinstance(item, YPoolCoroutine):
                    coros.append(item.coro)
                else:
                    async def _noop(v=item):
                        return v
                    coros.append(_noop())
            return list(await asyncio.gather(*coros))

        if t == 'AwaitRace':
            items = await self.eval(node['expr'], env)
            if not isinstance(items, list):
                items = [items]
            coros = []
            for item in items:
                if isinstance(item, YPoolCoroutine):
                    coros.append(item.coro)
                else:
                    async def _noop(v=item):
                        return v
                    coros.append(_noop())
            tasks = [asyncio.ensure_future(c) for c in coros]
            try:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for p in pending:
                    p.cancel()
                return done.pop().result()
            except Exception as e:
                raise YPoolError(f'AWAIT RACE failed: {e}')

        raise YPoolError(f'Unknown expression type: {t}')

    # ── function call helper ───────────────────────────────────────────────────

    async def _call(self, fn, args, name='?'):
        # Partial: prepend stored args
        if isinstance(fn, YPoolPartial):
            return await self._call(fn.fn, fn.partial_args + list(args), fn.name)

        # Memoized: cache by repr of args
        if isinstance(fn, YPoolMemoized):
            key = repr(args)
            if key not in fn.cache:
                fn.cache[key] = await self._call(fn.fn, args, fn.name)
            return fn.cache[key]

        # PyBridge (class or module) — call it directly
        if isinstance(fn, PyBridge):
            return fn(args)

        # Plain Python callable (lambda, builtin)
        if callable(fn):
            return fn(args)

        # ypool function
        if isinstance(fn, YPoolFunction):
            self.call_stack.append(name)
            fn_env = Environment(fn.closure)
            for i, (pname, default_node) in enumerate(fn.params):
                if i < len(args):
                    fn_env.define(pname, args[i])
                elif default_node is not None:
                    fn_env.define(pname, await self.eval(default_node, fn.closure))
                else:
                    fn_env.define(pname, None)
            if fn.variadic is not None:
                fn_env.define(fn.variadic, list(args[len(fn.params):]))
            try:
                try:
                    if fn.is_async:
                        # Return a coroutine wrapper — don't run it yet
                        async def _run_body():
                            try:
                                await self.exec_block(fn.body, fn_env)
                                return None
                            except ReturnSignal as r:
                                return r.value
                        self.call_stack.pop()
                        return YPoolCoroutine(_run_body())
                    else:
                        await self.exec_block(fn.body, fn_env)
                        return None
                except ReturnSignal as r:
                    return r.value
                except (ThrowSignal, YPoolError) as e:
                    if not hasattr(e, '_ypool_stack'):
                        e._ypool_stack = list(self.call_stack)
                    raise
            finally:
                if self.call_stack and self.call_stack[-1] == name:
                    self.call_stack.pop()

        raise YPoolError(f'"{name}" is not a function')

    # ── string interpolation ───────────────────────────────────────────────────

    async def _interpolate(self, s, env):
        result = ''
        i = 0
        while i < len(s):
            if s[i] == '{':
                j = s.find('}', i + 1)
                if j == -1:
                    result += s[i:]
                    break
                name = s[i+1:j].strip()
                try:
                    result += self.ypool_str(env.get(name))
                except YPoolError:
                    result += '{' + name + '}'
                i = j + 1
            else:
                result += s[i]
                i += 1
        return result

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

    def _resolve_path(self, path_str: str) -> str:
        if _os.path.isfile(path_str):
            return path_str
        with_ext = path_str if path_str.endswith('.yp') else path_str + '.yp'
        if _os.path.isfile(with_ext):
            return with_ext
        lib_local = _os.path.join('lib', with_ext)
        if _os.path.isfile(lib_local):
            return lib_local
        script_lib = _os.path.normpath(
            _os.path.join(_os.path.dirname(__file__), '..', 'lib', with_ext)
        )
        if _os.path.isfile(script_lib):
            return script_lib
        home_lib = _os.path.join(_os.path.expanduser('~'), '.ypool', 'lib', with_ext)
        if _os.path.isfile(home_lib):
            return home_lib
        for directory in _os.environ.get('YPOOL_PATH', '').split(_os.pathsep):
            if directory:
                candidate = _os.path.join(directory, with_ext)
                if _os.path.isfile(candidate):
                    return candidate
        raise YPoolError(f'Cannot find module "{path_str}"')

    async def _bring_in(self, path_str: str, env):
        from .lexer  import Lexer
        from .parser import Parser
        resolved = self._resolve_path(path_str)
        try:
            with open(resolved, 'r', encoding='utf-8') as f:
                source = f.read()
        except OSError as e:
            raise YPoolError(f'Cannot import "{path_str}": {e}')
        tokens  = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        await self.run(program, env)

    # ── builtins ───────────────────────────────────────────────────────────────

    async def _builtin(self, op, arg_nodes, env):
        args = []
        for a in arg_nodes:
            args.append(await self.eval(a, env))

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

        if op == 'kind':    return self._kind_of(args[0])

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

        if op == 'random':        return _random.random()
        if op == 'random_range':
            start, end = int(args[0]), int(args[1])
            return _random.randint(min(start, end), max(start, end))

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
                if self.truthy(await self._call(fn, [item], 'WHERE')):
                    return item
            return None

        if op == 'find_all':
            arr, fn = args
            if not isinstance(arr, list): raise YPoolError('FIND ALL requires an array')
            result = []
            for item in arr:
                if self.truthy(await self._call(fn, [item], 'WHERE')):
                    result.append(item)
            return result

        if op == 'map':
            arr, fn = args
            if not isinstance(arr, list): raise YPoolError('MAP requires an array')
            result = []
            for item in arr:
                result.append(await self._call(fn, [item], 'MAP'))
            return result

        if op == 'filter':
            arr, fn = args
            if not isinstance(arr, list): raise YPoolError('FILTER requires an array')
            result = []
            for item in arr:
                if self.truthy(await self._call(fn, [item], 'FILTER')):
                    result.append(item)
            return result

        if op == 'reduce':
            arr, fn, acc = args
            if not isinstance(arr, list): raise YPoolError('REDUCE requires an array')
            for item in arr:
                acc = await self._call(fn, [acc, item], 'REDUCE')
            return acc

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
                if isinstance(v, YPoolFunction):  return f'<function {v.name}>'
                if isinstance(v, YPoolPartial):   return f'<partial {v.name}>'
                if isinstance(v, YPoolMemoized):  return f'<memoized {v.name}>'
                if isinstance(v, PyBridge):       return f'<bridge {v.name}>'
                return str(v)
            try:
                return _json.dumps(args[0], default=_serialize, ensure_ascii=False, indent=2)
            except Exception as e:
                raise YPoolError(f'Cannot serialize to JSON: {e}')

        if op == 'today':  return str(_dt.date.today())
        if op == 'now':    return _dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if op == 'log':
            if not isinstance(args[0], (int, float)) or args[0] <= 0:
                raise YPoolError('LOG OF requires a positive number')
            return math.log(args[0])
        if op == 'sin':     return math.sin(args[0])
        if op == 'cos':     return math.cos(args[0])
        if op == 'tan':     return math.tan(args[0])
        if op == 'pi':      return math.pi
        if op == 'e_const': return math.e

        if op == 'merge':
            a, b = args
            if not isinstance(a, dict) or not isinstance(b, dict):
                raise YPoolError('MERGE requires two dicts')
            return {**a, **b}

        # ── HTTP — non-blocking via thread executor ──────────────────────────────

        if op == 'fetch':
            url = self.ypool_str(args[0])
            def _do_fetch():
                try:
                    with _urllib_req.urlopen(url) as resp:
                        return resp.read().decode('utf-8')
                except _urllib_err.URLError as e:
                    raise YPoolError(f'FETCH failed: {e}')
            try:
                return await asyncio.to_thread(_do_fetch)
            except YPoolError:
                raise
            except Exception as e:
                raise YPoolError(f'FETCH failed: {e}')

        if op == 'fetch_json':
            url = self.ypool_str(args[0])
            def _do_fetch_json():
                try:
                    with _urllib_req.urlopen(url) as resp:
                        return _json.loads(resp.read().decode('utf-8'))
                except _urllib_err.URLError as e:
                    raise YPoolError(f'FETCH failed: {e}')
                except _json.JSONDecodeError as e:
                    raise YPoolError(f'FETCH AS JSON: invalid JSON: {e}')
            try:
                return await asyncio.to_thread(_do_fetch_json)
            except YPoolError:
                raise
            except Exception as e:
                raise YPoolError(f'FETCH failed: {e}')

        if op == 'list_files':
            path = self.ypool_str(args[0])
            try:
                return sorted(_os.listdir(path))
            except OSError as e:
                raise YPoolError(f'LIST FILES IN "{path}": {e}')

        if op == 'path_exists':
            return _os.path.exists(self.ypool_str(args[0]))

        if op == 'env_var':
            return _os.environ.get(self.ypool_str(args[0]))

        if op == 'make_error':
            return {'type': self.ypool_str(args[0]), 'msg': self.ypool_str(args[1])}

        if op == 'unique':
            arr = args[0]
            if not isinstance(arr, list): raise YPoolError('UNIQUE OF requires an array')
            seen, result = [], []
            for item in arr:
                if item not in seen:
                    seen.append(item)
                    result.append(item)
            return result

        if op == 'flatten':
            arr = args[0]
            if not isinstance(arr, list): raise YPoolError('FLATTEN requires an array')
            result = []
            for item in arr:
                if isinstance(item, list):
                    result.extend(item)
                else:
                    result.append(item)
            return result

        if op == 'zip':
            a, b = args
            if not isinstance(a, list) or not isinstance(b, list):
                raise YPoolError('ZIP requires two arrays')
            return [[x, y] for x, y in zip(a, b)]

        if op == 'tally':
            arr = args[0]
            if not isinstance(arr, list): raise YPoolError('TALLY OF requires an array')
            result = {}
            for item in arr:
                key = self.ypool_str(item)
                result[key] = result.get(key, 0) + 1
            return result

        if op == 'clamp':
            val, lo, hi = args
            return max(lo, min(hi, val))

        if op == 'group_by':
            arr, fn = args
            if not isinstance(arr, list): raise YPoolError('GROUP requires an array')
            result = {}
            for item in arr:
                key = self.ypool_str(await self._call(fn, [item], 'GROUP'))
                if key not in result:
                    result[key] = []
                result[key].append(item)
            return result

        if op == 'partial':
            fn           = args[0]
            partial_args = args[1:]
            return YPoolPartial(fn, partial_args)

        raise YPoolError(f'Unknown builtin: {op}')

    # ── helpers ────────────────────────────────────────────────────────────────

    def _kind_of(self, val) -> str:
        if val is None:                                    return 'nothing'
        if isinstance(val, bool):                          return 'bool'
        if isinstance(val, (int, float)):                  return 'number'
        if isinstance(val, str):                           return 'text'
        if isinstance(val, list):                          return 'array'
        if isinstance(val, dict):                          return 'dict'
        if isinstance(val, YPoolCoroutine):                return 'coroutine'
        if isinstance(val, (YPoolFunction,
                            YPoolPartial,
                            YPoolMemoized)):               return 'function'
        if isinstance(val, PyBridge):                      return 'bridge'
        if callable(val):                                  return 'function'
        return 'unknown'

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
        if isinstance(val, YPoolCoroutine):  return '<coroutine (not yet awaited)>'
        if isinstance(val, YPoolFunction):   return f'<{"async " if val.is_async else ""}function {val.name}>'
        if isinstance(val, YPoolPartial):    return f'<partial {val.name}>'
        if isinstance(val, YPoolMemoized):   return f'<memoized {val.name}>'
        if isinstance(val, PyBridge):
            if _inspect.ismodule(val.module) or _inspect.isclass(val.module):
                return f'<bridge {val.name}>'
            return str(val.module)
        return str(val)
