# Video Walkthrough Outline

## 0:00–0:40 — Business Problem

* Introduce the hotel bar inventory problem.
* Explain that stockouts of popular brands can affect guest service and sales.
* Explain that excessive inventory of slow-moving products ties up working capital and storage.
* State the goal: forecast demand and recommend appropriate inventory par levels for each bar and brand.

## 0:40–1:20 — Dataset and Data Preparation

* Show the project structure and dataset.
* Explain that the dataset contains inventory transactions across 6 bars and 16 brands.
* Show the main fields: opening balance, purchases, consumption, and closing balance.
* Explain the inventory conservation check.
* Explain that transaction records were aggregated into daily consumption by bar and brand.
* Mention that missing bar-brand dates were represented as zero consumption.

## 1:20–2:10 — Demand Forecasting

* Show the forecasting section of the notebook.
* Explain the highly intermittent demand pattern.
* Mention the lag features:

  * Previous day
  * 7-day lag
  * 14-day lag
  * Previous 7-day average
  * Day of week
* Explain the chronological train-test split.
* Introduce the Random Forest model.
* Explain that a 7-day lag forecast was used as a simple baseline.

## 2:10–2:50 — Model Results

* Show the model evaluation results.
* Random Forest MAE: 98.42 ml.
* 7-day lag baseline MAE: 97.37 ml.
* Explain that the simple baseline was slightly better overall.
* Mention that Random Forest performed better on days with actual non-zero demand.
* Explain that the high WAPE reflects the highly intermittent demand in the dataset.

## 2:50–3:35 — Par Level and Inventory Simulation

* Show the inventory recommendation section.
* Explain that the recommended par level combines expected lead-time demand and safety stock.
* State the 3-day lead-time assumption and 95% service-level assumption.
* Explain that demand statistics were calculated from the training period.
* Show the historical backtesting process.
* Mention the simulated results:

  * 114 simulated stockout days
  * Approximately 811 ml average simulated inventory

## 3:35–4:10 — Business Insights and Limitations

* Show the stockout and overstock analysis.
* Explain that these are potential risk signals rather than confirmed financial stockouts or overstock costs.
* Mention that the current simulation does not include supplier constraints, minimum order quantities, variable lead times, promotions, or holidays.
* Explain that intermittent-demand forecasting methods could be explored in future versions.

## 4:10–4:30 — Conclusion

* Summarize the end-to-end workflow:

  * Data preparation
  * Demand forecasting
  * Par-level recommendation
  * Inventory backtesting
  * Risk analysis
* Explain that the solution provides a structured starting point for inventory planning and could be extended with richer operational data for production use.
