from data_loading import load_data, inspect_data
from data_analysis import add_length_of_stay
from visualization import plot_patient_insights

def main():
    df = load_data()
    inspect_data(df)
    df = add_length_of_stay(df)
    plot_patient_insights(df)

if __name__ == "__main__":
    main()
