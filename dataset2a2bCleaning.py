import pandas as pd

df1 = pd.read_csv('data/dataset2a.csv')
df2 = pd.read_csv('data/dataset2b.csv')

combinedUsageLogs = pd.concat([df1, df2], axis=0, ignore_index=True)
print(len(combinedUsageLogs))