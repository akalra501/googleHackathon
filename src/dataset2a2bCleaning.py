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

# combinedDataSet.to_csv('data/dataset2.csv', index=False)
churnedCustomerIds = df[df['is_churned'] == 1]['customer_id'].unique().tolist()
churnedCustomersActivity = combinedDataSet[combinedDataSet['customer_id'].isin(churnedCustomerIds)].copy()

# 2. Convert to datetime objects FIRST (This fixes the AttributeError)
churnedCustomersActivity['date'] = pd.to_datetime(churnedCustomersActivity['date'], format='mixed')

# 3. Sort by ID and Date while they are actual datetime objects
churnedCustomersActivity = churnedCustomersActivity.sort_values(by=['customer_id', 'date'])
churnedCustomersActivity['date'] = churnedCustomersActivity['date'].dt.strftime('%m-%d-%y')
# churnedCustomersActivity.to_csv('data/dataset2_churned.csv', index=False)

# 2. Filter for rows where any activity actually happened
# This ensures we are only looking at dates where they actually used the product
activeRowsOnly = churnedCustomersActivity[
    (churnedCustomersActivity['logins'] > 0) | 
    (churnedCustomersActivity['feature_events'] > 0) | 
    (churnedCustomersActivity['session_minutes'] > 0)
]

# # 3. Create the unique list by finding the max date per customer
# uniqueChurnedActivity = activeRowsOnly.groupby('customer_id')['date'].max().reset_index()

# # 4. Rename the column for clarity
# uniqueChurnedActivity.rename(columns={'date': 'lastActivityDate'}, inplace=True)
# # print(uniqueChurnedActivity.head())
# # print(len(uniqueChurnedActivity))

# allChurnedSet = set(churnedCustomerIds)
# activeChurnedSet = set(uniqueChurnedActivity['customer_id'])

# ghostCustomerIds = allChurnedSet - activeChurnedSet
# ghostCustomersCollection = df[df['customer_id'].isin(ghostCustomerIds)].copy()
activeChurnedIds = activeRowsOnly['customer_id'].unique()

# Group B: Those who never had any non-zero activity (The Ghosts)
ghostCustomers = churnedCustomersActivity[~churnedCustomersActivity['customer_id'].isin(activeChurnedIds)]

# 2. Get Max Date for Active Customers
uniqueActiveActivity = activeRowsOnly.groupby('customer_id')['date'].max().reset_index()
uniqueActiveActivity.rename(columns={'date': 'lastActivityDate'}, inplace=True)

# 3. Get First Date for Ghost Customers
# We use .min() because their 'last activity' is essentially the day they were created
uniqueGhostActivity = ghostCustomers.groupby('customer_id')['date'].min().reset_index()
uniqueGhostActivity.rename(columns={'date': 'lastActivityDate'}, inplace=True)

# 4. Combine both groups into one master list
allChurnedUniqueActivity = pd.concat([uniqueActiveActivity, uniqueGhostActivity], ignore_index=True)
print(allChurnedUniqueActivity.head())
print(len(allChurnedUniqueActivity))

df3 = pd.read_csv('data/dataset3.csv')
df3Churned = df3[df3['customer_id'].isin(churnedCustomerIds)].copy()
tempDates = pd.to_datetime(df3['created_at'], format='mixed')

# 2. Add the new column with the requested format %m-%d-%y
df3['createdAtDate'] = tempDates.dt.strftime('%m-%d-%y')


ticketsWithChurnDates = pd.merge(
    df3, 
    allChurnedUniqueActivity[['customer_id', 'lastActivityDate']], 
    on='customer_id', 
    how='inner'
)
# 3. Filter for tickets created AFTER the last activity date
postChurnTickets = ticketsWithChurnDates[
    ticketsWithChurnDates['createdAtDate'] > ticketsWithChurnDates['lastActivityDate']
]
# 4. Count the number of UNIQUE customers who did this
numPostChurnCustomers = postChurnTickets['customer_id'].nunique()
print(f"Number of customers who submitted a ticket after their last activity: {numPostChurnCustomers}")
# 3. Verify that both columns now exist
# print(df3.head())

# print(len)
