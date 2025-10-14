import pandas as pd
from scipy import stats

def add_length_of_stay(df):
    """Add a calculated 'length_of_stay_days' column."""
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    df['departure_date'] = pd.to_datetime(df['departure_date'])
    df['length_of_stay_days'] = (df['departure_date'] - df['arrival_date']).dt.days

   # print("\nLength of Stay Statistics:")
   # print(df['length_of_stay_days'].describe())
    return df

def service_satisfaction_summary(df):
    """Compute service-wise satisfaction statistics."""
    summary = df.groupby('service')['satisfaction'].agg(['mean', 'std', 'count']).round(2)
    #print("\nService-wise Satisfaction Summary:")
    #print(summary)  # Use print instead of display() in scripts

    groups = [group['satisfaction'].values for name, group in df.groupby('service')]
    f_stat, p_value = stats.f_oneway(*groups)

    #print(f"\nANOVA Test for Satisfaction across Services: F-statistic = {f_stat:.2f}, p-value = {p_value:.4f}")

    return summary