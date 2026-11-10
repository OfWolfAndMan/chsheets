# Notebooks

Seven notebooks from the 2018–2021 pandas and Python study notes, plus the CSV fixture
they use.

| Notebook | Covers |
|---|---|
| `Basics.ipynb` | Python basics in notebook form |
| `Advanced Lists.ipynb` | list operations |
| `Advanced Dictionaries.ipynb` | dict patterns |
| `Optimizations.ipynb` | small performance habits |
| `Useful_functions.ipynb` | the largest of the set: assorted helper functions |
| `Regex.ipynb` | regular expressions |
| `Pandas Examples.ipynb` | pandas recipes against `devices.csv` |

## Status

Unverified. None of these has been executed since 2021, and no environment is pinned.
All stored outputs and execution counts were stripped on 2026-11-10: committed output
is a claim about a run that nobody can now reproduce or contradict, and it carried
local paths, tracebacks and private addresses into the public tree.

If you want to use them:

```bash
uv run --with jupyter --with pandas jupyter lab
```

and clear the outputs before committing a change:

```bash
jupyter nbconvert --clear-output --inplace *.ipynb
```
