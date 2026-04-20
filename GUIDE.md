# ypool language guide

ypool is an English-style programming language. Keywords are ALL CAPS. Variable names are lowercase.

---

## Running ypool

```bash
python run.py examples/01_basics.yp    # run a file
python repl.py                          # interactive shell
```

---

## Comments

```
NOTE: this is a comment — everything after NOTE: is ignored
```

---

## Variables

```
MAKE name BE "loopy"
MAKE age  BE 20
MAKE pi   BE 3.14
MAKE on   BE YEAH
MAKE none BE NOTHING
```

Reassigning works the same way — `MAKE` updates if the variable already exists.

---

## Data Types

| Type    | Example              | KIND OF result |
|---------|----------------------|----------------|
| number  | `42`, `3.14`         | `"number"`     |
| text    | `"hello"`, `'hi'`    | `"text"`       |
| bool    | `YEAH`, `NAH`        | `"bool"`       |
| nothing | `NOTHING`            | `"nothing"`    |
| array   | `[1, 2, 3]`          | `"array"`      |
| dict    | `{key: "val"}`       | `"dict"`       |
| function| `TEACH name { }`     | `"function"`   |

Check the type of any value:
```
SHOW KIND OF "hello"    NOTE: text
SHOW KIND OF 42         NOTE: number
```

---

## Output & Input

```
SHOW "hello"           NOTE: print to screen
SHOW x PLUS y          NOTE: print expression result

MAKE name BE ASK "What is your name?"    NOTE: read user input
```

---

## Arithmetic

```
x PLUS y        NOTE: addition
x MINUS y       NOTE: subtraction
x TIMES y       NOTE: multiplication
x DIVIDED BY y  NOTE: division
x MOD y         NOTE: remainder (modulo)
x POWER y       NOTE: exponentiation (x^y)
```

Math built-ins:
```
FLOOR OF x      NOTE: round down
CEIL OF x       NOTE: round up
ROUND OF x      NOTE: round to nearest
SQRT OF x       NOTE: square root
ABS OF x        NOTE: absolute value
```

---

## Comparison & Conditions

```
x IS y              NOTE: equal
x IS NOT y          NOTE: not equal
x IS MORE THAN y    NOTE: greater than  (>)
x IS LESS THAN y    NOTE: less than     (<)
x IS AT LEAST y     NOTE: >= 
x IS AT MOST y      NOTE: <=
x IS BETWEEN a AND b    NOTE: a <= x <= b
x IS NOTHING        NOTE: null check
x IS NOT NOTHING    NOTE: not null
```

Logical operators:
```
cond ALSO cond2    NOTE: both must be true (AND)
cond OR cond2      NOTE: either must be true
NOT cond           NOTE: invert
```

Contains check:
```
arr CONTAINS value    NOTE: array/string/dict membership
```

---

## If / Otherwise

```
CHECK IF score IS AT LEAST 90 {
    SHOW "A grade"
} OTHERWISE {
    SHOW "not an A"
}
```

Nest as many `CHECK IF` blocks as you need inside `OTHERWISE`.

---

## Loops

### While
```
MAKE i BE 0
KEEP GOING WHILE i IS LESS THAN 5 {
    SHOW i
    MAKE i BE i PLUS 1
}
```

### Count (for loop)
```
COUNT FROM 1 TO 10 AS n {
    SHOW n
}
```
- The variable `it` is always set to the current number inside COUNT.
- Count down: `COUNT FROM 10 TO 1 AS n` — works automatically.

### For Each
```
MAKE fruits BE ["apple", "banana", "cherry"]
FOR EACH fruit IN fruits {
    SHOW fruit
}
```

### Break & Continue
```
STOP    NOTE: exit the loop immediately
SKIP    NOTE: skip to the next iteration
```

---

## Functions

```
TEACH greet USING name {
    COMBINE "hello, " AND name THEN SHOW IT
}

CALL greet WITH "loopy"
```

Return a value:
```
TEACH add USING a, b {
    GIVE BACK a PLUS b
}

MAKE result BE CALL add WITH 10, 5
SHOW result
```

No parameters:
```
TEACH say_hi {
    SHOW "hi!"
}
CALL say_hi
```

Functions are values — store them in variables:
```
TEACH double USING x { GIVE BACK x TIMES 2 }
MAKE fn BE double
SHOW CALL fn WITH 5    NOTE: 10
```

---

## Combine (signature ypool move)

```
COMBINE "hello, " AND name THEN SHOW IT           NOTE: print the result
COMBINE x AND y THEN KEEP IT AS total             NOTE: store the result
```

`COMBINE ... AND ...` works on numbers (addition), strings (concatenation), or mixed (auto-converts).

---

## Arrays

```
MAKE nums BE [1, 2, 3, 4, 5]
MAKE empty BE []
```

