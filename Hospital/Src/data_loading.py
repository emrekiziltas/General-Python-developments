
import os
import pandas as pd
from config import DATA_DIR

def load_data():
    """Load hospital datasets from CSV files."""
    try:

        services_df = pd.read_csv(os.path.join(DATA_DIR, 'services_weekly.csv'), encoding='utf-8')
        staff_df = pd.read_csv(os.path.join(DATA_DIR, 'staff.csv'), encoding='utf-8')
        staff_schedule_df = pd.read_csv(os.path.join(DATA_DIR, 'staff_schedule.csv'), encoding='utf-8')
        patients_df = pd.read_csv(os.path.join(DATA_DIR, 'patients.csv'), encoding='utf-8')

        print("\n✅ Data successfully loaded.")
        print(f"Patients shape: {patients_df.shape}")
        print(patients_df.head(), "\n")

        return {
            "patients": patients_df,
            "staff": staff_df,
            "staff_schedule": staff_schedule_df,
            "services": services_df
        }

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
    print(df.info())
    #print("\nMissing Values:")
    #print(df.isnull().sum())
    #print("\nBasic Statistics:")
    #print(df.describe(include='all'))
