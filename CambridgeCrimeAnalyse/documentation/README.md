# Cambridge Crime Data Analysis

Professional crime data analysis and visualization project for Cambridge, UK.

## 📊 Project Overview

This project analyzes 12 months of crime data from Cambridge, generating:
- Statistical reports and pivot tables
- Professional visualizations (charts)
- Interactive crime maps (heatmaps, markers, clusters)
- Detailed area-level crime statistics

## 🗂️ Project Structure

```
CambridgeCrimeAnalyse/
├── data/
│   └── raw/
│       └── merged_file.csv          # Input crime data
├── scripts/
│   ├── config.py                    # Configuration management
│   ├── data_loader.py               # Data loading & cleaning
│   ├── report_generator.py          # Statistical analysis
│   ├── map_generator.py             # Interactive map generation
│   ├── main.py                      # Main execution script
│   └── config.ini                   # Configuration file
├── output/
│   ├── charts/                      # PNG visualizations
│   ├── maps/                        # Interactive HTML maps
│   ├── data/                        # Processed CSV files
│   └── reports/                     # Text reports
├── docs/                            # Documentation (GitHub Pages)
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/CambridgeCrimeAnalyse.git
   cd CambridgeCrimeAnalyse
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your data:**
   - Place your `merged_file.csv` in the `data/raw/` folder
   - The CSV should contain columns: Crime ID, Month, Crime type, Location, LSOA name, Latitude, Longitude, Last outcome category

### Running the Analysis

From the project root directory:

```bash
cd scripts
python main.py
```

The script will:
1. Load and clean the data
2. Generate statistical reports and charts
3. Create interactive maps
4. Save all outputs to the `output/` directory

## 📈 Outputs

### Charts (PNG files)
- **chart1_crime_types.png** - Top 10 crime types
- **chart2_monthly_trends.png** - Monthly trends for top 5 crimes
- **chart3_areas.png** - Top 15 high-crime areas
- **chart4_outcomes.png** - Distribution of crime outcomes

### Interactive Maps (HTML files)
- **map1_crime_heatmap.html** - Crime density heatmap
- **map2_crime_markers.html** - High-crime location markers
- **map3_crime_clusters.html** - Clustered map with area statistics

### Data Files
- **top_dangerous_locations.csv** - Top 20 most dangerous coordinates

### Reports
- **summary_statistics.txt** - Key insights and statistics

## 🔧 Configuration

Edit `scripts/config.ini` to customize:

```ini
[Settings]
# Path to data folder (relative to scripts folder)
folder_path = ../data/raw

# Data file name
data_file = merged_file.csv
```

## 📊 Key Features

- **Modular Design**: Separated into logical components (data loading, analysis, visualization)
- **Error Handling**: Graceful handling of missing data and files
- **Logging**: Detailed logging to `crime_analysis.log`
- **Relative Paths**: Works from any directory
- **Professional Output**: Clean, organized file structure
- **Interactive Maps**: Zoom, pan, and click for details

## 🛠️ Customization

### Adding New Analysis

Edit `scripts/report_generator.py` to add new pivot tables or charts.

### Modifying Maps

Edit `scripts/map_generator.py` to customize map styles, colors, or markers.

### Changing Output Locations

Edit `scripts/config.py` to modify output directory structure.

## 📝 Data Format

The input CSV should have the following columns:

| Column | Description |
|--------|-------------|
| Crime ID | Unique identifier |
| Month | Date (YYYY-MM-DD) |
| Crime type | Type of crime |
| Location | Street location |
| LSOA name | Area name |
| Latitude | Geographic coordinate |
| Longitude | Geographic coordinate |
| Last outcome category | Investigation outcome |

## 🌐 GitHub Pages Deployment

To publish your interactive report:

1. Push your code to GitHub
2. Go to Settings → Pages
3. Select branch: `main`
4. Select folder: `/docs`
5. Save

Your report will be live at: `https://yourusername.github.io/CambridgeCrimeAnalyse/`

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

Your Name
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgments

- Crime data sourced from [UK Police Data](https://data.police.uk/)
- Map visualizations powered by [Folium](https://python-visualization.github.io/folium/)

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This project is for educational and analytical purposes only.