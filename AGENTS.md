# AGENTS.md

## Cursor Cloud specific instructions

This repo is a small Python 3 learning project (Chinese tutorial notes). Each `dayN.py` /
`day10/day10.py` is a standalone script you run directly with `python3`. There is no test
framework, no linter config, and no build step; "running the app" means executing a script.

- Python: uses the system `python3` (3.12). No virtualenv is required.
- Only third-party dependency is `requests` (imported in `day10/day10.py`). Install/refresh it with `pip3 install requests` (handled by the startup update script).
- Syntax/lint sanity check for all scripts: `python3 -m py_compile *.py day10/day10.py test1/__init__.py day10/test/__init__.py`.
- `day10/day10.py` hardcodes a macOS path (`/Users/apple/Work/learn_py`) and then does `import test1`. That path does not exist here, so run it from the repo root with the repo root on the path: `PYTHONPATH="$PWD" python3 day10/day10.py`. It also performs a live network GET to `https://www.baidu.com` and prints the status code.
- `day2.py` and `day4.py` call `input()` and block on stdin. Pipe input when running non-interactively, e.g. `echo "Felix" | python3 day2.py`. (`day4.py` also has a pre-existing Python 3 bug comparing a `str` to an `int`.)
