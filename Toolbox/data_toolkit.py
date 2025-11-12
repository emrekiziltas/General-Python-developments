"""
Data Conversion Toolkit - Reusable functions for data preprocessing
"""
import pandas as pd


# ==================== DATE CONVERSIONS ====================
def convert_dates(df, date_columns, extract_components=True):
    """
    Convert columns to datetime and optionally extract components

    Args:
        df: DataFrame
        date_columns: list of column names to convert
        extract_components: bool, if True extracts Year, Month, Day

    Returns:
        DataFrame with converted dates
    """
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])

            if extract_components:
                df[f'{col}_Year'] = df[col].dt.year
                df[f'{col}_Month'] = df[col].dt.month
                df[f'{col}_Day'] = df[col].dt.day
                df[f'{col}_DayOfWeek'] = df[col].dt.day_name()

    return df


# ==================== NUMERIC CONVERSIONS ====================
def convert_numeric(df, columns, round_decimals=2, add_formatted=True, currency_symbol='$'):
    """
    Convert and format numeric columns

    Args:
        df: DataFrame
        columns: list of column names to convert
        round_decimals: number of decimal places
        add_formatted: bool, if True creates formatted string column
        currency_symbol: symbol for formatted column

    Returns:
        DataFrame with converted numeric columns
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].round(round_decimals)

            if add_formatted:
                df[f'{col}_Formatted'] = df[col].apply(
                    lambda x: f'{currency_symbol}{x:.{round_decimals}f}'
                )

    return df


# ==================== CATEGORICAL CONVERSIONS ====================
def convert_to_category(df, columns):
    """
    Convert columns to category type for memory efficiency

    Args:
        df: DataFrame
        columns: list of column names to convert

    Returns:
        DataFrame with category columns
    """
    for col in columns:
        if col in df.columns:
            # Convert to string first if needed
            if df[col].dtype != 'object':
                df[col] = df[col].astype(str)
            df[col] = df[col].astype('category')

    return df


# ==================== BINNING/CATEGORIZATION ====================
def create_bins(df, column, bins, labels, new_column_name=None):
    """
    Create categorical bins from numeric column

    Args:
        df: DataFrame
        column: column name to bin
        bins: list of bin edges
        labels: list of labels for bins
        new_column_name: name for new column (default: column_Category)

    Returns:
        DataFrame with new binned column
    """
    if column in df.columns:
        if new_column_name is None:
            new_column_name = f'{column}_Category'

        df[new_column_name] = pd.cut(df[column], bins=bins, labels=labels)

    return df


# ==================== AUTO DETECTION & CONVERSION ====================
def auto_convert_types(df, date_columns=None, numeric_columns=None,
                       categorical_columns=None, id_columns=None):
    """
    Automatically detect and convert column types

    Args:
        df: DataFrame
        date_columns: list of date column names (auto-detect if None)
        numeric_columns: list of numeric column names (auto-detect if None)
        categorical_columns: list of categorical column names (auto-detect if None)
        id_columns: list of ID columns to convert to category

    Returns:
        DataFrame with converted types
    """
    # Auto-detect date columns if not provided
    if date_columns is None:
        date_columns = [col for col in df.columns if 'date' in col.lower()]

    # Auto-detect ID columns if not provided
    if id_columns is None:
        id_columns = [col for col in df.columns if 'id' in col.lower()]

    # Convert dates
    if date_columns:
        df = convert_dates(df, date_columns)

    # Convert IDs to category
    if id_columns:
        df = convert_to_category(df, id_columns)

    # Convert specified categorical columns
    if categorical_columns:
        df = convert_to_category(df, categorical_columns)

    # Round numeric columns if specified
    if numeric_columns:
        df = convert_numeric(df, numeric_columns)

    return df


# ==================== DISPLAY FUNCTIONS ====================
def describe_data(df):
    """Display statistics for numeric and categorical columns separately"""
    print("=" * 60)
    print("NUMERIC COLUMNS - Statistics")
    print("=" * 60)
    numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns

    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe())
    else:
        print("No numeric columns found.")

    print("\n" + "=" * 60)
    print("CATEGORICAL COLUMNS - Statistics")
    print("=" * 60)
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(categorical_cols) > 0:
        print(df[categorical_cols].describe())
    else:
        print("No categorical columns found.")

    print("\n" + "=" * 60)
    print("DATETIME COLUMNS - Statistics")
    print("=" * 60)
    datetime_cols = df.select_dtypes(include=['datetime64']).columns

    if len(datetime_cols) > 0:
        print(df[datetime_cols].describe())
    else:
        print("No datetime columns found.")


def show_info(df):
    """Display comprehensive information about the DataFrame"""
    print("=" * 60)
    print("DATAFRAME INFO")
    print("=" * 60)
    print(df.info())
    print("\n" + "=" * 60)
    print("FIRST 5 ROWS")
    print("=" * 60)
    print(df.head())
    print("\n" + "=" * 60)
    print("MISSING VALUES")
    print("=" * 60)
    print(df.isnull().sum())


# ==================== USAGE EXAMPLE ====================
if __name__ == "__main__":
    # Example usage with your dataset
    df = pd.read_csv("dataset.csv")

    print("BEFORE CONVERSIONS:")
    show_info(df)

    # Apply conversions using the toolkit
    df = convert_dates(df, ['PurchaseDate'])
    df = convert_to_category(df, ['CustomerID', 'Location'])
    df = convert_numeric(df, ['TransactionAmount'], round_decimals=2)
    df = create_bins(df, 'TransactionAmount',
                     bins=[0, 100, 400, 1000],
                     labels=['Low', 'Medium', 'High'],
                     new_column_name='PriceCategory')

    print("\n\nAFTER CONVERSIONS:")
    show_info(df)
    describe_data(df)

    # OR use auto-convert for quick setup:
    # df = auto_convert_types(df,
    #                         date_columns=['PurchaseDate'],
    #                         numeric_columns=['TransactionAmount'],
    #                         categorical_columns=['Location'],
    #                         id_columns=['CustomerID', 'OrderID'])