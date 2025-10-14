import pandas as pd

def add_length_of_stay(df):
    """Add a calculated 'length_of_stay_days' column."""
    df['arrival_date'] = pd.to_datetime(df['arrival_date'])
    df['departure_date'] = pd.to_datetime(df['departure_date'])
    df['length_of_stay_days'] = (df['departure_date'] - df['arrival_date']).dt.days

    print("\nLength of Stay Statistics:")
    print(df['length_of_stay_days'].describe())
    return df
