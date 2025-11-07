import pandas as pd
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('dataset.csv')

df['PurchaseDate'] = pd.to_datetime(df['PurchaseDate'])

#Recency
df_recency = df.groupby(by='CustomerID', as_index=False)['PurchaseDate'].max()
df_recency.columns = ['CustomerID', 'LastPurchaseDate']
recent_date = df_recency['LastPurchaseDate'].max()
df_recency['Recency'] = df_recency['LastPurchaseDate'].apply(lambda x: (recent_date - x).days)

#Frequency
frequency_df = df.drop_duplicates().groupby(by=['CustomerID'], as_index=False)['PurchaseDate'].count()
frequency_df.columns = ['CustomerID', 'Frequency']

#Monetary
df['Total'] = df['TransactionAmount']  # Total spent by each customer
monetary_df = df.groupby(by='CustomerID', as_index=False)['Total'].sum()
monetary_df.columns = ['CustomerID', 'Monetary']

rf_df = df_recency.merge(frequency_df, on='CustomerID')
rfm_df = rf_df.merge(monetary_df, on='CustomerID').drop(columns='LastPurchaseDate')


rfm_df['R_rank'] = rfm_df['Recency'].rank(ascending=True)
rfm_df['F_rank'] = rfm_df['Frequency'].rank(ascending=False)
rfm_df['M_rank'] = rfm_df['Monetary'].rank(ascending=False)

# Normalize
for col in ['R_rank', 'F_rank', 'M_rank']:
    rfm_df[f'{col}_norm'] = (rfm_df[col] / rfm_df[col].max()) * 100

# Calculate weighted RFM score
rfm_df['RFM_Score'] = (0.15 * rfm_df['R_rank_norm'] +
                       0.28 * rfm_df['F_rank_norm'] +
                       0.57 * rfm_df['M_rank_norm']) * 0.05
rfm_df = rfm_df.round(2)

print(rfm_df)

rfm_df["Customer_segment"] = np.where(rfm_df['RFM_Score'] > 4.5, "Top Customers",
                             np.where(rfm_df['RFM_Score'] > 4, "High value Customer",
                            np.where(rfm_df['RFM_Score'] > 3, "Medium Value Customer",
                             np.where(rfm_df['RFM_Score'] > 1.6, 'Low Value Customers', 'Lost Customers'))))


rfm_df[['CustomerID', 'RFM_Score', 'Customer_segment']].head(20)
plt.pie(rfm_df.Customer_segment.value_counts(), labels=rfm_df.Customer_segment.value_counts().index, autopct='%.0f%%')
plt.show()