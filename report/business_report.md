# Hotel Bar Inventory Forecasting & Par Level Recommendation System

## 1. Business Problem & Operational Impact

The hotel chain operates multiple bars where inventory availability must be balanced against excess stock. Two operational problems are important:

* **Stockouts of high-demand products:** Running out of popular brands can affect guest experience, reduce sales opportunities, and interrupt bar operations.
* **Overstocking of slow-moving products:** Excess inventory ties up working capital, occupies storage space, and can increase the risk of shrinkage or wastage.

The objective of this project is to transform transaction-level bottle balance records into daily consumption time series, forecast demand for each bar-brand combination, recommend inventory par levels, and evaluate the replenishment policy through historical backtesting.

The dataset contains **6 bars and 16 brands**, covering approximately one year from January 2023 to January 2024.

---

## 2. Data Preparation & Assumptions

The raw records contain:

* Date Time Served
* Bar Name
* Alcohol Type
* Brand Name
* Opening Balance
* Purchase
* Consumed
* Closing Balance

The timestamp was converted to a proper datetime format, and consumption was aggregated to **daily consumption by bar and brand**.

The inventory conservation relationship was also checked:

**Closing Balance = Opening Balance + Purchase − Consumed**

Most records matched this relationship closely. Small differences were observed in a limited number of records and were retained because they are consistent with possible measurement or rounding differences.

A complete daily grid of all **Date × Bar × Brand** combinations was created so that missing combinations were explicitly represented as zero consumption. This is important because the dataset contains highly intermittent demand: **83.98% of daily bar-brand records had zero consumption**.

### Key assumptions

* Supplier lead time is assumed to be a constant **3 days**.
* A **95% service level** is used, corresponding to Z = **1.645**.
* Missing bar-brand combinations on a date represent zero recorded consumption.
* The backtest uses actual observed test-period demand.
* The inventory simulation assumes replenishment toward the recommended par level and does not model supplier capacity, minimum order quantities, or variable delivery times.

---

## 3. Demand Forecasting Approach

A chronological train-test split was used so that future observations were not used to train the model. The forecasting features include:

* Previous-day consumption
* 7-day lag consumption
* 14-day lag consumption
* Previous 7-day average consumption
* Day of week
* Bar and brand information

A **Random Forest Regressor** was selected as the predictive model because it can capture nonlinear relationships between lagged demand, calendar information, bar, and brand without requiring a strong linearity assumption.

A simple **7-day lag baseline** was also implemented as a practical benchmark. This comparison is important because intermittent demand can make simple seasonal or lag-based methods surprisingly competitive.

The rolling feature was calculated using only previous observations to avoid data leakage.

---

## 4. Model Performance & Failure Modes

The evaluation used **MAE** and **WAPE**, which are appropriate for this problem because WAPE avoids the division-by-zero issue associated with MAPE when demand is zero.

| Metric             | Random Forest | 7-Day Lag Baseline |
| ------------------ | ------------: | -----------------: |
| Overall MAE        |      98.42 ml |           97.37 ml |
| Overall WAPE       |       176.85% |            174.98% |
| MAE on demand days |     281.97 ml |          320.37 ml |

The 7-day lag baseline performed slightly better on the overall test set. However, on days where actual consumption occurred, the Random Forest produced lower MAE than the baseline.

This difference highlights a major limitation of the dataset: demand is highly intermittent, with most daily observations equal to zero. The high WAPE values should therefore be interpreted in the context of sparse demand rather than as evidence that the model is unusable.

The current Random Forest model can also produce positive predictions on some zero-demand days. A production system could improve this by using forecasting methods specifically designed for intermittent demand or by combining demand-occurrence and demand-size modeling.

---

## 5. Dynamic Par Level & Inventory Backtesting

The recommended inventory level follows the assignment's safety-stock framework:

**Par Level = Lead-Time Demand + Safety Stock**

For a 3-day lead time:

**Lead-Time Demand = Average Daily Demand × 3**

**Safety Stock = 1.645 × Daily Demand Standard Deviation × √3**

The demand statistics used for the final inventory recommendation were calculated from the **training period only**, preventing information from the test period from influencing the recommended inventory levels.

The replenishment policy was then evaluated using a daily inventory simulation over the test period. The simulation:

1. Starts inventory at the recommended par level.
2. Receives previously placed replenishment orders.
3. Deducts actual daily consumption.
4. Records a stockout when available inventory is insufficient.
5. Places an order to replenish inventory toward the recommended par level.
6. Applies the assumed 3-day delivery delay.

### Backtest results

* **Simulated stockout days:** 114
* **Average simulated inventory:** 811.36 ml

The analysis also identified **potential overstock days**, defined as days where observed closing inventory exceeded the recommended par level. These are inventory-risk signals rather than confirmed financial overstock because carrying costs and actual purchasing constraints were not available.

---

## 6. Business Implications

The analysis provides bar managers with a structured way to identify demand patterns and set inventory buffers by bar and brand rather than relying only on fixed manual stock levels.

The results also demonstrate that inventory planning and forecasting should account for the intermittent nature of alcohol consumption. A simple 7-day baseline remains competitive overall, while the Random Forest provides better error performance specifically on days when demand occurs.

The recommended par levels can therefore serve as a starting point for operational replenishment, with further validation against actual purchasing and stockout records before production deployment.

---

## 7. Production Considerations & Future Improvements

A production version could run automatically each day after new POS or inventory data becomes available. The system could generate updated forecasts and recommended reorder quantities for each bar-brand combination and present them through a manager dashboard.

Important production considerations include:

* **Variable supplier lead times:** The current model assumes a fixed 3-day lead time.
* **Promotions and events:** Holidays, weekends, hotel events, and promotions can cause demand spikes that historical lags alone may not capture.
* **Operational constraints:** Minimum order quantities, supplier capacity, delivery schedules, and storage limits should be incorporated.
* **Measurement differences:** Pouring waste, breakage, spillage, and inventory-count discrepancies can affect recorded consumption.
* **Demand drift:** Consumption patterns may change over time and should be monitored.

Future modeling improvements could include intermittent-demand forecasting methods such as Croston-style approaches, Exponential Smoothing, or more advanced models after establishing appropriate validation procedures.

For production monitoring, forecast errors such as MAE/WAPE should be tracked continuously, while demand distributions and feature patterns should be monitored for data drift. Actual stockouts and reorder outcomes should also be fed back into the system for periodic model and inventory-policy evaluation.
