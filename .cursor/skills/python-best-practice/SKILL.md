---
name: python-best-practice
description: >-
  Enforces Python style for docstrings, comments, 88-character line length, and
  modularity. Use when writing, reviewing, or refactoring Python in this repo,
  or when the user mentions PEP 8, Google-style docstrings, or Python code quality.
---

# Python Best Practice

Apply these rules whenever writing, reviewing, or modifying Python code in this project.

## Docstrings

- Every public module, class, and function **must** have a docstring.
- Use Google-style docstrings (or NumPy/Sphinx if the project already uses another convention).
- Include a one-line summary, then a blank line, then arguments, returns, and raises.
- Private functions and methods need at least a one-line docstring when logic is non-trivial.

## Comments

- Explain *why* the code exists, not *what* it does.
- Avoid trivial comments like `# increment i`.
- Keep comments short. For multi-line comments, use `#` on each line.
- Remove commented-out code entirely.

## Line length

- Hard limit **88 characters** per line (PEP 8).
- Break long lines into meaningful parts.
- Prefer parentheses for implicit continuation over backslashes.
- Break long strings with implicit concatenation or `textwrap`.

## Modularity

- Functions do **one thing** and stay small enough to fit on a screen.
- Each module has a clear purpose; split when a file grows beyond ~400 lines.
- Import only what you need; avoid `from x import *`.
- Group imports: standard library, third-party, then local, with blank lines between groups.
- Prefer classes for related state and behavior; avoid deep inheritance.

## Clarifications

If the project already uses a different docstring style (e.g. reStructuredText) or `.editorconfig` overrides line length, follow the existing project convention instead of these defaults.
