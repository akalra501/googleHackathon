import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df1 = pd.read_csv('data/dataset1.csv')
# df2 = pd.read_csv('data/dataset2a.csv')
# df3 = pd.read_csv('data/dataset2b.csv')
# df4 = pd.read_csv('data/dataset3.csv')

# def summarize_data(df):
#     print("Data Summary:")
#     print(df.info())
#     print("\nMissing Values:")
#     print(df.isnull().sum())
#     print("\nStatistical Summary:")
#     print(df.describe())
#     print("\nColumn Names:")
#     print(df.columns.tolist())    

# # summarize_data(df1)
# summarize_data(df2)
# summarize_data(df3)
# # summarize_data(df4)

# # print(df4.value_counts('issue_category'))
columns = ['industry', 'company_size_bucket', 'product_tier', 
           'sales_segment', 'acquisition_channel']
for i in columns:
    print(df1[i].value_counts())