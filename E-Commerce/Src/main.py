from data_loading import load_data, inspect_data
from visualization import plot_patient_insights
from data_analysis import add_length_of_stay, service_satisfaction_summary

def main():
    df = load_data()
    inspect_data(df)
    df = add_length_of_stay(df)
    summary = service_satisfaction_summary(df)
    plot_patient_insights(df)

if __name__ == "__main__":
    main()

