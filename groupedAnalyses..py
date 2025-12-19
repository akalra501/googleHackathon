import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

salesforceFile = 'data/dataset1.csv' 
chartsDir = 'charts'

# Primary dimensions for grouping
categoricalGroups = [
    'industry', 'company_size_bucket', 'product_tier', 
    'sales_segment', 'acquisition_channel', 'region'
]

df = pd.read_csv(salesforceFile)


def analyzeChurnDistribution(df, groups):
    overallAvgChurn = df['is_churned'].mean()    
    for group in groups:
        if group not in df.columns:
            continue

        # Grouped calculation: Count of customers and Mean (Churn Rate)
        churnAnalysis = df.groupby(group)['is_churned'].agg(['count', 'mean']).reset_index()
        churnAnalysis.columns = [group, 'customerCount', 'churnRate']
        churnAnalysis = churnAnalysis.sort_values(by='churnRate', ascending=False)
        print(f"\n--- Churn Analysis by {group} ---")
        print(churnAnalysis)
        
        # Visualization
        plt.figure(figsize=(12, 7))
        sns.barplot(x=group, y='churnRate', data=churnAnalysis, palette='Reds_r')
        
        # Benchmarking against overall average
        plt.axhline(overallAvgChurn, color='blue', linestyle='--', label=f'Avg Churn ({overallAvgChurn:.2%})')    
        plt.title(f'Churn Rate Distribution: {group.replace("_", " ").title()}', fontsize=15)
        plt.ylabel('Churn Probability')
        plt.xlabel(group.replace('_', ' ').title())
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        
        # Export to charts folder
        savePath = os.path.join(chartsDir, f'churn_by_{group}.png')
        plt.savefig(savePath)
        plt.close()
        print(f"Saved PNG to {savePath}")

def runSalesforceAnalysis():
    salesforceDf = df
    if salesforceDf is not None:
        analyzeChurnDistribution(salesforceDf, categoricalGroups)

runSalesforceAnalysis()