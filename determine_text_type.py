# Load the new CSV file and re-categorize columns with the updated logic
import pandas as pd

file_path_defending = '/app/db/fifa/session_stats/2024-09-12/SUMMARY.csv'
data_defending = pd.read_csv(file_path_defending)

# Updated categorization function
ints = []
floats = []
texts = []
percents = []

# Categorize columns considering null/empty string handling
for column in data_defending.columns:
    col_data = data_defending[column].replace("", None).dropna()
    if col_data.empty:
        continue  # Skip columns with no data after cleaning
    if col_data.apply(lambda x: isinstance(x, int)).all():
        ints.append(column)
    elif col_data.apply(lambda x: isinstance(x, float)).all():
        floats.append(column)
    elif col_data.astype(str).str.contains('%').any():
        percents.append(column)
    else:
        texts.append(column)

# Results
print('INTS')
print(ints)
print('FLOATS')
print(floats)
print('TEXT')
print(texts)
print('PERCENTAGE')
print(percents)