| Operation              | Syntax                          |
|------------------------|---------------------------------|
| Access element         | `nums AT 0`                     |
| Length                 | `LENGTH OF nums`                |
| Add to end             | `PUSH 6 INTO nums`              |
| Remove from end        | `POP FROM nums`                 |
| Update element         | `UPDATE nums AT 2 TO 99`        |
| Remove at index        | `REMOVE nums AT 0`              |
| Sort in place          | `SORT nums`                     |
| Reverse in place       | `REVERSE nums`                  |
| Check membership       | `nums CONTAINS 3`               |
| Join to string         | `JOIN nums BY ", "`             |
| Loop over             | `FOR EACH item IN nums { }`     |

Nested arrays:
```
MAKE grid BE [[1, 2], [3, 4]]
SHOW grid AT 0 AT 1    NOTE: 2
```

---

## Dictionaries

```
MAKE person BE {name: "loopy", age: 20}
```

| Operation              | Syntax                             |
|------------------------|------------------------------------|
| Access field           | `person GET name`                  |
| Update field           | `UPDATE person age TO 21`          |
| Check field exists     | `HAS person name`                  |
| Get all keys           | `KEYS OF person`                   |
| Get all values         | `VALUES OF person`                 |
| Length (key count)     | `LENGTH OF person`                 |

---

## Strings

| Operation              | Syntax                              |
|------------------------|-------------------------------------|
| Length                 | `LENGTH OF str`                     |
| Uppercase              | `UPCASE OF str`                     |
| Lowercase              | `DOWNCASE OF str`                   |
| Trim whitespace        | `TRIM str`                          |
| Split                  | `SPLIT str BY ","`                  |
| Join array             | `JOIN arr BY " "`                   |
| Contains substring     | `str CONTAINS "x"`                  |
| Get character          | `str AT 0`                          |
| Concat                 | `"hello" AND " world"`              |

Escape sequences in strings:
- `\n` — newline
- `\t` — tab
- `\\` — backslash
- `\"` — double quote inside double-quoted string

---

## Error Handling

```
TRY {
    THROW "something went wrong"
} CATCH err {
    SHOW err
}
```

- `THROW` accepts any value (string, number, etc.)
- `err` inside CATCH holds the thrown value (or the runtime error message)
- Program continues normally after the CATCH block

---

## Random Numbers

```
MAKE r BE RANDOM                    NOTE: float between 0.0 and 1.0
MAKE n BE RANDOM FROM 1 TO 100     NOTE: integer between 1 and 100
```

---

## Type Conversion

```
MAKE n BE CALL asNumber WITH "42"    NOTE: text → number
MAKE s BE CALL asText WITH 99        NOTE: number → text
MAKE b BE CALL asBool WITH 0         NOTE: any → bool
```

---

## Built-in Functions (called with CALL)

| Name         | Usage                         | Returns           |
|--------------|-------------------------------|-------------------|
| `asNumber`   | `CALL asNumber WITH "42"`     | number            |
| `asText`     | `CALL asText WITH 99`         | text              |
| `asBool`     | `CALL asBool WITH 0`          | bool              |
| `max`        | `CALL max WITH 3, 7`          | largest value     |
| `min`        | `CALL min WITH 3, 7`          | smallest value    |
| `sum`        | `CALL sum WITH [1,2,3]`       | total             |

---

## Full Example: FizzBuzz

```
COUNT FROM 1 TO 20 AS n {
    CHECK IF n MOD 15 IS 0 {
        SHOW "FizzBuzz"
    } OTHERWISE {
        CHECK IF n MOD 3 IS 0 {
            SHOW "Fizz"
        } OTHERWISE {
            CHECK IF n MOD 5 IS 0 {
                SHOW "Buzz"
            } OTHERWISE {
                SHOW n
            }
        }
    }
}
```

## Full Example: Linked list via dicts

```
TEACH make_node USING val {
    GIVE BACK {value: val, next: NOTHING}
}

TEACH push_front USING list, val {
    MAKE node BE CALL make_node WITH val
    UPDATE node next TO list
    GIVE BACK node
}

MAKE head BE NOTHING
MAKE head BE CALL push_front WITH head, 3
MAKE head BE CALL push_front WITH head, 2
MAKE head BE CALL push_front WITH head, 1

MAKE curr BE head
KEEP GOING WHILE curr IS NOT NOTHING {
    SHOW curr GET value
    MAKE curr BE curr GET next
}
```

---

## File structure

```
ypool/
├── src/
│   ├── lexer.py        — tokenizer
│   ├── parser.py       — AST builder
│   └── interpreter.py  — tree-walk executor
├── examples/
│   ├── 01_basics.yp
│   ├── 02_control.yp
│   ├── 03_functions.yp
│   ├── 04_arrays.yp
│   ├── 05_dicts.yp
│   ├── 06_strings.yp
│   ├── 07_errors.yp
│   └── 08_advanced.yp
├── GUIDE.md            — this file
├── repl.py             — interactive shell
└── run.py              — file runner
```
