---
title: Python
summary: Python — environments, language core, typing, pathlib, async, testing
tags: [python, language, tooling]
tooling: [python, uv, ruff, pytest]
verified_on: 2026-11-10
verified_env: Python 3.14.9, uv 0.13.7, Linux
status: verified
---

# Python

The 2021 version of this sheet taught `pip install --user`, `virtualenv` and `tox`.
All three still exist; none of them is what you should reach for. The current idiom is
`uv` for environments and dependencies, `ruff` for lint and format, and `pytest` for
tests. Everything below was executed on Python 3.14.9.

## Environments and dependency management

```bash
uv venv                      # create .venv in the current directory
source .venv/bin/activate
uv pip install requests      # fast pip, same semantics
uv add requests              # add to pyproject.toml and the lock file
uv run pytest                # run inside the project environment without activating
uv sync                      # reproduce the locked environment exactly
uv python list               # interpreters uv can use or install
```

`uv run` is the one worth adopting first: it removes the entire class of "it works in
my shell but not in cron" failures.

## Strings

```python
name, port = "host1", 22
print(f"{name}:{port}")                 # f-string, the default since 3.6
print(f"{name=} {port=}")               # debug form: host1='host1' port=22
print(f"{3.14159:.2f}")                 # format spec inside the braces
print(f"{name:>10}")                    # right-align in 10 columns

text = """
multi-line text keeps its newlines
"""
parts = "a,b,c".split(",")
joined = "-".join(parts)
```

## Collections

```python
items = ["a", "b", "a"]
counts = {}
for item in items:
    counts[item] = counts.get(item, 0) + 1

from collections import Counter, defaultdict
Counter(items)                      # Counter({'a': 2, 'b': 1})
Counter(items).most_common(1)       # [('a', 2)]

buckets = defaultdict(list)
buckets["x"].append(1)              # no KeyError on first write

pairs = dict(zip(["a", "b"], [1, 2]))
for key, value in pairs.items():
    print(key, value)
```

Comprehensions, and the one case where a loop is better:

```python
squares = [n * n for n in range(5)]
evens = {n for n in range(10) if n % 2 == 0}
by_len = {w: len(w) for w in ["ab", "abc"]}
# side effects do not belong in a comprehension; use a loop
```

## Functions

```python
def connect(host: str, port: int = 22, *, timeout: float = 5.0) -> str:
    """Keyword-only after the *, which prevents positional mistakes."""
    return f"{host}:{port} timeout={timeout}"

def total(*values: float, **options: object) -> float:
    return sum(values)

square = lambda n: n * n            # fine for a one-liner, a def otherwise
```

## Typing

Type hints are documentation the interpreter can check:

```python
from typing import Iterable

def names(rows: Iterable[dict[str, object]]) -> list[str]:
    return [str(r["name"]) for r in rows]

Point = tuple[float, float]

def midpoint(a: Point, b: Point) -> Point:
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
```

Built-in generics (`list[str]`, `dict[str, int]`) replaced `typing.List` and
`typing.Dict` in 3.9. `ruff` and `mypy` both consume these.

## Dataclasses

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Interface:
    name: str
    mtu: int = 1500
    tags: list[str] = field(default_factory=list)

eth0 = Interface("eth0")
print(eth0)                          # free __repr__, __eq__, and a frozen instance
```

## Paths

`pathlib` replaces string concatenation and most of `os.path`:

```python
from pathlib import Path
import tempfile

base = Path("/var/log")
for entry in base.glob("*.log"):     # read side works as an ordinary user
    print(entry.name, entry.stat().st_size)

work = Path(tempfile.gettempdir()) / "demo-app"
target = work / "app" / "app.log"    # the / operator joins paths
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("done\n", encoding="utf-8")
print(target.read_text(encoding="utf-8").strip())
```

## Exceptions

```python
try:
    value = int("not a number")
except ValueError as exc:
    print(f"bad input: {exc}")
else:
    print("parsed", value)
finally:
    print("always runs")
```

Catch the narrowest exception that makes sense. `except Exception: pass` hides bugs;
`except (ValueError, KeyError)` states what you expect.

## subprocess

```python
import subprocess

result = subprocess.run(
    ["ip", "-brief", "addr"],
    capture_output=True, text=True, check=False, timeout=10,
)
if result.returncode != 0:
    raise RuntimeError(result.stderr.strip())
print(result.stdout)
```

Pass a list, never a shell string, unless you actually need shell features. If you do,
`shell=True` with user input is a command-injection hole.

## asyncio

```python
import asyncio

async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} done"

async def main() -> None:
    results = await asyncio.gather(
        fetch("a", 0.2), fetch("b", 0.1), fetch("c", 0.05)
    )
    print(results)

asyncio.run(main())
```

`asyncio.run` owns the loop; do not create loops by hand inside application code.

## JSON

```python
import json

data = json.loads('{"name": "host1", "port": 22}')
print(data["name"], data["port"])

with open("/tmp/example.json", "w", encoding="utf-8") as handle:
    json.dump(data, handle, indent=2)
```

## Testing

```bash
uv add --dev pytest
uv run pytest -q
uv run pytest -q -k 'parse and not slow' --maxfail=1
```

```python
# tests/test_parse.py
def test_parse_rejects_garbage() -> None:
    import pytest
    with pytest.raises(ValueError):
        int("nope")
```

## Lint and format

```bash
uv add --dev ruff
uv run ruff check .          # lint
uv run ruff check --fix .    # apply safe fixes
uv run ruff format .         # format (Black-compatible)
```

## Project layout

```toml
# pyproject.toml
[project]
name = "example"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["requests>=2.32"]

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]
```

```text
project/
├── pyproject.toml
├── src/example/__init__.py
└── tests/test_example.py
```

## Traps worth remembering

- Mutable default arguments: `def f(x, acc=[])` shares one list across calls. Use
  `None` and create inside.
- `is` compares identity, `==` compares value. `is` is for `None`, `True`, `False`.
- Late binding in closures and loops: `[lambda: i for i in range(3)]` returns three
  three's. Bind with `lambda i=i: i`.
- `except Exception` around a whole `main()` hides the traceback you need.
