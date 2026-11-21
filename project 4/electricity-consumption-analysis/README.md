# Household Electricity Consumption Analysis

**Roll number:** 2026B01010250 | **Tools:** Python, pandas, NumPy, matplotlib, seaborn | **Data:** synthetic (computer-generated) practice data, random seed 10250

## Business problem
A state electricity distribution company wants to understand why some households use far more electricity than others. The planning team needs this analysis to forecast demand and to find high-usage homes for energy-saving campaigns and better tariff offers. The outcome column is `Monthly_Units_kWh`.

## Questions
1. What does `Monthly_Units_kWh` look like overall?
2. Do `Home_Area_Sqft` and `Num_Air_Conditioners` affect `Monthly_Units_kWh`?
3. Does `Monthly_Units_kWh` differ by `City`, `Housing_Type` and `Tariff_Plan`?
4. Which households need attention? (**High Consumer** = more than 300 kWh in a month)

## Data dictionary

| Column | Type | Meaning | Valid values / range |
|---|---|---|---|
| Household_ID | text | Unique household identifier | E1001 to E1250 |
| City | category | City of the household | Delhi, Mumbai, Bengaluru, Chennai, Kolkata |
| Housing_Type | category | Type of dwelling | Apartment, Independent House, Villa |
| Tariff_Plan | category | Tariff plan | Standard, Time_of_Day, Solar_Net_Metering |
| Household_Size | integer | People living in the home | 1 to 8 |
| Home_Area_Sqft | integer | Built-up area (sq ft) | about 400 to 3500 |
| Num_Air_Conditioners | integer | Number of ACs | 0 to 4 |
| Avg_Temperature_C | decimal | Average outside temperature in the billing month (°C) | about 10 to 40 |
| Meter_Age_Years | integer | Age of the meter (years) | 0 to 10 |
| Billing_Date | date | Bill date (YYYY-MM-DD) | within the last two years |
| Monthly_Units_kWh | integer | Electricity used in the month (kWh), main outcome | about 40 to 500 |

## Project structure
```
electricity-consumption-analysis/
├── data/
│   ├── raw/electricity_data.csv              (file from the AI, not edited by hand)
│   └── processed/electricity_data_clean.csv  (saved by the notebook after cleaning)
├── notebooks/electricity_consumption_analysis.ipynb
├── images/                                   (6 charts saved by the notebook)
├── requirements.txt
└── README.md
```

## Steps
1. **Load and inspect:** `head`, `info`, `describe`, missing values, duplicates, category values.
2. **Clean:** removed 5 duplicate rows; made `City` text consistent (spaces and capital letters); turned impossible negative `Household_Size` values into missing; filled missing values with the mode or a group median (housing type for area, city for temperature, overall median for meter age and household size). Result: 250 unique households, no missing values.
3. **New columns:** `Units_Per_Sqft`, `Consumption_Level`, `High_Consumer`, `Area_Band`, `Estimated_Bill_Rs` (assumed Rs 7 per unit), `Billing_Month`.
4. **Analyse** each question with tables and charts.
5. **Insights and recommendations**, then save the cleaned file.

## Key findings
- Average usage is **214.5 kWh** a month (median 215); half of households use between 161 and 267 kWh.
- **Number of ACs is the strongest driver** (correlation 0.57): usage rises from 146 kWh with no AC to 298 kWh with 3 ACs.
- **Home area** also matters (correlation 0.41): large homes average 261 kWh vs 185 kWh for small homes.
- `Meter_Age_Years` (0.08), `Avg_Temperature_C` (0.06) and `Household_Size` (0.15) show little relationship with usage.
- **Villas** average 278 kWh vs 197 kWh for apartments; **solar net-metering** homes average 175 kWh vs 221 kWh on the standard tariff; **Chennai** is highest (239 kWh) and **Kolkata** lowest (174 kWh).
- **34 households (13.6%)** are High Consumers. 41% of villas and 45% of homes with 3 ACs fall in this group.

## Charts

| | |
|---|---|
| ![Distribution](images/01_units_distribution.png) | ![Area](images/02_area_vs_units.png) |
| ![ACs](images/03_acs_vs_units.png) | ![Correlation](images/04_correlation_heatmap.png) |
| ![Groups](images/05_units_by_category.png) | ![High consumers](images/06_high_consumers.png) |

## Recommendations
1. Target homes with 3 or more ACs first (AC replacement offers, smart-thermostat tips, usage alerts).
2. Focus campaigns and energy audits on villas and large homes.
3. Promote solar net-metering, since those homes use about 46 kWh less.
4. Review tariffs for High Consumers; time-of-day homes currently use about as much as standard homes.
5. Forecast demand by city and AC count instead of one average.
6. Do not use meter age or household size for targeting.

## How to run
```
pip install -r requirements.txt
jupyter notebook notebooks/electricity_consumption_analysis.ipynb
```
Run the notebook from top to bottom. It reads `data/raw/electricity_data.csv` and writes the charts and the cleaned file.

*Note: the data is synthetic, so the patterns illustrate the method and are not real findings about any company or person.*
