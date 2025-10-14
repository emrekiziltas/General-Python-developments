from config import OUTPUT_DIR
import os
import matplotlib.pyplot as plt
import seaborn as sns

def plot_patient_insights(df, output_dir=OUTPUT_DIR, filename="patient_insights.pdf"):
    """Generate combined patient satisfaction visualizations and save to output directory."""

    plt.figure(figsize=(18, 10))

    # 1. Histogram of satisfaction
    plt.subplot(2, 3, 1)
    sns.histplot(df['satisfaction'], kde=True, bins=20)
    plt.title('Distribution of Patient Satisfaction Scores')
    plt.xlabel('Satisfaction Score')

    # 2. Boxplot of satisfaction
    plt.subplot(2, 3, 2)
    sns.boxplot(y=df['satisfaction'])
    plt.title('Boxplot of Satisfaction Scores')
    plt.ylabel('Satisfaction Score')

    # 3. Correlation heatmap
    plt.subplot(2, 3, 3)
    numerical_cols = ['age', 'satisfaction', 'length_of_stay_days']
    corr_matrix = df[numerical_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Matrix of Numerical Features')

    # 4. Scatter: Satisfaction vs Age
    plt.subplot(2, 3, 4)
    sns.scatterplot(data=df, x='age', y='satisfaction')
    plt.title('Satisfaction vs. Age')

    # 5. Scatter: Satisfaction vs Length of Stay
    plt.subplot(2, 3, 5)
    sns.scatterplot(data=df, x='length_of_stay_days', y='satisfaction')
    plt.title('Satisfaction vs. Length of Stay')

    # 6. Boxplot: Satisfaction by Service
    plt.subplot(2, 3, 6)
    sns.boxplot(data=df, x='service', y='satisfaction')
    plt.title('Satisfaction by Service Type')
    plt.xticks(rotation=45)

    plt.tight_layout()

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, filename)
    plt.savefig(save_path, format='pdf')
    print(f"Figure saved to: {save_path}")

    plt.show()
