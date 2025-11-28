import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import numpy as np

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
print("\n" + "=" * 50)
print("DATA CLEANING")
print("=" * 50)

# Check for missing values
print("\nMissing values:")
print(df.isnull().sum())

# Convert Month to datetime
df['Month'] = pd.to_datetime(df['Month'])

# Clean coordinates - remove missing values
df_map = df.dropna(subset=['Longitude', 'Latitude'])
print(f"\nRows with valid coordinates: {len(df_map):,}")

# Check unique values
print(f"\nUnique crime types: {df['Crime type'].nunique()}")
print(f"Unique LSOA areas: {df['LSOA name'].nunique()}")

# ============================================
# PIVOT TABLE 1: CRIME TYPE ANALYSIS
# ============================================
print("\n" + "=" * 50)
print("PIVOT TABLE 1: CRIMES BY TYPE")
print("=" * 50)

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
print("\n" + "=" * 50)
print("PIVOT TABLE 2: MONTHLY TRENDS")
print("=" * 50)

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
print("\n" + "=" * 50)
print("PIVOT TABLE 3: CRIMES BY AREA")
print("=" * 50)

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
print("\n" + "=" * 50)
print("PIVOT TABLE 4: CRIME OUTCOMES")
print("=" * 50)

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
# INTERACTIVE MAP 1: HEATMAP (RED = DANGER!)
# ============================================
print("\n" + "=" * 50)
print("CREATING INTERACTIVE CRIME HEATMAP")
print("=" * 50)

# Calculate center of Cambridge
center_lat = df_map['Latitude'].mean()
center_lon = df_map['Longitude'].mean()

print(f"Map centered at: ({center_lat:.4f}, {center_lon:.4f})")

# Create base map
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=13,
    tiles='OpenStreetMap'
)

# Prepare data for heatmap
heat_data = [[row['Latitude'], row['Longitude']] for idx, row in df_map.iterrows()]

# Add heatmap layer (RED = HIGH CRIME)
HeatMap(
    heat_data,
    min_opacity=0.3,
    max_opacity=0.8,
    radius=15,
    blur=20,
    gradient={0.0: 'yellow', 0.5: 'orange', 1.0: 'red'}
).add_to(m)

# Save map
m.save('map1_crime_heatmap.html')
print("✓ Interactive map saved: map1_crime_heatmap.html")
print("  → Open this file in your browser to see the RED zones!")

# ============================================
# INTERACTIVE MAP 2: MARKERS FOR HIGH CRIME SPOTS
# ============================================
print("\nCreating map with crime hotspot markers...")

# Calculate crime density per location
location_counts = df_map.groupby(['Latitude', 'Longitude']).size().reset_index(name='Crimes')

# Get top dangerous locations
top_locations = location_counts.nlargest(20, 'Crimes')

# Create new map
m2 = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=13,
    tiles='OpenStreetMap'
)

# Add markers for top dangerous spots
for idx, row in top_locations.iterrows():
    # Color based on crime count
    if row['Crimes'] > top_locations['Crimes'].quantile(0.75):
        color = 'red'
        icon = 'exclamation-triangle'
    elif row['Crimes'] > top_locations['Crimes'].quantile(0.5):
        color = 'orange'
        icon = 'warning-sign'
    else:
        color = 'yellow'
        icon = 'info-sign'

    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"<b>HIGH CRIME AREA</b><br>Total Crimes: {row['Crimes']}",
        tooltip=f"{row['Crimes']} crimes",
        icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
    ).add_to(m2)

m2.save('map2_crime_markers.html')
print("✓ Interactive map saved: map2_crime_markers.html")
print("  → RED markers = Most dangerous spots!")

# ============================================
# INTERACTIVE MAP 3: CLUSTER MAP WITH STATISTICS
# ============================================
print("\nCreating enhanced cluster map with crime counts...")

from folium.plugins import MarkerCluster

m3 = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=13,
    tiles='OpenStreetMap'
)

# Create marker cluster
marker_cluster = MarkerCluster(
    name='Crime Locations',
    overlay=True,
    control=True,
).add_to(m3)

# Sample data (otherwise too many markers)
sample_size = min(5000, len(df_map))
df_sample = df_map.sample(n=sample_size, random_state=42)

