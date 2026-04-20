# The Complete ypool Guide

Welcome! This guide teaches you everything about **ypool** from the very beginning.
No prior programming experience required — but if you already know another language,
you'll pick this up in minutes.

---

## Table of Contents

1. [What is ypool?](#1-what-is-ypool)
2. [Running your first program](#2-running-your-first-program)
3. [Comments](#3-comments)
4. [Variables](#4-variables)
5. [Data types](#5-data-types)
6. [Output and Input](#6-output-and-input)
7. [Math and Arithmetic](#7-math-and-arithmetic)
8. [Text (Strings)](#8-text-strings)
9. [Comparisons and Logic](#9-comparisons-and-logic)
10. [Making Decisions — CHECK IF](#10-making-decisions--check-if)
11. [Loops](#11-loops)
12. [Functions](#12-functions)
13. [Arrays](#13-arrays)
14. [Dictionaries](#14-dictionaries)
15. [Constants](#15-constants)
16. [Advanced Strings](#16-advanced-strings)
17. [Match (Switch)](#17-match-switch)
18. [Error Handling](#18-error-handling)
19. [Files and JSON](#19-files-and-json)
20. [Dates and Time](#20-dates-and-time)
21. [Math Builtins](#21-math-builtins)
22. [Array Power Tools](#22-array-power-tools)
23. [New Array Tools](#23-new-array-tools)
24. [Partial Functions and Memoize](#24-partial-functions-and-memoize)
25. [Importing Libraries](#25-importing-libraries)
26. [Using Python Libraries (Bridge)](#26-using-python-libraries-bridge)
27. [The Standard Library](#27-the-standard-library)
28. [The REPL](#28-the-repl)
29. [Full Examples](#29-full-examples)
30. [Quick Reference Cheat Sheet](#30-quick-reference-cheat-sheet)

---

## 1. What is ypool?

ypool is a programming language built around one idea: **code should be readable**.

Instead of symbols and abbreviations, ypool uses plain English words.
If you can read a sentence, you can read ypool code.

**The two golden rules:**

- **KEYWORDS** (built-in words the language understands) are always **ALL CAPS**
- **your own names** (variables, functions) are always **lowercase**

```
NOTE: this reads almost like a sentence
MAKE greeting BE "Hello, world!"
SHOW greeting
```

That's it. Two rules. Everything else follows from them.

---

## 2. Running your first program

**Step 1 — Create a file** called `hello.yp` and write:

```
SHOW "Hello, world!"
```

**Step 2 — Run it:**

```bash
python ypool.py hello.yp
```

You should see:
```
Hello, world!
```

**The REPL (interactive mode)**

Type `python ypool.py` with no file to open the interactive shell.
Type any ypool code and press Enter to run it immediately.

```
ypool> SHOW 2 PLUS 2
4
ypool> MAKE name BE "loopy"
ypool> SHOW "Hey, " AND name
Hey, loopy
```

> **Tip:** In the REPL, type `:help` for a list of commands, `:vars` to see all your variables, `:quit` to exit.

---

## 3. Comments

A comment is a note to yourself (or others reading your code). Comments are completely ignored when the program runs.

```
NOTE: this is a comment — the whole line is ignored

MAKE x BE 10    NOTE: you can also comment at the end of a line
```

Everything after `NOTE:` on that line is skipped. Comments are great for explaining what your code does.

---

## 4. Variables

A **variable** is a named box that holds a value. Use `MAKE ... BE ...` to create one.

```
MAKE name    BE "Alice"
MAKE age     BE 16
MAKE score   BE 98.5
MAKE active  BE YEAH
MAKE nothing BE NOTHING
```

**Changing a variable** — just `MAKE` it again:

```
MAKE score BE 98.5
SHOW score          NOTE: 98.5

MAKE score BE 100
SHOW score          NOTE: 100
```

**Naming rules:**
- Must start with a letter or underscore
- Can contain letters, numbers, underscores
- Use lowercase (e.g. `my_score`, `player1`, `total_price`)
- No spaces allowed inside a name

```
MAKE first_name BE "Jordan"
MAKE total_items BE 42
MAKE is_logged_in BE YEAH
```

---

## 5. Data Types

Every value in ypool has a type. Here are all of them:

| Type | What it is | Example |
|---|---|---|
| `number` | Any number (whole or decimal) | `42`, `3.14`, `-7` |
| `text` | A string of characters | `"hello"`, `'world'` |
| `bool` | True or false | `YEAH`, `NAH` |
| `nothing` | No value / empty | `NOTHING` |
| `array` | A list of values | `[1, 2, 3]` |
| `dict` | Key-value pairs | `{name: "Alex"}` |
| `function` | A reusable block of code | `TEACH greet { }` |

**Check the type of any value with `KIND OF`:**

```
SHOW KIND OF "hello"    NOTE: text
SHOW KIND OF 42         NOTE: number
SHOW KIND OF YEAH       NOTE: bool
SHOW KIND OF NOTHING    NOTE: nothing
SHOW KIND OF [1, 2, 3]  NOTE: array
SHOW KIND OF {x: 1}     NOTE: dict
```

---

## 6. Output and Input

### Showing things

`SHOW` prints any value to the screen:

```
SHOW "Hello!"
SHOW 42
SHOW YEAH
SHOW 3.14
SHOW "Your score is " AND score    NOTE: combine text with a value
```

### String interpolation

Use `$"..."` to embed variables directly inside text with `{curly braces}`:

```
MAKE name  BE "Jordan"
MAKE score BE 95
SHOW $"Hello, {name}! Your score is {score}."
```

Output:
```
Hello, Jordan! Your score is 95.
```

> **Note:** Only simple variable names work inside `{ }`. For anything more complex, use `AND` instead.

### Getting input from the user

`ASK` shows a prompt and waits for the user to type something. It always returns text.

```
MAKE name BE ASK "What is your name? "
SHOW "Nice to meet you, " AND name AND "!"
```

If you need a number from the user, convert it:

```
MAKE age_text BE ASK "How old are you? "
MAKE age BE CALL asNumber WITH age_text
SHOW "In 10 years you will be " AND age PLUS 10
```

---

## 7. Math and Arithmetic

### Basic operators

```
SHOW 10 PLUS 3       NOTE: 13  (addition)
SHOW 10 MINUS 3      NOTE: 7   (subtraction)
SHOW 10 TIMES 3      NOTE: 30  (multiplication)
SHOW 10 DIVIDED BY 3 NOTE: 3.333...  (division)
SHOW 10 MOD 3        NOTE: 1   (remainder / modulo)
SHOW 2 POWER 8       NOTE: 256 (exponentiation: 2^8)
```

You can also use `+`, `-`, `*`, `/`, `%` as shorthand symbols:

```
SHOW 5 + 3     NOTE: same as 5 PLUS 3
SHOW 10 - 4    NOTE: same as 10 MINUS 4
SHOW 3 * 7     NOTE: same as 3 TIMES 7
SHOW 15 / 4    NOTE: same as 15 DIVIDED BY 4
SHOW 17 % 5    NOTE: same as 17 MOD 5
```

### Math built-ins

```
SHOW FLOOR OF 3.9     NOTE: 3   (round down)
SHOW CEIL OF 3.1      NOTE: 4   (round up)
SHOW ROUND OF 3.5     NOTE: 4   (round to nearest)
SHOW SQRT OF 16       NOTE: 4   (square root)
SHOW ABS OF -7        NOTE: 7   (absolute value / remove minus sign)
```

### Order of operations

ypool follows the standard math order (same as most languages):

1. Parentheses `( )` — always first
2. `POWER` — exponents
3. `TIMES`, `DIVIDED BY`, `MOD` — multiplication/division
4. `PLUS`, `MINUS` — addition/subtraction

```
SHOW 2 PLUS 3 TIMES 4    NOTE: 14  (3*4 first, then +2)
SHOW (2 PLUS 3) TIMES 4  NOTE: 20  (parens force 2+3 first)
```

### Combining numbers and text

Use `AND` to join numbers with text (it auto-converts):

```
MAKE score BE 95
SHOW "You scored " AND score AND " points!"   NOTE: You scored 95 points!
```

---

## 8. Text (Strings)

Text values (also called strings) are surrounded by quotes. You can use double `"` or single `'` quotes.

```
MAKE greeting BE "Hello, world!"
MAKE name     BE 'Alice'
```

### String operations

```
MAKE s BE "Hello, ypool!"

SHOW LENGTH OF s              NOTE: 13  (how many characters)
SHOW UPCASE OF s              NOTE: HELLO, YPOOL!
SHOW DOWNCASE OF s            NOTE: hello, ypool!
SHOW TRIM "  hello  "         NOTE: hello  (removes spaces from both ends)
```

### Slicing (getting part of a string)

`SLICE` gives you a piece of a string. It starts at the `FROM` position and stops *before* the `TO` position (positions start at 0):

```
MAKE word BE "programming"

SHOW SLICE word FROM 0 TO 4    NOTE: prog
SHOW SLICE word FROM 4 TO 11   NOTE: ramming
```

> **Tip:** `SLICE` also works on arrays!

### Splitting and joining

```
MAKE csv BE "apple,banana,cherry"
MAKE fruits BE SPLIT csv BY ","
SHOW fruits                          NOTE: [apple, banana, cherry]

MAKE sentence BE JOIN fruits BY " and "
SHOW sentence                        NOTE: apple and banana and cherry
```

### Checking the start and end

```
MAKE url BE "https://example.com"

SHOW url STARTS WITH "https"    NOTE: yeah
SHOW url ENDS WITH ".com"       NOTE: yeah
SHOW url STARTS WITH "http:"    NOTE: nah
```

### Searching and replacing

```
MAKE msg BE "I love cats. Cats are great."

SHOW msg CONTAINS "cats"               NOTE: yeah
SHOW REPLACE IN msg FROM "cats" TO "dogs"
NOTE: I love dogs. Cats are great.   (only replaces first match)
```

### Checking if text matches a pattern (FITS)

`FITS` checks whether text matches a **regular expression** (a special pattern language):

```
MAKE email BE "user@example.com"
SHOW email FITS "[a-z]+@[a-z]+\\.[a-z]+"    NOTE: yeah

MAKE phone BE "555-1234"
SHOW phone FITS "\\d{3}-\\d{4}"              NOTE: yeah
```

> **Tip:** Use `\\d` for "a digit", `\\w` for "a letter or digit", `+` means "one or more", `*` means "zero or more".

### Escape sequences

Inside strings, a backslash `\` followed by a letter has special meaning:

| Escape | Meaning |
|---|---|
| `\n` | New line |
| `\t` | Tab character |
| `\\` | Literal backslash |
| `\"` | Double quote inside `"..."` |
| `\'` | Single quote inside `'...'` |

```
SHOW "Line 1\nLine 2"
NOTE: Line 1
NOTE: Line 2
```

---

## 9. Comparisons and Logic

Comparisons always produce `YEAH` (true) or `NAH` (false).

### Comparison operators

```
SHOW 5 IS 5              NOTE: yeah   (equal)
SHOW 5 IS NOT 3          NOTE: yeah   (not equal)
SHOW 10 IS MORE THAN 5   NOTE: yeah   (greater than)
SHOW 3 IS LESS THAN 7    NOTE: yeah   (less than)
SHOW 5 IS AT LEAST 5     NOTE: yeah   (greater than or equal)
SHOW 8 IS AT MOST 10     NOTE: yeah   (less than or equal)
```

### Range check

```
MAKE age BE 17
SHOW age IS BETWEEN 13 AND 19    NOTE: yeah  (is it in this range?)
```

### Null check

```
MAKE x BE NOTHING
SHOW x IS NOTHING        NOTE: yeah
SHOW x IS NOT NOTHING    NOTE: nah
```

### Logical operators

Use these to combine comparisons:

```
MAKE age BE 20
MAKE has_id BE YEAH

NOTE: ALSO = both must be true (like "and")
SHOW age IS AT LEAST 18 ALSO has_id IS YEAH    NOTE: yeah

NOTE: OR = at least one must be true (like "or")
SHOW age IS LESS THAN 10 OR age IS MORE THAN 18    NOTE: yeah

NOTE: NOT = flip the result (like "not")
SHOW NOT YEAH    NOTE: nah
SHOW NOT NAH     NOTE: yeah
```

### Membership check

```
MAKE fruits BE ["apple", "banana", "cherry"]
SHOW fruits CONTAINS "banana"    NOTE: yeah
SHOW fruits CONTAINS "grape"     NOTE: nah

MAKE msg BE "hello world"
SHOW msg CONTAINS "world"        NOTE: yeah
```

---

## 10. Making Decisions — CHECK IF

`CHECK IF` runs a block of code only when a condition is true.

### Basic if

```
MAKE score BE 85

CHECK IF score IS AT LEAST 90 {
    SHOW "Grade: A"
}
```

### If / else

```
CHECK IF score IS AT LEAST 60 {
    SHOW "You passed!"
} OTHERWISE {
    SHOW "You need to retake the test."
}
```

### If / else if / else

Chain as many checks as you like:

```
CHECK IF score IS AT LEAST 90 {
    SHOW "Grade: A"
} OTHERWISE {
    CHECK IF score IS AT LEAST 80 {
        SHOW "Grade: B"
    } OTHERWISE {
        CHECK IF score IS AT LEAST 70 {
            SHOW "Grade: C"
        } OTHERWISE {
            SHOW "Grade: F"
        }
    }
}
```

### Ternary (one-liner if/else)

When you need a quick one-line decision to pick a value, use the inline form:

```
MAKE grade BE IF score IS AT LEAST 90 THEN "A" ELSE "B"
SHOW grade
```

### Null coalescing (use a backup value)

`EITHER ... OR ...` returns the first value if it exists, otherwise the second:

```
MAKE user_color BE NOTHING
MAKE color BE EITHER user_color OR "blue"
SHOW color    NOTE: blue  (because user_color is NOTHING)

MAKE user_color BE "red"
MAKE color BE EITHER user_color OR "blue"
SHOW color    NOTE: red  (because user_color has a value)
```

---

## 11. Loops

### KEEP GOING WHILE (while loop)

Keeps running a block as long as a condition is true:

```
MAKE i BE 1
KEEP GOING WHILE i IS AT MOST 5 {
    SHOW i
    MAKE i BE i PLUS 1
}
NOTE: prints 1 2 3 4 5
```

> **Warning:** If your condition never becomes false, the loop runs forever. Always make sure something inside the loop changes the condition!

### COUNT FROM / TO (numeric for loop)

The cleanest way to loop a specific number of times:

```
COUNT FROM 1 TO 5 AS n {
    SHOW n
}
NOTE: prints 1 2 3 4 5
```

- `n` holds the current number on each pass
- The built-in variable `it` also holds the current number (useful for quick one-liners)
- Count backwards: `COUNT FROM 10 TO 1` — ypool figures it out automatically

```
NOTE: Countdown!
COUNT FROM 10 TO 1 AS n {
    SHOW n
}
SHOW "Blast off!"
```

### FOR EACH (loop over a list)

Loop over every item in an array or every character in a string:

```
MAKE colors BE ["red", "green", "blue"]
FOR EACH color IN colors {
    SHOW color
}
```

```
MAKE word BE "hello"
FOR EACH letter IN word {
    SHOW letter
}
```

### REPEAT (repeat N times)

The simplest loop — just repeat something N times. Optionally get the current count:

```
REPEAT 3 {
    SHOW "Hello!"
}

REPEAT 5 AS i {
    SHOW "Turn " AND i    NOTE: i is 0, 1, 2, 3, 4
}
```

### Breaking out and skipping

- `STOP` — immediately exits the loop
- `SKIP` — skips the rest of this pass and starts the next one

```
COUNT FROM 1 TO 10 AS n {
    CHECK IF n IS 5 { STOP }      NOTE: exits when n reaches 5
    SHOW n
}
NOTE: prints 1 2 3 4

COUNT FROM 1 TO 10 AS n {
    CHECK IF n MOD 2 IS 0 { SKIP }    NOTE: skips even numbers
    SHOW n
}
NOTE: prints 1 3 5 7 9
```

---

## 12. Functions

A function is a reusable block of code you can call by name.
Use `TEACH` to define one.

### Basic function

```
TEACH say_hello {
    SHOW "Hello, world!"
}

CALL say_hello    NOTE: Hello, world!
```

### Function with parameters

```
TEACH greet USING name {
    SHOW "Hello, " AND name AND "!"
}

CALL greet WITH "Alice"    NOTE: Hello, Alice!
CALL greet WITH "Bob"      NOTE: Hello, Bob!
```

### Function that returns a value

```
TEACH add USING a, b {
    GIVE BACK a PLUS b
}

MAKE result BE CALL add WITH 10, 5
SHOW result    NOTE: 15
```

> `GIVE BACK` sends a value out of the function and stops it immediately.

### Multiple parameters

```
TEACH describe_person USING name, age, city {
    SHOW $"Name: {name}, Age: {age}, City: {city}"
}

CALL describe_person WITH "Jordan", 17, "Miami"
```

### Default parameter values

Give a parameter a default so it's optional when calling the function:

```
TEACH greet USING name, greeting DEFAULT "Hello" {
    SHOW greeting AND ", " AND name AND "!"
}

CALL greet WITH "Alice"              NOTE: Hello, Alice!
CALL greet WITH "Alice", "Hey"       NOTE: Hey, Alice!
```

### Variadic functions (accept any number of arguments)

Use `...` before the last parameter name to collect all extra arguments into an array:

```
TEACH total USING ...numbers {
    GIVE BACK TOTAL OF numbers
}

SHOW CALL total WITH 1, 2, 3           NOTE: 6
SHOW CALL total WITH 10, 20, 30, 40    NOTE: 100
```

### Functions as values

Functions can be stored in variables and passed around:

```
TEACH double USING x { GIVE BACK x TIMES 2 }
TEACH triple USING x { GIVE BACK x TIMES 3 }

MAKE transform BE double

SHOW CALL transform WITH 5     NOTE: 10
MAKE transform BE triple
SHOW CALL transform WITH 5     NOTE: 15
```

### Closures (functions that remember their scope)

A function defined inside another function remembers the outer variables:

```
TEACH make_counter {
    MAKE count BE 0
    TEACH increment {
        MAKE count BE count PLUS 1
        GIVE BACK count
    }
    GIVE BACK increment
}

MAKE counter BE CALL make_counter
SHOW CALL counter    NOTE: 1
SHOW CALL counter    NOTE: 2
SHOW CALL counter    NOTE: 3
```

### Returning multiple values

Return an array to send back more than one value, then destructure it:

```
TEACH min_max USING arr {
    MAKE lo BE arr AT 0
    MAKE hi BE arr AT 0
    FOR EACH n IN arr {
        CHECK IF n IS LESS THAN lo { MAKE lo BE n }
        CHECK IF n IS MORE THAN hi { MAKE hi BE n }
    }
    GIVE BACK lo, hi
}

MAKE [smallest, largest] FROM CALL min_max WITH [3, 1, 4, 1, 5, 9]
SHOW smallest    NOTE: 1
SHOW largest     NOTE: 9
```

### Recursion (a function that calls itself)

```
TEACH factorial USING n {
    CHECK IF n IS AT MOST 1 { GIVE BACK 1 }
    GIVE BACK n TIMES (CALL factorial WITH n MINUS 1)
}

SHOW CALL factorial WITH 5    NOTE: 120
```

> **Important:** When a recursive call's result is part of a bigger arithmetic expression,
> wrap the `CALL` in parentheses: `(CALL fn WITH n MINUS 1) PLUS (CALL fn WITH n MINUS 2)`

---

## 13. Arrays

An array is an ordered list of values. Items can be any type, including other arrays.

### Creating arrays

```
MAKE nums    BE [1, 2, 3, 4, 5]
MAKE words   BE ["apple", "banana", "cherry"]
MAKE mixed   BE [1, "two", YEAH, NOTHING]
MAKE empty   BE []
MAKE nested  BE [[1, 2], [3, 4], [5, 6]]
```

### Accessing items (index starts at 0)

```
MAKE fruits BE ["apple", "banana", "cherry"]

SHOW fruits AT 0    NOTE: apple  (first item)
SHOW fruits AT 1    NOTE: banana (second item)
SHOW fruits AT 2    NOTE: cherry (third item)

NOTE: negative indexes count from the end:
SHOW fruits AT -1   NOTE: cherry (last item)
SHOW fruits AT -2   NOTE: banana (second-to-last)
```

### Length

```
SHOW LENGTH OF fruits    NOTE: 3
```

### Adding and removing

```
MAKE nums BE [1, 2, 3]

PUSH 4 INTO nums        NOTE: nums is now [1, 2, 3, 4]
POP FROM nums           NOTE: removes the last item → [1, 2, 3]
```

### Updating and removing specific positions

```
MAKE nums BE [10, 20, 30, 40, 50]

UPDATE nums AT 2 TO 99      NOTE: [10, 20, 99, 40, 50]  (change index 2)
REMOVE nums AT 0            NOTE: removes first item

NOTE: Using MAKE:
MAKE nums AT 1 BE 999       NOTE: same as UPDATE nums AT 1 TO 999
```

### Sorting and reversing

```
MAKE nums BE [5, 2, 8, 1, 9]
SORT nums                NOTE: nums is now [1, 2, 5, 8, 9] (in place!)
REVERSE nums             NOTE: nums is now [9, 8, 5, 2, 1] (in place!)
```

Sort an array of dicts by a field:
```
MAKE people BE [{name: "Charlie"}, {name: "Alice"}, {name: "Bob"}]
SORT people BY name
SHOW people    NOTE: [{name: Alice}, {name: Bob}, {name: Charlie}]
```

### Checking membership

```
MAKE nums BE [1, 2, 3, 4, 5]
SHOW nums CONTAINS 3    NOTE: yeah
SHOW nums CONTAINS 9    NOTE: nah
```

### Slicing

```
MAKE nums BE [10, 20, 30, 40, 50]
SHOW SLICE nums FROM 1 TO 4    NOTE: [20, 30, 40]
```

### Joining to text

```
MAKE words BE ["hello", "world", "ypool"]
SHOW JOIN words BY " "     NOTE: hello world ypool
SHOW JOIN words BY ", "    NOTE: hello, world, ypool
```

### Spread (copy/merge arrays)

Use `...arr` inside a new array literal to spread all items into it:

```
MAKE a BE [1, 2, 3]
MAKE b BE [4, 5, 6]
MAKE c BE [...a, ...b]    NOTE: [1, 2, 3, 4, 5, 6]

MAKE copy BE [...a]       NOTE: creates a fresh copy of a
```

### Destructuring (unpack into variables)

```
MAKE [first, second, third] FROM [10, 20, 30]
SHOW first     NOTE: 10
SHOW second    NOTE: 20
SHOW third     NOTE: 30
```

### Aggregate operations

```
MAKE nums BE [4, 7, 2, 9, 1]

SHOW TOTAL OF nums      NOTE: 23  (sum of all numbers)
SHOW AVERAGE OF nums    NOTE: 4.6 (mean)
SHOW FIRST OF nums      NOTE: 4   (first element)
SHOW LAST OF nums       NOTE: 1   (last element)
```

---

## 14. Dictionaries

A dictionary (dict) stores key-value pairs — like a real dictionary where you look up a word (key) to find its definition (value).

### Creating dicts

```
MAKE person BE {name: "Alice", age: 17, city: "Miami"}
MAKE empty  BE {}
```

Keys must be identifiers (no quotes needed around them).

### Accessing values

```
SHOW person GET name    NOTE: Alice
SHOW person GET age     NOTE: 17
```

### Safe access with a fallback (GET ... ELSE)

```
SHOW person GET nickname ELSE "no nickname"
NOTE: "no nickname" — because nickname key doesn't exist
```

### Updating values

```
UPDATE person age TO 18
SHOW person GET age    NOTE: 18
```

### Adding new keys

```
UPDATE person email TO "alice@example.com"
```

### Checking if a key exists

```
SHOW HAS person name     NOTE: yeah
SHOW HAS person phone    NOTE: nah
```

### Getting all keys and values

```
SHOW KEYS OF person      NOTE: [name, age, city]
SHOW VALUES OF person    NOTE: [Alice, 17, Miami]
SHOW LENGTH OF person    NOTE: 3 (number of keys)
```

### Destructuring (unpack into variables)

```
MAKE {name, age, city} FROM person
SHOW name    NOTE: Alice
SHOW age     NOTE: 17
SHOW city    NOTE: Miami
```

### Merging two dicts

`MERGE` combines two dicts. If both have the same key, the second one wins:

```
MAKE defaults BE {theme: "dark", lang: "en", size: 14}
MAKE user     BE {lang: "es", size: 18}
MAKE settings BE MERGE defaults WITH user

SHOW settings GET theme    NOTE: dark  (from defaults)
SHOW settings GET lang     NOTE: es    (user overrode it)
SHOW settings GET size     NOTE: 18    (user overrode it)
```

### Dynamic key assignment

Set a key using a variable as the key name:

```
MAKE key BE "score"
MAKE stats BE {}
MAKE stats AT key BE 100
SHOW stats GET score    NOTE: 100
```

---

## 15. Constants

A constant is a variable that **cannot be changed** after it's set. Use `FIX` instead of `MAKE`.

```
FIX max_score BE 100
FIX pi        BE 3.14159
FIX app_name  BE "My App"

SHOW max_score    NOTE: 100

NOTE: trying to change it causes an error:
MAKE max_score BE 200    NOTE: ERROR! Cannot reassign constant "max_score"
```

> **Best practice:** Use constants for values that should never change, like config settings, limits, or physical constants. It prevents accidental changes later.

---

## 16. Advanced Strings

### Interpolated strings (embed variables inline)

Prefix your string with `$` and wrap variable names in `{ }`:

```
MAKE name  BE "Sam"
MAKE score BE 92

SHOW $"Player {name} scored {score} points."
NOTE: Player Sam scored 92 points.
```

### FORMAT (number formatting)

Control how many decimal places a number shows:

```
MAKE pi BE 3.14159265
SHOW FORMAT pi TO 2      NOTE: 3.14
SHOW FORMAT pi TO 4      NOTE: 3.1416
SHOW FORMAT 1000 TO 0    NOTE: 1000
```

### REPLACE

Replace the first occurrence of a substring:

```
MAKE s BE "I like cats. Cats are cute."
SHOW REPLACE IN s FROM "cats" TO "dogs"
NOTE: I like dogs. Cats are cute.
```

### STARTS WITH / ENDS WITH

```
MAKE filename BE "report.pdf"
SHOW filename ENDS WITH ".pdf"      NOTE: yeah
SHOW filename STARTS WITH "rep"     NOTE: yeah
```

### FITS (regex matching)

Check if text matches a pattern:

```
SHOW "hello123" FITS "\\d+"        NOTE: yeah  (contains digits)
SHOW "abc" FITS "^[a-z]+$"         NOTE: yeah  (only lowercase letters)
SHOW "Hello" FITS "^[a-z]"         NOTE: nah   (doesn't start with lowercase)
```

**Common regex patterns:**

| Pattern | Matches |
|---|---|
| `\\d` | A single digit (0-9) |
| `\\d+` | One or more digits |
| `\\w` | A letter, digit, or underscore |
| `\\s` | A whitespace character |
| `[a-z]` | Any lowercase letter |
| `[A-Z]` | Any uppercase letter |
| `^` | Start of string |
| `$` | End of string |
| `.` | Any single character |
| `+` | One or more of the previous |
| `*` | Zero or more of the previous |
| `?` | Zero or one of the previous |

### Regex helpers (via CALL)

```
MAKE text BE "The price is $42.50 and $9.99"

SHOW CALL regex_test WITH text, "\\$[0-9.]+"
NOTE: yeah  (does it contain a price pattern?)

SHOW CALL regex_find WITH text, "\\$[0-9.]+"
NOTE: $42.50  (first match)

SHOW CALL regex_all WITH text, "\\$[0-9.]+"
NOTE: [$42.50, $9.99]  (all matches)

SHOW CALL regex_replace WITH text, "\\$[0-9.]+", "PRICE"
NOTE: The price is PRICE and PRICE
```

---

## 17. Match (Switch)

`MATCH` is a clean way to check one value against many possible cases — better than stacking `CHECK IF` blocks.

### Basic match

```
MAKE day BE "Monday"
MATCH day {
    IS "Saturday" { SHOW "Weekend!" }
    IS "Sunday"   { SHOW "Weekend!" }
    OTHERWISE     { SHOW "Weekday." }
}
```

### Numeric match with ranges

```
MAKE score BE 85
MATCH score {
    IS AT LEAST 90 { SHOW "A" }
    IS AT LEAST 80 { SHOW "B" }
    IS AT LEAST 70 { SHOW "C" }
    IS AT LEAST 60 { SHOW "D" }
    OTHERWISE      { SHOW "F" }
}
```

### Match with range check

```
MAKE age BE 25
MATCH age {
    IS BETWEEN 0 AND 12   { SHOW "child" }
    IS BETWEEN 13 AND 17  { SHOW "teenager" }
    IS BETWEEN 18 AND 64  { SHOW "adult" }
    OTHERWISE             { SHOW "senior" }
}
```

### Match with comparisons

```
MATCH temperature {
    IS LESS THAN 0      { SHOW "Freezing" }
    IS LESS THAN 15     { SHOW "Cold" }
    IS LESS THAN 25     { SHOW "Comfortable" }
    IS LESS THAN 35     { SHOW "Warm" }
    OTHERWISE           { SHOW "Hot" }
}
```

---

## 18. Error Handling

Programs can encounter errors — a file doesn't exist, a number is divided by zero, invalid input, etc. `TRY` / `CATCH` lets you handle errors gracefully.

### Basic try/catch

```
TRY {
    MAKE result BE 10 DIVIDED BY 0
} CATCH err {
    SHOW "Something went wrong: " AND err
}
```

### Throwing your own errors

Use `THROW` to signal that something went wrong:

```
TEACH check_age USING age {
    CHECK IF age IS LESS THAN 0 {
        THROW "Age cannot be negative"
    }
    GIVE BACK "Age is valid: " AND age
}

TRY {
    SHOW CALL check_age WITH -5
} CATCH err {
    SHOW "Error: " AND err
}
NOTE: Error: Age cannot be negative
```

### Typed errors (catching specific error types)

Use `ERROR "TypeName" WITH message` to create typed errors.
Then catch them selectively with `CATCH "TypeName" e`:

```
TEACH find_user USING id {
    CHECK IF id IS NOT 1 {
        THROW ERROR "NotFound" WITH "no user with id " AND id
    }
    GIVE BACK {id: 1, name: "Alice"}
}

TRY {
    MAKE user BE CALL find_user WITH 99
} CATCH "NotFound" e {
    SHOW "Not found: " AND e GET msg
} CATCH e {
    SHOW "Unexpected error: " AND e
}
```

> **Rule:** More specific CATCH blocks go first. The generic `CATCH e` (no type) always goes last and catches anything not caught above.

### ASSERT (assert a condition is true)

`ASSERT` is a shortcut — it throws an error if a condition is false. Great for sanity checks:

```
MAKE age BE 25
ASSERT age IS MORE THAN 0 ELSE "age must be positive"
SHOW "Age is valid"

NOTE: Catching an assertion failure:
TRY {
    ASSERT age IS MORE THAN 100 ELSE "age must be above 100"
} CATCH "AssertionError" e {
    SHOW "Assertion failed: " AND e GET msg
}
NOTE: Assertion failed: age must be above 100
```

---

## 19. Files and JSON

### Reading files

```
MAKE contents BE READ "my_notes.txt"
SHOW contents
```

### Writing files

```
WRITE "output.txt" WITH "Hello from ypool!\nSecond line."
```

### Checking if a path exists

```
SHOW PATH EXISTS "my_file.txt"    NOTE: yeah or nah
SHOW PATH EXISTS "my_folder"      NOTE: yeah or nah
```

### Listing files in a folder

```
MAKE files BE LIST FILES IN "examples"
SHOW LENGTH OF files    NOTE: how many files
FOR EACH f IN files {
    SHOW f
}
```

### JSON (JavaScript Object Notation)

JSON is a common text format for storing and sharing structured data.

**Parse JSON text into a dict or array:**
```
MAKE json_text BE '{"name": "Alice", "score": 95}'
MAKE data BE PARSE JSON json_text
SHOW data GET name     NOTE: Alice
SHOW data GET score    NOTE: 95
```

**Convert a dict or array back to JSON text:**
```
MAKE person BE {name: "Alice", age: 17}
MAKE json_text BE DUMP JSON person
SHOW json_text
NOTE: {
NOTE:   "name": "Alice",
NOTE:   "age": 17
NOTE: }
```

**Load a JSON file:**
```
MAKE text BE READ "data.json"
MAKE data BE PARSE JSON text
SHOW data GET users AT 0 GET name
```

**Save a dict to a JSON file:**
```
MAKE record BE {score: 100, player: "loopy"}
WRITE "scores.json" WITH DUMP JSON record
```

---

## 20. Dates and Time

```
SHOW TODAY    NOTE: 2025-04-20  (current date as text: YYYY-MM-DD)
SHOW NOW      NOTE: 2025-04-20 14:32:05  (date and time)
```

---

## 21. Math Builtins

### Trig functions (use radians)

```
SHOW SIN OF 0      NOTE: 0.0
SHOW COS OF 0      NOTE: 1.0
SHOW TAN OF 0      NOTE: 0.0

NOTE: convert degrees to radians first:
MAKE deg BE 90
MAKE rad BE deg TIMES PI DIVIDED BY 180
SHOW FORMAT SIN OF rad TO 4    NOTE: 1.0000
```

### Logarithm

```
SHOW LOG OF 1     NOTE: 0.0     (natural log, base e)
SHOW LOG OF 100   NOTE: 4.605...
```

### Math constants

```
SHOW FORMAT PI TO 6    NOTE: 3.141593
SHOW FORMAT E TO 6     NOTE: 2.718282
```

### Random numbers

```
MAKE r BE RANDOM                   NOTE: random float between 0.0 and 1.0
MAKE n BE RANDOM FROM 1 TO 100    NOTE: random whole number between 1 and 100
```

---

## 22. Array Power Tools

These tools let you transform, filter, and combine arrays without writing loops yourself.

### MAP — transform every item

`MAP arr USING fn` runs a function on every item and returns a new array of results:

```
TEACH double USING x { GIVE BACK x TIMES 2 }

MAKE nums   BE [1, 2, 3, 4, 5]
MAKE doubled BE MAP nums USING double
SHOW doubled    NOTE: [2, 4, 6, 8, 10]
```

### FILTER — keep only matching items

`FILTER arr WHERE fn` keeps only items where the function returns YEAH:

```
TEACH is_big USING x { GIVE BACK x IS MORE THAN 3 }

MAKE nums   BE [1, 2, 3, 4, 5, 6]
MAKE big    BE FILTER nums WHERE is_big
SHOW big    NOTE: [4, 5, 6]
```

### REDUCE — combine all items into one value

`REDUCE arr USING fn START initial` applies a function left-to-right, accumulating a result:

```
TEACH add USING acc, x { GIVE BACK acc PLUS x }

MAKE nums  BE [1, 2, 3, 4, 5]
MAKE total BE REDUCE nums USING add START 0
SHOW total    NOTE: 15
```

### FIND — find the first matching item

```
TEACH is_adult USING p { GIVE BACK p GET age IS AT LEAST 18 }

MAKE people BE [{name: "Alice", age: 17}, {name: "Bob", age: 20}]
MAKE adult  BE FIND IN people WHERE is_adult
SHOW adult GET name    NOTE: Bob
```

### FIND ALL — find all matching items

```
MAKE nums     BE [1, 5, 2, 8, 3, 7]
TEACH is_big  USING x { GIVE BACK x IS MORE THAN 4 }
MAKE big_ones BE FIND ALL IN nums WHERE is_big
SHOW big_ones    NOTE: [5, 8, 7]
```

### PIPE — chain operations

`PIPE` lets you pass an array through a series of operations, left to right.
This is like building an assembly line for your data:

```
MAKE scores BE [45, 92, 67, 88, 23, 99, 55]
TEACH is_passing USING s { GIVE BACK s IS AT LEAST 60 }
TEACH to_grade   USING s { GIVE BACK IF s IS AT LEAST 90 THEN "A" ELSE "B" }

MAKE grades BE scores
    PIPE FILTER WHERE is_passing
    PIPE MAP USING to_grade

SHOW grades    NOTE: [B, B, A, B]
```

`PIPE` supports: `MAP USING fn`, `FILTER WHERE fn`, `REDUCE USING fn START val`,
`UNIQUE`, `FLATTEN`, `TALLY`, `GROUP BY fn`.

---

## 23. New Array Tools

### UNIQUE — remove duplicates

```
MAKE nums BE [1, 2, 3, 2, 1, 4, 3]
SHOW UNIQUE OF nums    NOTE: [1, 2, 3, 4]
```

### FLATTEN — un-nest one level of arrays

```
MAKE nested BE [[1, 2], [3, 4], [5]]
SHOW FLATTEN nested    NOTE: [1, 2, 3, 4, 5]
```

### ZIP — pair up two arrays

```
MAKE names  BE ["Alice", "Bob", "Carol"]
MAKE scores BE [95, 87, 92]
MAKE paired BE ZIP names WITH scores
SHOW paired    NOTE: [[Alice, 95], [Bob, 87], [Carol, 92]]
```

### TALLY — count occurrences

Returns a dict showing how many times each value appeared:

```
MAKE votes BE ["red", "blue", "red", "green", "blue", "red"]
SHOW TALLY OF votes
NOTE: {red: 3, blue: 2, green: 1}
```

### CLAMP — pin a number to a range

```
SHOW CLAMP 150 FROM 0 TO 100    NOTE: 100  (too high, clamped to max)
SHOW CLAMP -5  FROM 0 TO 100    NOTE: 0    (too low, clamped to min)
SHOW CLAMP 42  FROM 0 TO 100    NOTE: 42   (already in range)
```

Great for things like health bars, volume sliders, or any value with limits.

### GROUP — group items by a key

Returns a dict where each key is a group and its value is an array of matching items:

```
MAKE words BE ["apple", "ant", "bear", "avocado", "banana"]
TEACH first_letter USING w { GIVE BACK SLICE w FROM 0 TO 1 }
MAKE grouped BE GROUP words BY first_letter

SHOW grouped GET a    NOTE: [apple, ant, avocado]
SHOW grouped GET b    NOTE: [bear, banana]
```

---

## 24. Partial Functions and Memoize

### PARTIAL — pre-fill arguments

`PARTIAL fn WITH arg` creates a new function with some arguments already filled in:

```
TEACH multiply USING a, b { GIVE BACK a TIMES b }

MAKE double BE PARTIAL multiply WITH 2
MAKE triple BE PARTIAL multiply WITH 3

SHOW CALL double WITH 7    NOTE: 14
SHOW CALL triple WITH 7    NOTE: 21
```

Think of it as making a specialized version of a general function.

### MEMOIZE — cache results

`MEMOIZE fn AS name` wraps a function so it remembers past results.
If you call it with the same arguments twice, it returns the cached answer instantly:

```
TEACH fib USING n {
    CHECK IF n IS AT MOST 1 { GIVE BACK n }
    GIVE BACK (CALL fib WITH n MINUS 1) PLUS (CALL fib WITH n MINUS 2)
}

NOTE: Replace fib with a cached version
NOTE: (same name so recursive calls also hit the cache)
MEMOIZE fib AS fib
SHOW CALL fib WITH 30    NOTE: fast! (832040)
```

> **Key tip:** `MEMOIZE fib AS fib` (same name) is needed for recursive memoization.
> When `fib` calls itself, it looks up `fib` in memory — and now finds the cached version.

---

## 25. Importing Libraries

Split your code across multiple files and reuse it anywhere.

### BRING IN (import a file)

```
BRING IN "helpers.yp"        NOTE: exact path
BRING IN "utils"             NOTE: ypool auto-adds .yp extension
BRING IN "arrays"            NOTE: searches lib/ folder automatically
```

**Where ypool looks for files (in order):**

1. The exact path you gave
2. Same path with `.yp` added
3. `lib/` folder (relative to where you ran ypool)
4. `lib/` folder next to the ypool interpreter
5. `~/.ypool/lib/` (your personal library folder)
6. Any folder in the `YPOOL_PATH` environment variable

### BRING IN AS (namespace import)

Load a file's contents into a named dict so names don't clash:

```
BRING IN "arrays" AS arr
BRING IN "strings" AS str

SHOW CALL arr GET chunk WITH [1, 2, 3, 4, 5, 6], 2
NOTE: [[1, 2], [3, 4], [5, 6]]

SHOW CALL str GET pad_left WITH "42", 6, "0"
NOTE: 000042
```

### Creating your own library

Just write a `.yp` file with `TEACH` definitions:

```
NOTE: my_tools.yp

TEACH clamp_score USING s {
    GIVE BACK CLAMP s FROM 0 TO 100
}

TEACH letter_grade USING s {
    MATCH s {
        IS AT LEAST 90 { GIVE BACK "A" }
        IS AT LEAST 80 { GIVE BACK "B" }
        IS AT LEAST 70 { GIVE BACK "C" }
        OTHERWISE      { GIVE BACK "F" }
    }
}
```

Then use it:

```
BRING IN "my_tools"

SHOW CALL clamp_score WITH 115       NOTE: 100
SHOW CALL letter_grade WITH 87       NOTE: B
```

---

## 26. Using Python Libraries (Bridge)

`BRIDGE` imports any installed Python module and makes it usable from ypool.

```
BRIDGE "math" AS m

SHOW CALL m GET sqrt WITH 144        NOTE: 12.0
SHOW CALL m GET factorial WITH 7     NOTE: 5040
SHOW m GET pi                        NOTE: 3.141592653589793
```

```
BRIDGE "random" AS rng

MAKE lucky BE CALL rng GET randint WITH 1, 100
SHOW "Your lucky number: " AND lucky
```

```
BRIDGE "os.path" AS path

SHOW CALL path GET join WITH "examples", "hello.yp"
NOTE: examples\hello.yp  (or examples/hello.yp on Mac/Linux)

SHOW CALL path GET exists WITH "examples"
NOTE: yeah
```

> **Tip:** Any pip-installed package works. `BRIDGE "numpy" AS np`, `BRIDGE "requests" AS req`, etc.

**Calling bridged functions:**

- `CALL module GET function_name WITH arg1, arg2` — pass arguments
- `module GET attribute` — read a constant/property (no CALL needed)

---

## 27. The Standard Library

Import these built-in libraries with `BRING IN`:

---

### `BRING IN "arrays"`

| Function | Usage | What it does |
|---|---|---|
| `chunk` | `CALL chunk WITH arr, 3` | Splits array into chunks of size n |
| `compact` | `CALL compact WITH arr` | Removes NOTHING, NAH, 0, "" |
| `sum_arr` | `CALL sum_arr WITH arr` | Sum of all numbers |
| `max_of` | `CALL max_of WITH arr` | Largest value |
| `min_of` | `CALL min_of WITH arr` | Smallest value |
| `flatten_deep` | `CALL flatten_deep WITH arr` | Recursively flattens all nesting |
| `range` | `CALL range WITH 1, 10` | Creates `[1, 2, 3, ..., 10]` |
| `includes` | `CALL includes WITH arr, val` | Is val in arr? |
| `index_of` | `CALL index_of WITH arr, val` | First index of val, or -1 |
| `zip_with` | `CALL zip_with WITH a, b, fn` | Pairs + transforms two arrays |

---

### `BRING IN "strings"`

| Function | Usage | What it does |
|---|---|---|
| `pad_left` | `CALL pad_left WITH "7", 3, "0"` | `"007"` — pad to width on left |
| `pad_right` | `CALL pad_right WITH "hi", 5, "-"` | `"hi---"` — pad to width on right |
| `repeat_str` | `CALL repeat_str WITH "ab", 3` | `"ababab"` |
| `title_case` | `CALL title_case WITH "hello world"` | `"Hello World"` |
| `truncate` | `CALL truncate WITH s, 20, "..."` | Shortens long strings |
| `count_occurrences` | `CALL count_occurrences WITH s, sub` | How many times sub appears |
| `is_numeric` | `CALL is_numeric WITH "3.14"` | Is it a valid number? |
| `lines` | `CALL lines WITH text` | Splits text into array of lines |
| `str_starts` | `CALL str_starts WITH s, prefix` | Does s start with prefix? |
| `str_ends` | `CALL str_ends WITH s, suffix` | Does s end with suffix? |

---

### `BRING IN "math"`

| Name / Function | Usage | What it does |
|---|---|---|
| `TAU` | `SHOW TAU` | 2π ≈ 6.283 |
| `PHI` | `SHOW PHI` | Golden ratio ≈ 1.618 |
| `lerp` | `CALL lerp WITH 0, 100, 0.5` | Linear interpolation → 50 |
| `to_rad` | `CALL to_rad WITH 90` | Degrees → radians |
| `to_deg` | `CALL to_deg WITH 1.5708` | Radians → degrees |
| `is_even` | `CALL is_even WITH 4` | YEAH if even |
| `is_odd` | `CALL is_odd WITH 3` | YEAH if odd |
| `sign` | `CALL sign WITH -5` | -1, 0, or 1 |
| `factorial` | `CALL factorial WITH 6` | 720 |
| `fibonacci` | `CALL fibonacci WITH 10` | 55 |
| `gcd` | `CALL gcd WITH 48, 18` | Greatest common divisor → 6 |
| `lcm` | `CALL lcm WITH 4, 6` | Least common multiple → 12 |
| `percent` | `CALL percent WITH 3, 12` | 25.0 (percent of total) |
| `distance` | `CALL distance WITH 0, 0, 3, 4` | Euclidean distance → 5 |

---

## 28. The REPL

The **REPL** (Read-Eval-Print Loop) is an interactive shell where you type code and see results immediately. Start it with:

```bash
python ypool.py
```

### REPL commands

| Command | What it does |
|---|---|
| `:help` | Show all REPL commands |
| `:vars` | List all variables you've defined (with types and values) |
| `:type name` | Show the type of a specific variable |
| `:clear` | Wipe everything and start fresh |
| `:run filename.yp` | Load and run a file into the current session |
| `:save filename.yp` | Save everything you've typed to a file |
| `:history` | Show recent commands |
| `:history 10` | Show last 10 commands |
| `:quit` | Exit the REPL |

### Multi-line input

The REPL automatically detects when you have unclosed braces `{ }` and waits for you to finish:

```
ypool> TEACH greet USING name {
  ...>     SHOW "Hello, " AND name
  ...> }
ypool> CALL greet WITH "world"
Hello, world
```

### Expression mode

Just type an expression — no SHOW needed — and it prints the result with `=>`:

```
ypool> 2 PLUS 2
=> 4
ypool> "hello" AND " world"
=> hello world
ypool> LENGTH OF [1, 2, 3, 4]
=> 4
```

### Tab completion

Press `Tab` to auto-complete keywords and variable names:

```
ypool> SHO[Tab]  →  SHOW 
ypool> my_sc[Tab]  →  my_score  (if you defined it)
```

### History

Use the **Up arrow** to recall previous commands. Your history is saved between sessions in `~/.ypool_history`.

---

## 29. Full Examples

### FizzBuzz

```
COUNT FROM 1 TO 30 AS n {
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

### Guessing game

```
FIX secret BE RANDOM FROM 1 TO 100
MAKE tries  BE 0
MAKE guessed BE NAH

KEEP GOING WHILE NOT guessed {
    MAKE input BE ASK "Guess (1-100): "
    MAKE guess BE CALL asNumber WITH input
    MAKE tries BE tries PLUS 1

    CHECK IF guess IS secret {
        SHOW "Correct! You got it in " AND tries AND " tries."
        MAKE guessed BE YEAH
    } OTHERWISE {
        CHECK IF guess IS LESS THAN secret {
            SHOW "Too low!"
        } OTHERWISE {
            SHOW "Too high!"
        }
    }
}
```

### Student grade reporter

```
MAKE students BE [
    {name: "Alice", scores: [90, 85, 92]},
    {name: "Bob",   scores: [72, 68, 75]},
    {name: "Carol", scores: [95, 98, 97]}
]

TEACH letter_grade USING avg {
    CHECK IF avg IS AT LEAST 90 { GIVE BACK "A" }
    CHECK IF avg IS AT LEAST 80 { GIVE BACK "B" }
    CHECK IF avg IS AT LEAST 70 { GIVE BACK "C" }
    GIVE BACK "F"
}

FOR EACH student IN students {
    MAKE avg BE AVERAGE OF student GET scores
    MAKE grade BE CALL letter_grade WITH avg
    SHOW $"{student GET name}: avg={FORMAT avg TO 1} grade={grade}"
}
```

Output:
```
Alice: avg=89.0 grade=B
Bob: avg=71.7 grade=C
Carol: avg=96.7 grade=A
```

### Word frequency counter

```
MAKE text BE "the cat sat on the mat the cat"
MAKE words BE SPLIT text BY " "
MAKE freq BE TALLY OF words

FOR EACH word IN KEYS OF freq {
    SHOW word AND ": " AND freq GET word
}
```

### Fibonacci with memoization

```
TEACH fib USING n {
    CHECK IF n IS AT MOST 1 { GIVE BACK n }
    GIVE BACK (CALL fib WITH n MINUS 1) PLUS (CALL fib WITH n MINUS 2)
}
MEMOIZE fib AS fib    NOTE: replace fib with a cached version

NOTE: Now fib(40) runs instantly instead of taking seconds
SHOW CALL fib WITH 40    NOTE: 102334155
```

### Simple to-do list (file-backed)

```
MAKE todo_file BE "todos.txt"

TEACH load_todos {
    CHECK IF PATH EXISTS todo_file {
        MAKE contents BE READ todo_file
        MAKE lines BE SPLIT contents BY "\n"
        GIVE BACK FILTER lines WHERE TEACH _nonempty USING l { GIVE BACK NOT l IS "" }
    }
    GIVE BACK []
}

TEACH save_todos USING todos {
    WRITE todo_file WITH JOIN todos BY "\n"
}

TEACH add_todo USING text {
    MAKE todos BE CALL load_todos
    PUSH text INTO todos
    CALL save_todos WITH todos
    SHOW "Added: " AND text
}

TEACH list_todos {
    MAKE todos BE CALL load_todos
    CHECK IF LENGTH OF todos IS 0 {
        SHOW "No todos yet!"
    } OTHERWISE {
        MAKE i BE 1
        FOR EACH item IN todos {
            SHOW i AND ". " AND item
            MAKE i BE i PLUS 1
        }
    }
}

CALL add_todo WITH "Learn ypool"
CALL add_todo WITH "Build something cool"
CALL list_todos
```

### HTTP fetch

```
TRY {
    MAKE response BE FETCH "https://api.github.com/repos/python/cpython" AS JSON
    SHOW "Stars: " AND response GET stargazers_count
    SHOW "Language: " AND response GET language
} CATCH err {
    SHOW "Fetch failed: " AND err
}
```

### Using the Python math bridge

```
BRIDGE "math" AS m

MAKE angles BE [0, 30, 45, 60, 90]
FOR EACH deg IN angles {
    MAKE rad BE CALL m GET radians WITH deg
    MAKE s BE FORMAT CALL m GET sin WITH rad TO 4
    SHOW deg AND "° → sin = " AND s
}
```

---

## 30. Quick Reference Cheat Sheet

### Variables

```
MAKE x BE 42               ← create / update variable
FIX pi BE 3.14             ← constant (cannot change)
```

### Output / Input

```
SHOW "hello"               ← print
SHOW $"hi {name}"          ← interpolated print
MAKE x BE ASK "prompt: "  ← read input
```

### Types

```
YEAH  NAH  NOTHING
"text"  42  3.14
[1, 2, 3]  {key: value}
KIND OF x → "text" | "number" | "bool" | "nothing" | "array" | "dict" | "function" | "bridge"
```

### Arithmetic

```
PLUS  MINUS  TIMES  DIVIDED BY  MOD  POWER
FLOOR OF  CEIL OF  ROUND OF  SQRT OF  ABS OF
LOG OF  SIN OF  COS OF  TAN OF  PI  E
```

### Comparison

```
IS  IS NOT  IS MORE THAN  IS LESS THAN  IS AT LEAST  IS AT MOST
IS BETWEEN a AND b  IS NOTHING  IS NOT NOTHING
CONTAINS  STARTS WITH  ENDS WITH  FITS "pattern"
```

### Logic

```
ALSO  OR  NOT
EITHER x OR fallback         ← null coalescing
IF cond THEN val ELSE other  ← ternary
```

### Control flow

```
CHECK IF cond { } OTHERWISE { }
MATCH val { IS x { } OTHERWISE { } }
KEEP GOING WHILE cond { }
COUNT FROM n TO m AS i { }
FOR EACH item IN list { }
REPEAT n { }  |  REPEAT n AS i { }
STOP  SKIP
```

### Functions

```
TEACH name USING a, b DEFAULT val { GIVE BACK ... }
CALL name WITH arg1, arg2
PARTIAL fn WITH pre_arg         ← partial application
MEMOIZE fn AS cached_name       ← cache results
```

### Arrays

```
[1, 2, 3]  arr AT i  arr AT -1  LENGTH OF arr
PUSH val INTO arr    POP FROM arr
UPDATE arr AT i TO val    REMOVE arr AT i
SORT arr    SORT arr BY field    REVERSE arr
SLICE arr FROM a TO b    arr CONTAINS val
JOIN arr BY sep    [...arr1, ...arr2]    MAKE [a,b,c] FROM arr
FIRST OF arr    LAST OF arr    TOTAL OF arr    AVERAGE OF arr
UNIQUE OF arr    FLATTEN arr    ZIP a WITH b
TALLY OF arr    GROUP arr BY fn    CLAMP n FROM lo TO hi
MAP arr USING fn    FILTER arr WHERE fn    REDUCE arr USING fn START val
FIND IN arr WHERE fn    FIND ALL IN arr WHERE fn
arr PIPE MAP USING fn PIPE FILTER WHERE fn
```

### Dicts

```
{key: val}    obj GET key    obj GET key ELSE fallback
UPDATE obj key TO val    HAS obj key
KEYS OF obj    VALUES OF obj    LENGTH OF obj    MERGE a WITH b
MAKE {a, b} FROM obj    MAKE obj AT key BE val
```

### Strings

```
LENGTH OF s    UPCASE OF s    DOWNCASE OF s    TRIM s
SPLIT s BY sep    REPLACE IN s FROM old TO new
SLICE s FROM a TO b    FORMAT n TO digits
CALL regex_find WITH s, pattern    CALL regex_all WITH s, pattern
CALL regex_replace WITH s, pattern, replacement
```

### Error handling

```
TRY { } CATCH e { }
TRY { } CATCH "TypeName" e { } CATCH e { }
THROW value
THROW ERROR "TypeName" WITH message
ASSERT cond ELSE "message"
```

### Files / JSON / Net

```
READ "file.txt"    WRITE "file.txt" WITH content
PATH EXISTS "path"    LIST FILES IN "dir"
PARSE JSON text    DUMP JSON value
FETCH "url"    FETCH "url" AS JSON
TODAY    NOW
```

### Imports

```
BRING IN "file"            ← imports into current scope
BRING IN "arrays" AS arr   ← imports into named namespace
BRIDGE "math" AS m         ← wraps Python module
CALL m GET fn WITH args    ← call bridged function
m GET constant             ← read bridged value
```

### Misc

```
NOTE: this is a comment
EXISTS varname → YEAH/NAH   (check if variable is defined)
CALL asNumber WITH "42"     → 42
CALL asText WITH 99         → "99"
CALL max WITH a, b          CALL min WITH a, b
CALL sum WITH [1,2,3]
```

---

*That's everything. You now know ypool inside and out.*
*Build something cool!*
