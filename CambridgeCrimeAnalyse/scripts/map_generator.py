import folium
from folium.plugins import HeatMap, MarkerCluster
import numpy as np
import pandas as pd
import logging


class MapGenerator:
    """Generates interactive crime maps."""

    def __init__(self, df_map, config):
        self.df_map = df_map
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Calculate map center
        self.center_lat = df_map['Latitude'].mean()
        self.center_lon = df_map['Longitude'].mean()

    def create_heatmap(self):
        """Create crime density heatmap."""
        self.logger.info("Creating crime heatmap...")

        # Create base map
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # Prepare heatmap data
        heat_data = [[row['Latitude'], row['Longitude']]
                     for idx, row in self.df_map.iterrows()]

        # Add heatmap layer
        HeatMap(
            heat_data,
            min_opacity=0.3,
            max_opacity=0.8,
            radius=15,
            blur=20,
            gradient={0.0: 'yellow', 0.5: 'orange', 1.0: 'red'}
        ).add_to(m)

        # Save map
        output_path = self.config.get_output_path('maps', 'map1_crime_heatmap.html')
        m.save(output_path)
        self.logger.info(f"Saved: {output_path}")

    def create_marker_map(self):
        """Create map with markers for high-crime locations."""
        self.logger.info("Creating marker map...")

        # Calculate crime density per location
        location_counts = self.df_map.groupby(
            ['Latitude', 'Longitude']
        ).size().reset_index(name='Crimes')

        # Get top dangerous locations
        top_locations = location_counts.nlargest(20, 'Crimes')

        # Create map
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # Add markers
        for idx, row in top_locations.iterrows():
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
            ).add_to(m)

        # Save map
        output_path = self.config.get_output_path('maps', 'map2_crime_markers.html')
        m.save(output_path)
        self.logger.info(f"Saved: {output_path}")

        # Also save top locations to CSV
        self._save_top_locations(top_locations)

    def _save_top_locations(self, top_locations):
        """Save top dangerous locations to CSV."""
        # Add area names and crime types
        top_with_names = []
        for idx, loc in top_locations.iterrows():
            crimes_here = self.df_map[
                (self.df_map['Latitude'] == loc['Latitude']) &
                (self.df_map['Longitude'] == loc['Longitude'])
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
        output_path = self.config.get_output_path('data', 'top_dangerous_locations.csv')
        top_df.to_csv(output_path, index=False)
        self.logger.info(f"Saved: {output_path}")

    def create_cluster_map(self):
        """Create clustered map with area statistics."""
        self.logger.info("Creating cluster map...")

        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=13,
            tiles='OpenStreetMap'
        )

        # Create marker cluster
        marker_cluster = MarkerCluster(
            name='Crime Locations',
            overlay=True,
            control=True,
        ).add_to(m)

        # Sample data to avoid too many markers
        sample_size = min(5000, len(self.df_map))
        df_sample = self.df_map.sample(n=sample_size, random_state=42)

        # Add markers to cluster
        for idx, row in df_sample.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=3,
                popup=f"<b>Crime Type:</b> {row['Crime type']}<br>"
                      f"<b>Date:</b> {row['Month']}<br>"
                      f"<b>Location:</b> {row['Location']}",
                color='red',
                fill=True,
                fillColor='red',
                fillOpacity=0.6
            ).add_to(marker_cluster)

        # Add area statistics
        area_stats = self.df_map.groupby('LSOA name').agg({
            'Latitude': 'mean',
            'Longitude': 'mean',
            'Crime ID': 'count'
        }).reset_index()
        area_stats.columns = ['LSOA_name', 'Lat', 'Lon', 'Crime_Count']
        area_stats = area_stats.sort_values('Crime_Count', ascending=False)

        # Add circles for each LSOA area
        for idx, row in area_stats.iterrows():
            radius = np.sqrt(row['Crime_Count']) * 20

            if row['Crime_Count'] > area_stats['Crime_Count'].quantile(0.75):
                color = 'darkred'
                fill_color = 'red'
            elif row['Crime_Count'] > area_stats['Crime_Count'].quantile(0.5):
                color = 'orange'
                fill_color = 'orange'
            else:
                color = 'yellow'
                fill_color = 'yellow'

            # Get crime breakdown
            area_crimes = self.df_map[self.df_map['LSOA name'] == row['LSOA_name']]
            crime_breakdown = area_crimes['Crime type'].value_counts().head(5)
            breakdown_html = "<br>".join([f"• {crime}: {count}"
                                          for crime, count in crime_breakdown.items()])

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
            ).add_to(m)

            # Add labels for top 10 areas
            if idx < 10:
                folium.Marker(
                    location=[row['Lat'], row['Lon']],
                    icon=folium.DivIcon(html=f"""
                        <div style='
                            font-size: 14px; 
                            font-weight: bold; 
                            color: white; 
                            text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, 
                                        -1px 1px 0 #000, 1px 1px 0 #000;
                            text-align: center;
                        '>
                            {row['Crime_Count']}
                        </div>
                    """)
                ).add_to(m)

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
            <p style="margin: 5px 0; font-size: 12px;">Circle size = Crime count<br>
            Numbers = Total crimes in area</p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        # Save map
        output_path = self.config.get_output_path('maps', 'map3_crime_clusters.html')
        m.save(output_path)
        self.logger.info(f"Saved: {output_path}")

    def generate_all_maps(self):
        """Generate all interactive maps."""
        self.create_heatmap()
        self.create_marker_map()
        self.create_cluster_map()

