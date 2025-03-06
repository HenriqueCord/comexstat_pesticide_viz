# Brazil Pesticide Importation Dashboard

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://br-comexstat-pesticide-viz.streamlit.app/)  

Interactive dashboard for analyzing Brazil's pesticide import data (1997-2024) with trend visualization, geographical distribution, and product class breakdown.

---

## Features

### **Data Fetching & Processing**
- **API Integration**: Fetches data from the [COMEXSTAT API](https://api-comexstat.mdic.gov.br/general).
- **Data Quality Checks**: Ensures no NaNs or duplicates in the dataset.
- **Data Enrichment**:
  - Adds ISO3 country codes for geographical visualization.
  - Classifies products into categories based on description (e.g., herbicides, fungicides, insecticides).

### **Visualizations**
- **Time Series Analysis**:
  - Monthly import trends with stacked product class breakdown.
- **Geographical Distribution**:
  - Choropleth map showing import volumes by country.
- **Product Class Breakdown**:
  - Bar/pie charts showing composition of imports.
  - Custom color mapping for product classes.
- **Seasonal Decomposition**:
  - Visualizes seasonal and residual components of import trends.

---

## Project Structure

```bash
comexstat_viz/
├── dashboard/
│   ├──  app.py              # Main Streamlit application
│   └──  fetch_data.py       # Data loading and processing logic
│   └──  plots.py            # Plotting fns used in app
├── data/
│   └── processed/          # Processed saved data
├── notebooks/
│   ├── explore_data.ipynb  # Data exploration notebooks
│   └── get_import_data.ipynb
├── setup.py                # Package configuration
├── requirements.txt        # Python dependencies
└── README.md
```

## Installation & Usage
1. **Clone repo**:
  ```bash
git clone https://github.com/your-username/comexstat_viz.git
cd comexstat_viz
```
2. **Install**:
  ```bash
pip install -r requirements.txt
pip install -e .  # Install package in editable mode
```

3.**Run**: 
  ```bash
streamlit comexstat_viz/dashboard/app.py 
```

## Acknowledgments
Data sourced from COMEXSTAT (Brazilian Foreign Trade Portal).

Built with Streamlit, Plotly, and Pandas.
