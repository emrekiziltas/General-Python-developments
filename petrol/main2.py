import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# --- CONFIGURATION ---

COMMODITY_SYMBOLS = {
    # Brent Crude Oil (Futures Contract)
    "Brent_Crude": "BZ=F",  # ICE Brent Crude Futures

    # Natural Gas Henry Hub (Futures Contract)
    "Natural_Gas_Henry_Hub": "NG=F",  # NYMEX Natural Gas Futures

    # Alternative: ETFs (more stable data)
    # "Brent_Crude_ETF": "BNO",
    # "Natural_Gas_ETF": "UNG",
}

# Date Range: Last 1 year
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

# Storage Options
OUTPUT_DIR = "commodity_data"
SAVE_CSV = True
SAVE_JSON = True
SAVE_EXCEL = True
OUTPUT_DIR = "commodity_data"
SAVE_CSV = True
SAVE_JSON = True
SAVE_EXCEL = True


# --- FUNCTIONS ---

def create_output_directory():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Created directory: {OUTPUT_DIR}")


def fetch_yfinance_data(symbol, start, end, name):
    """
    Fetch historical data using yfinance with enhanced error handling.
    """
    try:
        print(f"  🔄 Fetching data for {name}...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end)

        if df.empty:
            print(f"  ⚠️  Warning: No data returned for {symbol}")
            return pd.DataFrame()

        if 'Close' not in df.columns:
            print(f"  ⚠️  Warning: 'Close' column not found for {symbol}")
            return pd.DataFrame()

        # Return only Close price with renamed column
        result = df[['Close']].copy()
        result.columns = [f"{name}_Price"]

        print(f"  ✅ Successfully fetched {len(result)} days of data")
        return result

    except Exception as e:
        print(f"  ❌ Error fetching {symbol}: {e}")
        return pd.DataFrame()


def save_to_csv(df, filename):
    """Save DataFrame to CSV file."""
    try:
        filepath = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(filepath)
        print(f"✅ CSV saved: {filepath}")
        return True
    except Exception as e:
        print(f"❌ CSV save failed: {e}")
        return False


def save_to_json(df, filename):
    """Save DataFrame to JSON file (multiple formats)."""
    try:
        base_name = filename.replace('.csv', '')

        # Format 1: Records format (list of dictionaries)
        filepath_records = os.path.join(OUTPUT_DIR, f"{base_name}_records.json")
        df.reset_index().to_json(filepath_records, orient='records', date_format='iso', indent=2)
        print(f"✅ JSON (records) saved: {filepath_records}")

        # Format 2: Index format (date as key)
        filepath_index = os.path.join(OUTPUT_DIR, f"{base_name}_indexed.json")
        df.to_json(filepath_index, orient='index', date_format='iso', indent=2)
        print(f"✅ JSON (indexed) saved: {filepath_index}")

        return True
    except Exception as e:
        print(f"❌ JSON save failed: {e}")
        return False


def save_to_excel(df, filename):
    """Save DataFrame to Excel file with formatting."""
    try:
        filepath = os.path.join(OUTPUT_DIR, filename.replace('.csv', '.xlsx'))

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Write main data
            df.to_excel(writer, sheet_name='Commodity_Prices')

            # Write summary statistics
            summary = df.describe()
            summary.to_excel(writer, sheet_name='Statistics')

        print(f"✅ Excel saved: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Excel save failed: {e}")
        return False


def save_metadata(df, symbols_used):
    """Save metadata about the data collection."""
    metadata = {
        'collection_date': datetime.now().isoformat(),
        'date_range': {
            'start': df.index.min().isoformat() if not df.empty else None,
            'end': df.index.max().isoformat() if not df.empty else None,
        },
        'symbols': symbols_used,
        'rows_collected': len(df),
        'columns': list(df.columns),
        'missing_data_points': df.isna().sum().to_dict()
    }

    filepath = os.path.join(OUTPUT_DIR, 'metadata.json')
    with open(filepath, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Metadata saved: {filepath}")


# --- MAIN EXECUTION ---

def main():
    print("=" * 60)
    print(f"💰 COMMODITY DATA FETCHER")
    print(f"📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("=" * 60)

    # Create output directory
    create_output_directory()

    # Fetch data for all commodities
    all_data = pd.DataFrame()
    successful_symbols = {}

    for name, symbol in COMMODITY_SYMBOLS.items():
        print(f"\n{'─' * 60}")
        print(f"📊 Processing: {name} ({symbol})")
        print(f"{'─' * 60}")

        commodity_df = fetch_yfinance_data(symbol, start_date, end_date, name)

        if not commodity_df.empty:
            if all_data.empty:
                all_data = commodity_df
            else:
                all_data = all_data.join(commodity_df, how='outer')
            successful_symbols[name] = symbol

    # Process and save results
    if not all_data.empty:
        print("\n" + "=" * 60)
        print("📈 DATA PROCESSING")
        print("=" * 60)

        # Set index name
        all_data.index.name = 'Date'

        # Forward fill missing values
        all_data.ffill(inplace=True)

        # Display sample data
        print("\n--- First 5 Rows ---")
        print(all_data.head())
        print("\n--- Last 5 Rows ---")
        print(all_data.tail())
        print("\n--- Data Summary ---")
        print(all_data.describe())

        # Save in multiple formats
        print("\n" + "=" * 60)
        print("💾 SAVING DATA")
        print("=" * 60)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"commodities_{timestamp}.csv"

        if SAVE_CSV:
            save_to_csv(all_data, base_filename)

        if SAVE_JSON:
            save_to_json(all_data, base_filename)

        if SAVE_EXCEL:
            save_to_excel(all_data, base_filename)

        # Save metadata
        save_metadata(all_data, successful_symbols)

        print("\n" + "=" * 60)
        print("✅ DATA COLLECTION COMPLETE")
        print("=" * 60)
        print(f"📁 All files saved to: {OUTPUT_DIR}/")
        print(f"📊 Total data points: {len(all_data)}")
        print(f"📈 Commodities collected: {len(successful_symbols)}")

    else:
        print("\n" + "=" * 60)
        print("⚠️  ERROR: No data was collected")
        print("=" * 60)
        print("Possible reasons:")
        print("  - Invalid symbols")
        print("  - Network connection issues")
        print("  - yfinance API problems")


if __name__ == "__main__":
    main()