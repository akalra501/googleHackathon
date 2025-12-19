import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# 1. Load and Combine Data
df = pd.read_csv('data/dataset1.csv')
dfUsage = pd.concat([pd.read_csv('data/dataset2a.csv'), pd.read_csv('data/dataset2b.csv')], ignore_index=True)
dfTickets = pd.read_csv('data/dataset3.csv')

churnedCustomers = df[df['is_churned'] == 1]
ticketsChurnedCustomers = pd.merge(churnedCustomers, dfTickets, on='customer_id')
import pandas as pd

# 1. Identify 5 consecutive days of zero logins
dfUsage['date'] = pd.to_datetime(dfUsage['date'])
dfUsage = dfUsage.sort_values(['customer_id', 'date'])
dfUsage['isZeroLogin'] = (dfUsage['logins'] == 0).astype(int)

# Use rolling window to find 5-day streaks
dfUsage['zeroStreak'] = dfUsage.groupby('customer_id')['isZeroLogin'].rolling(window=5).sum().reset_index(0, drop=True)

# Grab the FIRST time they hit a 5-day silence
inactivityDropOffs = dfUsage[dfUsage['zeroStreak'] == 5].groupby('customer_id').first().reset_index()
inactivityDropOffs = inactivityDropOffs[['customer_id', 'date']].rename(columns={'date': 'firstGapEndDate'})

# 2. Prepare Ticket Data and Join
# Convert created_at and remove timezone info to prevent subtraction errors
ticketsChurnedCustomers['createdAtDt'] = pd.to_datetime(ticketsChurnedCustomers['created_at']).dt.tz_localize(None)
inactivityDropOffs['firstGapEndDate'] = pd.to_datetime(inactivityDropOffs['firstGapEndDate']).dt.tz_localize(None)

mergedInactivity = pd.merge(ticketsChurnedCustomers, inactivityDropOffs, on='customer_id')

# 3. Calculate the time difference
# This finds how close the ticket creation was to the start of the inactivity streak
mergedInactivity['daysFromGap'] = (mergedInactivity['createdAtDt'] - mergedInactivity['firstGapEndDate']).dt.days.abs()

# 4. Filter for tickets within 2 days of that inactivity period
inactivityTicketsList = mergedInactivity[mergedInactivity['daysFromGap'] <= 2]

# Final list for investigation
finalInactivityList = inactivityTicketsList[['customer_id', 'ticket_text', 'firstGapEndDate', 'createdAtDt', 'daysFromGap']].to_dict('records')

print(f"Identified {len(finalInactivityList)} tickets tied to the first 5-day silence period.")

# Display a few examples
if finalInactivityList:
    print("\nSample Ticket Near Drop-off:")
    print(finalInactivityList[0]['ticket_text'])