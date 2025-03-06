# Brazil Pesticide Importation Dashboard

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://br-comexstat-pesticide-viz.streamlit.app/)  

Interactive dashboard for analyzing Brazil's pesticide import data (1997-2024) with trend visualization, geographical distribution, and product class breakdown.

![Dashboard Preview](![newplot](https://github.com/user-attachments/assets/6999b43a-c0c9-4e5d-bd7a-91e1cfd8059c))  

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
