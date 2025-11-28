import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import configparser

# Read config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Get folder path from config and strip any extra quotes
folder_path = config['Settings']['folder_path'].strip('"')

# Set style for better-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# ============================================
# STEP 1: LOAD DATA
# ============================================
print("Loading data...")

merged_file_path = f"{folder_path}/merged_file.csv"
df = pd.read_csv(merged_file_path)

# Display basic info
print(f"\nTotal rows: {len(df):,}")
print(f"Date range: {df['Month'].min()} to {df['Month'].max()}")
print(f"\nColumn names:\n{df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head())

# ============================================
# STEP 2: DATA CLEANING
# ============================================
print("\n" + "="*50)
print("DATA CLEANING")
print("="*50)

# Check for missing values
print("\nMissing values:")
print(df.isnull().sum())

# Convert Month to datetime
df['Month'] = pd.to_datetime(df['Month'])

# Check unique values
print(f"\nUnique crime types: {df['Crime type'].nunique()}")
print(f"Unique LSOA areas: {df['LSOA name'].nunique()}")

# ============================================
# PIVOT TABLE 1: CRIME TYPE ANALYSIS
# ============================================
print("\n" + "="*50)
print("PIVOT TABLE 1: CRIMES BY TYPE")
print("="*50)

pivot1 = df.groupby('Crime type').size().reset_index(name='Count')
pivot1 = pivot1.sort_values('Count', ascending=False)
pivot1['Percentage'] = (pivot1['Count'] / pivot1['Count'].sum() * 100).round(2)

print("\n", pivot1.to_string(index=False))

# Visualize
plt.figure(figsize=(12, 8))
top10 = pivot1.head(10)
plt.barh(top10['Crime type'], top10['Count'], color='steelblue')
plt.xlabel('Number of Crimes')
plt.title('Top 10 Crime Types in Cambridge (12 Months)', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()
for i, v in enumerate(top10['Count']):
    plt.text(v + 50, i, f'{v:,}', va='center')
plt.tight_layout()
plt.savefig('chart1_crime_types.png', dpi=300, bbox_inches='tight')
print("\n✓ Chart saved: chart1_crime_types.png")
plt.close()

# ============================================
# PIVOT TABLE 2: MONTHLY TRENDS
# ============================================
print("\n" + "="*50)
print("PIVOT TABLE 2: MONTHLY TRENDS")
print("="*50)

# Get top 5 crime types
top5_crimes = pivot1.head(5)['Crime type'].tolist()

# Create pivot table for monthly trends
pivot2 = df[df['Crime type'].isin(top5_crimes)].groupby(
    [df['Month'].dt.to_period('M'), 'Crime type']
).size().unstack(fill_value=0)

print("\n", pivot2)

# Visualize
pivot2.plot(kind='line', marker='o', linewidth=2, figsize=(14, 7))
plt.title('Monthly Crime Trends - Top 5 Crime Types', fontsize=14, fontweight='bold')
plt.xlabel('Month')
plt.ylabel('Number of Crimes')
plt.legend(title='Crime Type', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('chart2_monthly_trends.png', dpi=300, bbox_inches='tight')
print("✓ Chart saved: chart2_monthly_trends.png")
plt.close()

# ============================================
# PIVOT TABLE 3: GEOGRAPHIC ANALYSIS
# ============================================
print("\n" + "="*50)
print("PIVOT TABLE 3: CRIMES BY AREA")
print("="*50)

pivot3 = df.groupby('LSOA name').size().reset_index(name='Count')
pivot3 = pivot3.sort_values('Count', ascending=False)
pivot3['Percentage'] = (pivot3['Count'] / pivot3['Count'].sum() * 100).round(2)

print("\nTop 15 Areas:")
print(pivot3.head(15).to_string(index=False))

print("\nSafest 10 Areas:")
print(pivot3.tail(10).to_string(index=False))

# Visualize top areas
plt.figure(figsize=(12, 8))
top15_areas = pivot3.head(15)
colors = plt.cm.Reds(top15_areas['Count'] / top15_areas['Count'].max())
plt.barh(top15_areas['LSOA name'], top15_areas['Count'], color=colors)
plt.xlabel('Number of Crimes')
plt.title('Top 15 High-Crime Areas in Cambridge', fontsize=14, fontweight='bold')
plt.gca().invert_yaxis()
for i, v in enumerate(top15_areas['Count']):
    plt.text(v + 20, i, f'{v:,}', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('chart3_areas.png', dpi=300, bbox_inches='tight')
print("✓ Chart saved: chart3_areas.png")
plt.close()

# ============================================
# PIVOT TABLE 4: OUTCOMES ANALYSIS
# ============================================
print("\n" + "="*50)
print("PIVOT TABLE 4: CRIME OUTCOMES")
print("="*50)

pivot4 = df.groupby('Last outcome category').size().reset_index(name='Count')
pivot4 = pivot4.sort_values('Count', ascending=False)
pivot4['Percentage'] = (pivot4['Count'] / pivot4['Count'].sum() * 100).round(2)

print("\n", pivot4.to_string(index=False))

# Visualize
plt.figure(figsize=(10, 10))
colors = plt.cm.Set3(range(len(pivot4)))
plt.pie(pivot4['Count'], labels=pivot4['Last outcome category'], autopct='%1.1f%%',
        startangle=90, colors=colors)
plt.title('Distribution of Crime Outcomes', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('chart4_outcomes.png', dpi=300, bbox_inches='tight')
print("✓ Chart saved: chart4_outcomes.png")
plt.close()

# ============================================
# ADDITIONAL INSIGHTS
# ============================================
print("\n" + "="*50)
print("KEY INSIGHTS")
print("="*50)

# Total crimes
total_crimes = len(df)
print(f"\n1. Total crimes analyzed: {total_crimes:,}")

# Most common crime
most_common = pivot1.iloc[0]
print(f"\n2. Most common crime type: {most_common['Crime type']}")
print(f"   - Count: {most_common['Count']:,} ({most_common['Percentage']:.1f}%)")

# Highest crime area
highest_area = pivot3.iloc[0]
print(f"\n3. Highest crime area: {highest_area['LSOA name']}")
print(f"   - Count: {highest_area['Count']:,} ({highest_area['Percentage']:.1f}%)")

# Safest area
safest_area = pivot3.iloc[-1]
print(f"\n4. Safest area: {safest_area['LSOA name']}")
print(f"   - Count: {safest_area['Count']:,} ({safest_area['Percentage']:.1f}%)")

# Most common outcome
most_common_outcome = pivot4.iloc[0]
print(f"\n5. Most common outcome: {most_common_outcome['Last outcome category']}")
print(f"   - Count: {most_common_outcome['Count']:,} ({most_common_outcome['Percentage']:.1f}%)")

# Calculate solved rate (charges/summons)
solved = df[df['Last outcome category'].str.contains('charge|summons|court', case=False, na=False)]
solved_rate = (len(solved) / total_crimes * 100)
print(f"\n6. Cases resulting in charges/court: {len(solved):,} ({solved_rate:.1f}%)")

# Monthly average
monthly_avg = df.groupby(df['Month'].dt.to_period('M')).size().mean()
print(f"\n7. Average crimes per month: {monthly_avg:.0f}")

# Seasonal analysis
df['Season'] = df['Month'].dt.month.map({
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Autumn', 10: 'Autumn', 11: 'Autumn'
})
seasonal = df.groupby('Season').size().sort_values(ascending=False)
print(f"\n8. Crimes by season:")
for season, count in seasonal.items():
    print(f"   - {season}: {count:,}")

print("\n" + "="*50)
print("ANALYSIS COMPLETE!")
print("="*50)
print("\nGenerated files:")
print("✓ chart1_crime_types.png")
print("✓ chart2_monthly_trends.png")
print("✓ chart3_areas.png")
print("✓ chart4_outcomes.png")
print("\nNext steps:")
print("1. Review the charts")
print("2. Write your report using these insights")
print("3. Upload to GitHub")
print("4. Share on LinkedIn!")