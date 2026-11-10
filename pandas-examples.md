---
title: pandas
summary: pandas 2.x — loading, selecting, grouping, joining, time series
tags: [python, data, pandas]
tooling: [python, pandas]
verified_on: 2026-11-10
verified_env: Python 3.14.9, pandas 2.x via uv
status: verified
---

# pandas

Executed against pandas 2.x on Python 3.14. The 2021 version of this sheet used
`df.append`, `inplace=True` everywhere, and `.ix` — all removed or discouraged. The
replacements are below.

## Load and inspect

```python
import pandas as pd

df = pd.read_csv("devices.csv")
df = pd.read_csv("devices.csv", dtype={"port": "Int64"}, parse_dates=["created"])
df = pd.read_json("data.json")
df = pd.read_parquet("data.parquet")      # needs pyarrow

df.head()
df.shape
df.dtypes
df.info()
df.describe(include="all")
df.isna().sum()
```

`Int64` (capital I) is the nullable integer type: it can hold `NaN` without turning the
column into floats.

## Select

```python
df["host"]                       # Series
df[["host", "port"]]             # DataFrame
df.loc[df["port"] > 1000, ["host", "port"]]     # label-based, with a condition
df.iloc[0:5, 0:2]                # position-based
df.query("port > 1000 and host == 'web1'")
df.filter(like="addr")           # columns whose name contains 'addr'
```

`.loc` is label-based and `.iloc` is positional; `.ix` was removed in pandas 1.0 and
appears in most old tutorials.

## Create and modify

```python
df = df.assign(port_high=df["port"] > 1000)
df = df.rename(columns={"host": "hostname"})
df = df.drop(columns=["notes"])
df = df.sort_values(["hostname", "port"], ascending=[True, False])
df = df.drop_duplicates(subset=["hostname"])
```

Assign the result. `inplace=True` still exists but chains badly and is being
discouraged; the assignment form is what the documentation now shows.

## Missing data

```python
df.isna().sum()
df = df.dropna(subset=["hostname"])
df["port"] = df["port"].fillna(0)
df["notes"] = df["notes"].fillna("")
```

## Group and aggregate

```python
df.groupby("environment")["port"].count()
df.groupby("environment").agg(hosts=("hostname", "nunique"), max_port=("port", "max"))
df.groupby(["environment", "role"]).size().reset_index(name="count")
```

The named-aggregation form (`new_col=("column", "func")`) replaced the old
dictionary-of-dicts syntax and produces a flat, named result.

## Join and concatenate

```python
pd.merge(hosts, events, on="host_id", how="left")
pd.merge(hosts, events, left_on="id", right_on="host_id", how="inner")
pd.concat([df1, df2], ignore_index=True)
```

`merge` is a SQL join; `concat` stacks. `ignore_index=True` prevents duplicate index
labels, which are the usual cause of a later `.loc` returning a DataFrame instead of a
row.

## Time series

```python
df["created"] = pd.to_datetime(df["created"], utc=True)
df = df.set_index("created").sort_index()
df.resample("1D").size()                 # rows per day
df.rolling("7D").mean(numeric_only=True)
df.loc["2026-11-01":"2026-11-10"]
```

Always parse with `utc=True` when the source is mixed or ambiguous; local-time parsing
is how a dataset silently loses an hour twice a year.

## Strings

```python
df["hostname"].str.lower()
df["hostname"].str.startswith("web")
df["hostname"].str.extract(r"^(?P<role>[a-z]+)(?P<num>\d+)$")
df["hostname"].str.replace(r"\d+$", "", regex=True)
```

`.str` accessors are vectorised; a Python loop over a column is the slow path.

## Write

```python
df.to_csv("out.csv", index=False)
df.to_parquet("out.parquet", index=False)      # needs pyarrow
df.to_json("out.json", orient="records", lines=True)
```

`index=False` unless the index is meaningful data — otherwise every reload gains an
`Unnamed: 0` column.

## Traps worth remembering

- Chained assignment (`df[df.a > 1]["b"] = 0`) silently does nothing; use `.loc`.
- A SettingWithCopyWarning is a real warning about a copy, not noise.
- `df.append` was removed in pandas 2.0; use `pd.concat`.
- Object columns holding numbers are slow and memory-hungry; convert with
  `pd.to_numeric(errors="coerce")`.
- `groupby` drops NaN keys by default; pass `dropna=False` when the missing group
  matters.
- Parquet needs `pyarrow` installed; without it `to_parquet` fails with a message about
  a missing engine, not a missing package.
