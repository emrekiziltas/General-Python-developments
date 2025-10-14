
import pandas as pd
from config import CSV_PATH

def load_data():
    """Load patient data from CSV."""
    df = pd.read_csv(CSV_PATH)
    print("✅ Data loaded successfully from:", CSV_PATH)
    print(df.head())
    return df

def inspect_data(df):
    """Basic inspection of the dataset."""
    print("\nDataset Shape:", df.shape)
    print("\nDataset Info:")
    print(df.info())
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nBasic Statistics:")
    print(df.describe(include='all'))