# Add markers to cluster
for idx, row in df_sample.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=3,
        popup=f"<b>Crime Type:</b> {row['Crime type']}<br><b>Date:</b> {row['Month']}<br><b>Location:</b> {row['Location']}",
        color='red',
        fill=True,
        fillColor='red',
        fillOpacity=0.6
    ).add_to(marker_cluster)

# Add area-level crime statistics as large circles
area_stats = df_map.groupby('LSOA name').agg({
    'Latitude': 'mean',
    'Longitude': 'mean',
    'Crime ID': 'count'
}).reset_index()
area_stats.columns = ['LSOA_name', 'Lat', 'Lon', 'Crime_Count']
area_stats = area_stats.sort_values('Crime_Count', ascending=False)

# Add circles for each LSOA area showing crime counts
for idx, row in area_stats.iterrows():
    # Calculate circle size based on crime count
    radius = np.sqrt(row['Crime_Count']) * 20

    # Color based on crime density
    if row['Crime_Count'] > area_stats['Crime_Count'].quantile(0.75):
        color = 'darkred'
        fill_color = 'red'
    elif row['Crime_Count'] > area_stats['Crime_Count'].quantile(0.5):
        color = 'orange'
        fill_color = 'orange'
    else:
        color = 'yellow'
        fill_color = 'yellow'

    # Get crime breakdown for this area
    area_crimes = df_map[df_map['LSOA name'] == row['LSOA_name']]
    crime_breakdown = area_crimes['Crime type'].value_counts().head(5)

    breakdown_html = "<br>".join([f"• {crime}: {count}" for crime, count in crime_breakdown.items()])

    popup_html = f"""
    <div style='width: 250px'>
        <h4 style='margin-bottom: 10px; color: #d32f2f;'>{row['LSOA_name']}</h4>
        <hr style='margin: 5px 0;'>
        <p style='margin: 5px 0;'><b>Total Crimes:</b> {row['Crime_Count']}</p>
        <p style='margin: 5px 0;'><b>Top Crime Types:</b></p>
        <div style='margin-left: 10px; font-size: 12px;'>
            {breakdown_html}
        </div>
    </div>
    """

    folium.Circle(
        location=[row['Lat'], row['Lon']],
        radius=radius,
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{row['LSOA_name']}: {row['Crime_Count']} crimes",
        color=color,
        fill=True,
        fillColor=fill_color,
        fillOpacity=0.3,
        weight=2
    ).add_to(m3)

    # Add text label for crime count (for top areas)
    if idx < 10:  # Only show labels for top 10 areas
        folium.Marker(
            location=[row['Lat'], row['Lon']],
            icon=folium.DivIcon(html=f"""
                <div style='
                    font-size: 14px; 
                    font-weight: bold; 
                    color: white; 
                    text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000;
                    text-align: center;
                '>
                    {row['Crime_Count']}
                </div>
            """)
        ).add_to(m3)

# Add legend
legend_html = """
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 200px; height: auto; 
            background-color: white; z-index:9999; font-size:14px;
            border:2px solid grey; border-radius: 5px; padding: 10px">
    <p style="margin: 0; font-weight: bold; text-align: center;">Crime Density</p>
    <hr style="margin: 5px 0;">
    <p style="margin: 5px 0;"><span style="color: darkred;">●</span> Very High (Top 25%)</p>
    <p style="margin: 5px 0;"><span style="color: orange;">●</span> High (25-50%)</p>
    <p style="margin: 5px 0;"><span style="color: yellow;">●</span> Moderate (Below 50%)</p>
    <hr style="margin: 5px 0;">
    <p style="margin: 5px 0; font-size: 12px;">Circle size = Crime count<br>Numbers = Total crimes in area</p>
</div>
"""
m3.get_root().html.add_child(folium.Element(legend_html))

m3.save('map3_crime_clusters.html')
print("✓ Interactive map saved: map3_crime_clusters.html")
print("  → Click clusters to zoom in!")
print("  → Circle size = Crime density")
print("  → Numbers show total crimes per area!")
print("  → Click circles for detailed breakdown!")

