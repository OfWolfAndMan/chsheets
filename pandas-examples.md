---
title: pandas
summary: pandas recipes
tags: [python, data, pandas]
tooling: [python, pandas]
verified_on: null
verified_env: null
status: unverified
---

# pandas

## Add Pandas

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```

### Inputs output directly into notebook

%matplotlib inline

### Reads CSV file from Pandas

```python
pd.read_csv('file | url')
```

### Gives a number of omitted values per column

```python
drinks.isnull().sum()
```

### Selecting a specific column

```python
drinks['continent']      # or: drinks.continent
```

### Show the first five rows

```python
drinks.head()
```

### Shows the first five rows, including two specific columns

```python
drinks[['country', 'beer_servings']].head()
```

### Show the last five rows

```python
drinks.tail()
```

### Describes the numeric columns (Meant values, counts, min and max, etc)

```python
drinks.describe()
```

### Gets the various column names

```python
drinks.columns()
```

### Shows the number of rows and columns in a dataset

```python
drinks.shape
```

### Show the number of null values for each column

```python
drinks.isnull().sum()
```

### Select all rows where a specific column is null

```python
drinks[drinks['continent'].isnull()]
```

### Get the number of counts for a specific column

```python
drinks.continent.value_counts()
```
