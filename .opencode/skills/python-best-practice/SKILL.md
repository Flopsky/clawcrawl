---
name: python-best-practice
description: >
  Enforce Python best practices: docstrings for all public modules/classes/functions,
  concise comments explaining "why" rather than "what", maximum line length of 88
  characters (PEP 8), and strict modularity (small functions, single-responsibility,
  logical file boundaries).
license: MIT
compatibility: opencode
metadata:
  audience: developers
  language: python
---

## What I do

When you ask me to write, review, or modify Python code, I apply these rules:

### Docstrings

- Every public module, class, and function **must** have a docstring.
- Use Google-style docstrings (or NumPy/Sphinx if the project convention is already set).
- Include a one-line summary, then a blank line, then details of arguments, returns, and raises.
- Private functions and methods should have at least a one-line docstring when the logic is non-trivial.

### Comments

- Write comments that explain *why* the code exists, not *what* it does.
- Avoid trivial comments like `# increment i`.
- Keep comments short and to the point. If a comment spans multiple lines, use `#` on each line.
- Remove commented‑out code entirely.

### Line length

- Hard limit **88 characters** per line (PEP 8 – allows slightly more than 79 for readability).
- If a line exceeds 88 characters, break it into meaningful parts.
- Prefer parentheses for implicit line continuation over backslashes.
- Break long strings with implicit concatenation or `textwrap`.

### Modularity

- Functions should do **one thing** and be small enough to fit on a screen.
- A module should have a clear purpose; refactor it into multiple modules when it grows beyond ~400 lines.
- Import only what you need; avoid wildcard (`from x import *`).
- Group imports: standard library, third‑party, then local, each group separated by a blank line.
- Prefer classes for grouping related state and behavior, but avoid deep inheritance.

## When to use me

Use this skill when working on any Python codebase where you want to maintain a consistent, high‑quality style. It works for both new code and refactoring existing code.

I will ask clarifying questions if the project already uses a different docstring style (e.g., reStructuredText) or has an explicit `.editorconfig` that overrides line length.