# ============================================
# SAVE TOP DANGEROUS LOCATIONS
# ============================================
print("\n" + "=" * 50)
print("TOP 20 MOST DANGEROUS COORDINATES")
print("=" * 50)

print("\n", top_locations.to_string(index=False))

# Add LSOA names to top locations
top_with_names = []
for idx, loc in top_locations.iterrows():
    # Find crimes at this location
    crimes_here = df_map[
        (df_map['Latitude'] == loc['Latitude']) &
        (df_map['Longitude'] == loc['Longitude'])
        ]
    most_common_lsoa = crimes_here['LSOA name'].mode()[0] if len(crimes_here) > 0 else 'Unknown'
    most_common_type = crimes_here['Crime type'].mode()[0] if len(crimes_here) > 0 else 'Unknown'

    top_with_names.append({
        'Latitude': loc['Latitude'],
        'Longitude': loc['Longitude'],
        'Total_Crimes': loc['Crimes'],
        'LSOA_Name': most_common_lsoa,
        'Most_Common_Crime': most_common_type
    })

top_df = pd.DataFrame(top_with_names)
top_df.to_csv('top_dangerous_locations.csv', index=False)
print("\n✓ Saved: top_dangerous_locations.csv")

# ============================================
# KEY INSIGHTS
# ============================================
print("\n" + "=" * 50)
print("KEY INSIGHTS")
print("=" * 50)

total_crimes = len(df)
print(f"\n1. Total crimes analyzed: {total_crimes:,}")

most_common = pivot1.iloc[0]
print(f"\n2. Most common crime type: {most_common['Crime type']}")
print(f"   - Count: {most_common['Count']:,} ({most_common['Percentage']:.1f}%)")

highest_area = pivot3.iloc[0]
print(f"\n3. Highest crime area: {highest_area['LSOA name']}")
print(f"   - Count: {highest_area['Count']:,} ({highest_area['Percentage']:.1f}%)")

safest_area = pivot3.iloc[-1]
print(f"\n4. Safest area: {safest_area['LSOA name']}")
print(f"   - Count: {safest_area['Count']:,} ({safest_area['Percentage']:.1f}%)")

most_common_outcome = pivot4.iloc[0]
print(f"\n5. Most common outcome: {most_common_outcome['Last outcome category']}")
print(f"   - Count: {most_common_outcome['Count']:,} ({most_common_outcome['Percentage']:.1f}%)")

solved = df[df['Last outcome category'].str.contains('charge|summons|court', case=False, na=False)]
solved_rate = (len(solved) / total_crimes * 100)
print(f"\n6. Cases resulting in charges/court: {len(solved):,} ({solved_rate:.1f}%)")

monthly_avg = df.groupby(df['Month'].dt.to_period('M')).size().mean()
print(f"\n7. Average crimes per month: {monthly_avg:.0f}")

most_dangerous_spot = top_df.iloc[0]
print(f"\n8. Most dangerous single location:")
print(f"   - Area: {most_dangerous_spot['LSOA_Name']}")
print(f"   - Coordinates: ({most_dangerous_spot['Latitude']:.4f}, {most_dangerous_spot['Longitude']:.4f})")
print(f"   - Total crimes: {most_dangerous_spot['Total_Crimes']:,}")
print(f"   - Most common: {most_dangerous_spot['Most_Common_Crime']}")

print("\n" + "=" * 50)
print("ANALYSIS COMPLETE!")
print("=" * 50)
print("\nGenerated files:")
print("✓ chart1_crime_types.png")
print("✓ chart2_monthly_trends.png")
print("✓ chart3_areas.png")
print("✓ chart4_outcomes.png")
print("✓ map1_crime_heatmap.html (INTERACTIVE HEATMAP - RED ZONES!)")
print("✓ map2_crime_markers.html (DANGEROUS LOCATIONS MARKED!)")
print("✓ map3_crime_clusters.html (CLUSTER MAP - ZOOM IN!)")
print("✓ top_dangerous_locations.csv")
print("\n🔥 OPEN THE HTML FILES IN YOUR BROWSER TO SEE REAL MAPS!")
print("   → Red areas = High crime!")
print("   → You can zoom, pan, and click on markers!")