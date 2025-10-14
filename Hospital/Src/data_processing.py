import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from config import OUTPUT_DIR
import os

def preprocess_data(df):
    """
    Preprocess the dataset for modeling:
    - Removes irrelevant columns
    - Computes length of stay
    - Extracts arrival month
    - Encodes categorical features
    - Scales numeric features
    - Splits into train/test with stratified target
    """
    # Drop non-predictive columns
    df_model = df.drop(['patient_id', 'name'], axis=1)

    # Ensure length_of_stay_days is included
    if 'length_of_stay_days' not in df_model.columns:
        df_model['arrival_date'] = pd.to_datetime(df_model['arrival_date'])
        df_model['departure_date'] = pd.to_datetime(df_model['departure_date'])
        df_model['length_of_stay_days'] = (df_model['departure_date'] - df_model['arrival_date']).dt.days

    # Engineer month feature
    df_model['arrival_month'] = df_model['arrival_date'].dt.month

    # Separate target and features
    X = df_model.drop(['satisfaction', 'arrival_date', 'departure_date'], axis=1)
    y = df_model['satisfaction']

    # Define feature types
    numerical_features = ['age', 'length_of_stay_days', 'arrival_month']
    categorical_features = ['service']

    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
        ]
    )

    # Apply transformations
    X_preprocessed = preprocessor.fit_transform(X)

    # Build readable DataFrame
    feature_names = numerical_features + list(
        preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)
    )
    X_preprocessed_df = pd.DataFrame(X_preprocessed, columns=feature_names)

    # Summary outputs
    #print("✅ Preprocessing complete.")
    #print("Preprocessed Feature Shape:", X_preprocessed.shape)
    #print("\nPreprocessed Features Summary:")
    #print(X_preprocessed_df.describe())
    #print("\nTarget (y) Summary:")
    #print(y.describe())

    # Stratify train/test split on y quartiles
    y_strata = pd.qcut(y, q=4, labels=False)
    X_train, X_test, y_train, y_test = train_test_split(
        X_preprocessed, y, test_size=0.2, random_state=42, stratify=y_strata
    )

    #print("\nTrain Set Shape:", X_train.shape, "Test Set Shape:", X_test.shape)
    #print("Train y mean:", y_train.mean().round(2), "Test y mean:", y_test.mean().round(2))

    return X_train, X_test, y_train, y_test, preprocessor
