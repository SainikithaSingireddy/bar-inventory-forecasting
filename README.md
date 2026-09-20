# Bar Inventory Forecasting and Inventory Recommendation System

## Project Overview

This project develops a demand forecasting and inventory recommendation system for a hotel bar environment. It uses historical alcohol inventory and consumption records across multiple bars and brands to forecast demand, calculate recommended inventory par levels, and evaluate a replenishment policy through historical backtesting.

The goal is to help reduce stockout risk while avoiding unnecessarily high inventory levels for slow-moving products.

## Business Objectives

* Forecast daily alcohol consumption for each bar and brand
* Calculate dynamic inventory par levels using demand and demand variability
* Simulate inventory replenishment using a 3-day lead time
* Identify potential stockout and overstock risks
* Compare a machine-learning forecast with a simple 7-day lag baseline

## Dataset

The dataset contains transaction-level inventory records with the following fields:

* Date Time Served
* Bar Name
* Alcohol Type
* Brand Name
* Opening Balance (ml)
* Purchase (ml)
* Consumed (ml)
* Closing Balance (ml)

The data covers approximately one year, from January 2023 to January 2024, across:

* 6 bars
* 16 brands
* 366 calendar days

Daily consumption was aggregated by bar, brand, and date. Missing bar-brand combinations were explicitly added to the daily dataset and treated as zero consumption.

## Technology Stack

* Python 3.11
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Scikit-learn
* Statsmodels
* Jupyter Notebook

## Project Structure

```text
bar_inventory_project/
│
├── data/
│   ├── raw/
│   │   └── bar_inventory_data.csv
│   │
│   └── processed/
│       ├── daily_bar_consumption.csv
│       ├── inventory_simulation.csv
│       ├── metrics_summary.csv
│       ├── overstock_summary.csv
│       └── stockout_by_item.csv
│
├── notebooks/
│   └── inventory_forecasting_solution.ipynb
│
├── report/
│   ├── actual_vs_predicted.png
│   ├── business_report.md
│   ├── business_report.pdf
│   └── consumption_by_brand.png
│
├── video_script/
│
├── .gitignore
├── README.md
└── requirements.txt
```

> The local `venv/` folder is used for development but is excluded from version control through `.gitignore`.

## Methodology

### 1. Data Preparation

Transaction-level inventory records were converted into daily consumption by bar and brand.

The inventory conservation relationship was also checked using:

```text
Closing Balance = Opening Balance + Purchase - Consumed
```

Most records followed the expected relationship, with a small number of differences attributed to measurement or rounding variation.

A complete daily bar-brand grid was created so that days without recorded consumption were represented explicitly as zero consumption.

### 2. Exploratory Data Analysis

The analysis includes:

* Daily consumption patterns
* Consumption by bar
* Consumption by brand
* ABC-style consumption classification
* Demand coverage across bar-brand combinations
* Potential historical stockout signals
* Potential overstock days

The dataset has highly intermittent demand, with approximately 83.98% of model records showing zero daily consumption.

### 3. Feature Engineering

The forecasting model uses:

* Previous-day consumption (`Lag_1`)
* 7-day lag consumption (`Lag_7`)
* 14-day lag consumption (`Lag_14`)
* Previous 7-day average consumption
* Day of week
* Bar name
* Brand name

Rolling features were calculated using only previous observations to avoid using future information during forecasting.

### 4. Demand Forecasting

A chronological train-test split was used rather than random cross-validation.

Two forecasting approaches were evaluated:

**Random Forest Regressor**

The Random Forest model was trained using lag features, rolling demand, day-of-week information, and bar/brand identifiers.

**7-Day Lag Baseline**

The previous week's consumption was used as a simple baseline forecast.

The baseline remained competitive because demand in the dataset is highly intermittent.

### 5. Inventory Recommendation

Recommended inventory levels were calculated using:

```text
Par Level = Lead-Time Demand + Safety Stock
```

A 3-day lead time and a 95% service-level z-value of 1.645 were used.

Lead-time demand was calculated from average daily demand:

```text
Lead-Time Demand = Average Daily Demand × Lead Time
```

