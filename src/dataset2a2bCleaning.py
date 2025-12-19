import pandas as pd

df = pd.read_csv('data/dataset1.csv')
df1 = pd.read_csv('data/dataset2a.csv')
df2 = pd.read_csv('data/dataset2b.csv')
combinedDataSet = pd.concat([df1, df2], axis=0, ignore_index=True)
starterBusinesses = df[df['product_tier'] == 'Starter']
growthBusinesses = df[df['product_tier'] == 'Growth']
enterpriseBusinesses = df[df['product_tier'] == 'Enterprise']

# print((starterBusinesses['renewed_flag'].sum())/len(starterBusinesses))
# print((growthBusinesses['renewed_flag'].sum())/len(growthBusinesses))
# print((enterpriseBusinesses['renewed_flag'].sum())/len(enterpriseBusinesses))

# print((starterCustomerIDs))
# starterInvestigationData = combinedDataSet[combinedDataSet['customer_id'].isin(starterCustomerIDs)]
# starterSummaryStats = starterInvestigationData.describe()
# # print(starterSummaryStats)
def checkDataIntegrity(df):
    '''
    Checks for inconsistencies in the dataframe provided.

    nullSummary: A summary of null values in each column.
    eventsWithoutLogins: Number of rows where feature_events > 0 but logins = 0.
    minutesWithoutLogins: Number of rows where session_minutes > 0 but logins = 0.
    duplicateRows: Number of duplicate rows based on the customer_id and date columns.

    '''
    nullSummary = df.isnull().sum()
    eventsWithoutLogins = df[(df['feature_events'] > 0) & (df['logins'] == 0)]
    minutesWithoutLogins = df[(df['session_minutes'] > 0) & (df['logins'] == 0)]
    duplicateRows = df.duplicated(subset=['customer_id', 'date']).sum()

    return {
        "nullSummary": nullSummary,
        "inconsistentEvents": len(eventsWithoutLogins),
        "inconsistentMinutes": len(minutesWithoutLogins),
        "duplicateEntries": duplicateRows
    }

# inspectionResults = checkDataIntegrity(combinedDataSet)
# print(inspectionResults)

combinedDataSet.to_csv('data/dataset2.csv', index=False)


