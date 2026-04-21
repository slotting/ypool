# ypool Language Support

VS Code extension for **ypool** (`.yp` files).

## Features

- **Syntax highlighting** — keywords, strings, numbers, comments, functions, and variables are all coloured.
- **Live error squiggles** — the ypool lexer and parser run in the background; red underlines appear the moment a syntax error is introduced.
- **Hover documentation** — hover over any keyword (MAKE, TEACH, CALL, …) to see a short description and usage example.

---

## Quick install — highlighting only

No `npm` or Python dependencies needed for this path.

1. Copy the entire `vscode-extension/` folder into your VS Code extensions directory:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\ypool-language-1.0.0`
   - **macOS / Linux**: `~/.vscode/extensions/ypool-language-1.0.0`
2. Restart VS Code (or run **Developer: Reload Window** from the Command Palette).
3. Open any `.yp` file — syntax highlighting is active immediately.

---

## Full install — highlighting + live error checking + hover docs

This requires Node.js, npm, and Python with `pygls` installed.

### 1. Install Python dependencies

```bash
pip install pygls
```

### 2. Install Node dependencies

Inside the extension folder:

```bash
npm install
```

### 3. Copy to VS Code extensions

```
cp -r vscode-extension/ ~/.vscode/extensions/ypool-language-1.0.0
```

(Windows: copy the folder to `%USERPROFILE%\.vscode\extensions\ypool-language-1.0.0`)

### 4. Reload VS Code

Run **Developer: Reload Window** from the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`).

---

## Settings

| Setting | Default | Description |
|---|---|---|
| `ypool.pythonPath` | `"python"` | Path to the Python executable used to run the language server. Set this if `python` is not on your PATH or you want to use a specific virtual environment, e.g. `"C:/venv/Scripts/python.exe"` or `"/usr/bin/python3"`. |

Add to your VS Code `settings.json`:

```json
{
  "ypool.pythonPath": "/usr/bin/python3"
}
```

---

## Known limitation — AWAIT ALL / AWAIT RACE lists

The ypool parser currently handles one expression per `AWAIT` call. When you need to await multiple coroutines in parallel, assign each coroutine call to a variable first, then pass those variables:

```ypool
NOTE: Correct pattern
MAKE taskA BE CALL fetchUser WITH 1
MAKE taskB BE CALL fetchUser WITH 2
MAKE results BE AWAIT ALL [taskA taskB]

NOTE: This may not parse correctly — avoid
MAKE results BE AWAIT ALL [CALL fetchUser WITH 1  CALL fetchUser WITH 2]
```

This applies equally to `AWAIT RACE`.