Safety stock was based on demand variability:

```text
Safety Stock = Z × Demand Standard Deviation × √Lead Time
```

Demand statistics used for the recommendation were calculated from the training period to avoid test-period leakage.

### 6. Inventory Backtesting

The replenishment policy was evaluated using the test-period demand.

The simplified simulation:

* Starts inventory at the recommended par level
* Deducts daily demand
* Records a stockout when simulated inventory falls below zero
* Places replenishment orders when inventory is below the recommended level
* Receives orders after the simulated 3-day lead time

The simulation does not model supplier capacity limits, minimum order quantities, variable lead times, or actual procurement constraints.

## Results

| Metric                           |     Value |
| -------------------------------- | --------: |
| Random Forest MAE                |  98.42 ml |
| 7-Day Lag Baseline MAE           |  97.37 ml |
| Random Forest WAPE               |   176.85% |
| Baseline WAPE                    |   174.98% |
| Random Forest MAE on Demand Days | 281.97 ml |
| Total Simulated Stockout Days    |       114 |
| Average Simulated Inventory      | 811.36 ml |

### Model Observations

* The simple 7-day lag baseline achieved a slightly lower overall MAE than Random Forest.
* Random Forest performed better than the baseline on days when actual consumption was non-zero.
* The high WAPE is influenced by the large number of zero-demand observations and the intermittent nature of consumption.
* These results suggest that specialized intermittent-demand forecasting methods could be investigated for future improvements.

## Inventory Risk Analysis

The project identifies:

* Bar-brand combinations with simulated stockout days during the backtest
* Days where observed closing inventory exceeded the recommended par level

These are treated as **potential risk signals**, not confirmed financial stockouts or overstock costs.

## Key Business Insights

* Demand varies significantly across bar-brand combinations.
* High-volume brands require greater inventory buffers.
* Intermittent demand makes forecasting challenging and can make simple baselines surprisingly competitive.
* Par levels should account for both expected lead-time demand and demand variability.
* Inventory recommendations should be validated against actual operational constraints before production deployment.

## Limitations

The current solution uses a simplified inventory model and has several limitations:

* Fixed 3-day lead time
* No supplier capacity constraints
* No minimum order quantities
* No variable supplier lead times
* No promotions or special events
* No holiday features
* No external demand drivers
* No actual procurement costs
* No financial holding-cost calculation
* Potential stockout signals are not necessarily confirmed stockouts

## Future Improvements

Future versions could include:

* Intermittent-demand forecasting methods such as Croston-style approaches
* Exponential Smoothing and other statistical models
* More detailed calendar and seasonal features
* Holiday and event information
* Promotion and sales-event indicators
* Actual supplier lead-time data
* Minimum order quantities and supplier constraints
* Inventory holding and ordering costs
* Automated model monitoring
* Daily production forecasting pipelines
* Model performance monitoring and retraining

## How to Run

### 1. Clone or Download the Project

Open the project folder in a terminal.

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch Jupyter Notebook

```bash
jupyter notebook
```

Open:

```text
notebooks/inventory_forecasting_solution.ipynb
```

Run the notebook cells from top to bottom.

## Files

* `data/raw/bar_inventory_data.csv` — Original transaction-level dataset
* `data/processed/` — Processed datasets and analysis results
* `notebooks/inventory_forecasting_solution.ipynb` — Complete data analysis, forecasting, inventory recommendation, and backtesting workflow
* `report/business_report.pdf` — Final business report
* `report/business_report.md` — Editable report source
* `report/consumption_by_brand.png` — Brand consumption visualization
* `report/actual_vs_predicted.png` — Forecast comparison visualization
* `requirements.txt` — Python dependencies
* `.gitignore` — Files excluded from version control

## Conclusion

This project demonstrates an end-to-end approach to hotel bar inventory forecasting and replenishment planning. It combines data preparation, exploratory analysis, demand forecasting, safety-stock calculation, par-level recommendation, and historical inventory backtesting.

The results highlight the challenges of intermittent demand and show why both forecasting accuracy and inventory behavior should be evaluated before deploying an inventory recommendation system in production.
