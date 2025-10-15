from data_loading import load_data, inspect_data
from visualization import plot_patient_insights
from data_analysis import add_length_of_stay, service_satisfaction_summary
from data_processing import preprocess_data

def main():

    data = load_data()
    df = data["patients"]

    inspect_data(data["patients"])
    data["patients"] = add_length_of_stay(data["patients"])
    summary = service_satisfaction_summary(data["patients"])

    # Preprocess and split
    X_train, X_test, y_train, y_test, preprocessor = preprocess_data(df)

    # Plot and save visualizations
    plot_patient_insights(df, filename="patient_insights.pdf")

if __name__ == "__main__":
    main()
