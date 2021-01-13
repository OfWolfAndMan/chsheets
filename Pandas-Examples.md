### Add Pandas
```Python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```
### Inputs output directly into notebook
%matplotlib inline 


### Reads CSV file from Pandas
```Python
pd.read_csv('file | url')
```
### Gives a number of omitted values per column
```Python
drinks.isnull().sum()
```
### Selecting a specific column
```Python
drinks.continent OR drinks['continent']
```

### Show the first five rows
```Python
drinks.head()
```

### Shows the first five rows, including two specific columns
```Python
drinks[['country', 'beer_servings]].head()
```

### Show the last five rows
```Python
drinks.tail()
```

### Describes the numeric columns (Meant values, counts, min and max, etc)
```Python
drinks.describe()
```

### Gets the various column names
```Python
drinks.columns()
```

### Shows the number of rows and columns in a dataset
```Python
drinks.shape
```

### Show the number of null values for each column
```Python
drinks.isnull().sum()
```

### Select all rows where a specific column is null
```Python
drinks[drinks['continent'].isnull()]
```

### Get the number of counts for a specific column
```Python
drinks.continent.value_counts()
```