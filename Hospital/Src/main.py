from data_loading import load_data, inspect_data
from visualization import plot_patient_insights
from data_analysis import add_length_of_stay, service_satisfaction_summary
from data_processing import preprocess_data

def main():
    df = load_data()
    inspect_data(df)
    df = add_length_of_stay(df)
    summary = service_satisfaction_summary(df)


    # Preprocess and split
    X_train, X_test, y_train, y_test, preprocessor = preprocess_data(df)

    #print("\nSample of preprocessed training data:")
    #print(X_train[:5])
    #print("Sample of target values:")
    #print(y_train[:5])

    plot_patient_insights(df)
if __name__ == "__main__":
    main()
