# ypool

**ypool** is a programming language that reads like plain English.
Every keyword is written in ALL CAPS. Your own names (variables, functions) are written in lowercase.
No semicolons. No curly-brace confusion. Just clear, readable code.

```
MAKE name BE "loopy"
MAKE score BE 97

CHECK IF score IS AT LEAST 90 {
    SHOW "Nice work, " AND name AND "!"
} OTHERWISE {
    SHOW "Keep going, " AND name AND "."
}
```

---

## Getting Started

**Run a file**
```bash
python ypool.py hello.yp
```

**Start the interactive REPL** (type code and see results instantly)
```bash
python ypool.py
```

**Run a quick one-liner**
```bash
python ypool.py -c "SHOW 2 PLUS 2"
```

**Run a file, then stay in the REPL with all its variables loaded**
```bash
python ypool.py -i myscript.yp
```

> On Windows you can also use `ypool.bat` or `yp.bat` so you just type `ypool hello.yp`.

---

## What ypool looks like

```
NOTE: ── guess the number game ───────────────────────────────────────

FIX secret BE 42
MAKE guesses BE 0

MAKE guess BE CALL asNumber WITH ASK "Guess a number: "
MAKE guesses BE guesses PLUS 1

KEEP GOING WHILE guess IS NOT secret {
    CHECK IF guess IS LESS THAN secret {
        SHOW "Too low! Try again."
    } OTHERWISE {
        SHOW "Too high! Try again."
    }
    MAKE guess BE CALL asNumber WITH ASK "Guess a number: "
    MAKE guesses BE guesses PLUS 1
}

SHOW "You got it in " AND guesses AND " guesses!"
```

---

## Features at a glance

| Feature | Syntax |
|---|---|
| Variables | `MAKE x BE 10` |
| Constants | `FIX pi BE 3.14` |
| Output | `SHOW "hello"` |
| Input | `ASK "Your name: "` |
| If/else | `CHECK IF … { } OTHERWISE { }` |
| While loop | `KEEP GOING WHILE … { }` |
| Count loop | `COUNT FROM 1 TO 10 AS n { }` |
| For each | `FOR EACH item IN list { }` |
| Repeat | `REPEAT 5 { }` |
| Functions | `TEACH add USING a, b { GIVE BACK a PLUS b }` |
| Call | `CALL add WITH 3, 7` |
| Arrays | `[1, 2, 3]` |
| Dicts | `{name: "loopy", age: 20}` |
| Error handling | `TRY { } CATCH e { }` |
| Imports | `BRING IN "arrays"` |
| Python bridge | `BRIDGE "math" AS m` |
| Comments | `NOTE: anything here` |

---

## Learn More

Read the full guide → **[GUIDE.md](GUIDE.md)**

The guide covers every feature from the very basics to advanced topics, written to be easy to understand for beginners of any age.

---

## Project layout

```
ypool/
├── ypool.py          ← main CLI entry point
├── ypool.bat         ← Windows shortcut: ypool hello.yp
├── yp.bat            ← Windows shortcut: yp hello.yp
├── repl.py           ← interactive shell
├── src/
│   ├── lexer.py      ← breaks source into tokens
│   ├── parser.py     ← builds the syntax tree
│   └── interpreter.py ← runs the program
├── lib/              ← standard library (BRING IN "arrays" etc.)
│   ├── arrays.yp
│   ├── strings.yp
│   └── math.yp
├── examples/         ← 14 example programs
└── GUIDE.md          ← the complete language guide
```
