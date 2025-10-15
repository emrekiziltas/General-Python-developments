
import os
import pandas as pd
from config import DATA_DIR
import missingno as msno
import matplotlib.pyplot as plt

def load_data():
    """Load hospital datasets from CSV files."""
    try:

        hotel_df = pd.read_csv(os.path.join(DATA_DIR, 'Hotel Reservations.csv'), encoding='utf-8')
        print("\n✅ Data successfully loaded.")
        print(f"Patients shape: {hotel_df.shape}")
        print(hotel_df.head(), "\n")
        return hotel_df

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        raise

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        raise

def inspect_data(df):
    """Basic inspection of the dataset."""
    #print("\nDataset Shape:", df.shape)
    #print("\nDataset Info:")
   # print(df.info())
    #print("\nMissing Values:")
    #print(df.isnull().sum())
    #print("\nBasic Statistics:")
    df = df.drop("Booking_ID", axis=1)
    #print(msno.matrix(df))
    #plt.show()
    #print(df.describe(include='all'))


def visualize_missing(df):

    # Bar plot
    plt.figure(figsize=(6, 6))
    msno.bar(df)
    plt.title("Missing Data Bar Plot")
    plt.show()

    # Ek: eksik değerlerin sayısını göstermek
    print("\nMissing values per column:\n")
    print(df.isnull().sum())