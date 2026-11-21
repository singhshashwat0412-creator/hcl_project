# Household Electricity Consumption Analysis (roll no. 2026B01010250)
# Run:  python electricity_consumption_analysis.py   (works from any folder)

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
np.random.seed(10250)   # last 6 digits of my roll number

os.makedirs(BASE + "/images", exist_ok=True)
os.makedirs(BASE + "/data/processed", exist_ok=True)

# simple, readable chart style
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "axes.edgecolor": GRID,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "figure.dpi": 110,
})
print(pd.set_option("display.max_columns", None))

df = pd.read_csv(BASE + "/data/raw/electricity_data.csv")
print("Rows, columns:", df.shape)
print(df.head())

df.info()

print(df.describe())

print("Missing values per column:")
print(df.isna().sum())
print()
print("Duplicate rows:", df.duplicated().sum())
print()
for col in ["City", "Housing_Type", "Tariff_Plan"]:
    print(col, "->", df[col].value_counts(dropna=False).to_dict())
print()
print("Household_Size values below 1:", (df["Household_Size"] < 1).sum())

rows_before = len(df)

# 1) Duplicates: an exact copy is the same household counted twice, so I drop the copies.
print("Duplicate rows removed:", df.duplicated().sum())
df = df.drop_duplicates().reset_index(drop=True)

# 2) Inconsistent text: remove extra spaces and make the capital letters the same.
print("City values before:", sorted(df["City"].unique()))
for col in ["City", "Housing_Type", "Tariff_Plan"]:
    df[col] = df[col].str.strip()
df["City"] = df["City"].str.title()
print("City values after: ", sorted(df["City"].unique()))

# 3) Impossible values: a negative household size cannot be true.
#    I treat them as missing (NaN) and fill them together with the other missing values.
bad_size = df["Household_Size"] < 1
print(df.loc[bad_size, ["Household_ID", "Household_Size"]])
df.loc[bad_size, "Household_Size"] = np.nan

# 4) Missing values
print("Missing before:")
print(df.isna().sum()[df.isna().sum() > 0])

# Housing_Type is a category, so I use the most common value (mode).
df["Housing_Type"] = df["Housing_Type"].fillna(df["Housing_Type"].mode()[0])

# Area depends on the housing type (villas are bigger than apartments), so I use the median of the same type.
df["Home_Area_Sqft"] = df["Home_Area_Sqft"].fillna(df.groupby("Housing_Type")["Home_Area_Sqft"].transform("median"))

# Temperature depends on the city, so I use the median temperature of the same city.
df["Avg_Temperature_C"] = df["Avg_Temperature_C"].fillna(df.groupby("City")["Avg_Temperature_C"].transform("median"))

# Meter age and household size: the overall median (it is not pulled by extreme values).
df["Meter_Age_Years"] = df["Meter_Age_Years"].fillna(df["Meter_Age_Years"].median())
df["Household_Size"] = df["Household_Size"].fillna(df["Household_Size"].median())

# Fix the data types again after filling
for col in ["Household_Size", "Home_Area_Sqft", "Meter_Age_Years"]:
    df[col] = df[col].round().astype(int)
df["Avg_Temperature_C"] = df["Avg_Temperature_C"].round(1)
df["Billing_Date"] = pd.to_datetime(df["Billing_Date"])

print()
print("Missing after:", int(df.isna().sum().sum()))
print("Rows before / after cleaning:", rows_before, "/", len(df))
print("Unique Household_ID:", df["Household_ID"].nunique())

# 1) Combine two columns: how many units per square foot
df["Units_Per_Sqft"] = (df["Monthly_Units_kWh"] / df["Home_Area_Sqft"]).round(3)

# 2) Labels with conditions
df["Consumption_Level"] = np.select(
    [df["Monthly_Units_kWh"] <= 150, df["Monthly_Units_kWh"] <= 300],
    ["Low", "Medium"], default="High")
df["High_Consumer"] = np.where(df["Monthly_Units_kWh"] > 300, "Yes", "No")

# 3) Bin a numeric column: size band for the home
df["Area_Band"] = pd.cut(df["Home_Area_Sqft"], bins=[0, 800, 1500, 4000],
                         labels=["Small (up to 800)", "Medium (801-1500)", "Large (above 1500)"]).astype(str)

# 4) Estimated bill, assuming a flat Rs 7 per unit (my own simple assumption)
df["Estimated_Bill_Rs"] = (df["Monthly_Units_kWh"] * 7).round().astype(int)

# 5) Month number from the date
df["Billing_Month"] = df["Billing_Date"].dt.month

print(df[["Household_ID", "Monthly_Units_kWh", "Units_Per_Sqft", "Consumption_Level",
    "High_Consumer", "Area_Band", "Estimated_Bill_Rs", "Billing_Month"]].head())

units = df["Monthly_Units_kWh"]
summary = units.describe().round(1)
summary["skewness"] = round(units.skew(), 2)
print(summary)

fig, ax = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [3, 1.2]})

ax[0].hist(units, bins=20, color=BLUE, edgecolor="white", linewidth=1.2)
ax[0].axvline(units.mean(), color=INK, linewidth=1.5)
ax[0].text(units.mean() + 4, ax[0].get_ylim()[1] * 0.93, f"Mean {units.mean():.0f} kWh", color=INK, fontsize=9)
ax[0].set_title("Most households use 160 to 270 kWh a month")
ax[0].set_xlabel("Monthly units (kWh)")
ax[0].set_ylabel("Number of households")

ax[1].boxplot(units, vert=True, widths=0.5, patch_artist=True,
              boxprops=dict(facecolor=BLUE, alpha=0.35, edgecolor=BLUE),
              medianprops=dict(color=INK, linewidth=1.5),
              whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
              flierprops=dict(marker="o", markerfacecolor=BLUE, markeredgecolor="white", markersize=6))
ax[1].set_title("Spread and outliers")
ax[1].set_xticks([])
ax[1].set_ylabel("Monthly units (kWh)")
plt.tight_layout()
plt.savefig(BASE + "/images/01_units_distribution.png", dpi=150, bbox_inches="tight")
plt.close()

num_cols = ["Household_Size", "Home_Area_Sqft", "Num_Air_Conditioners", "Avg_Temperature_C", "Meter_Age_Years"]
corr_table = df[num_cols + ["Monthly_Units_kWh"]].corr()["Monthly_Units_kWh"].drop("Monthly_Units_kWh").sort_values(ascending=False).round(2)
print(corr_table.to_frame("Correlation with Monthly_Units_kWh"))

r_area = df["Home_Area_Sqft"].corr(df["Monthly_Units_kWh"])

fig, ax = plt.subplots(figsize=(7.5, 4.6))
sns.regplot(data=df, x="Home_Area_Sqft", y="Monthly_Units_kWh", ax=ax,
            scatter_kws=dict(alpha=0.6, s=28, color=BLUE, edgecolor="white", linewidths=0.6),
            line_kws=dict(color=ORANGE, linewidth=2), ci=None)
ax.set_title(f"Bigger homes use more electricity (r = {r_area:.2f})")
ax.set_xlabel("Home area (sq ft)")
ax.set_ylabel("Monthly units (kWh)")
plt.tight_layout()
plt.savefig(BASE + "/images/02_area_vs_units.png", dpi=150, bbox_inches="tight")
plt.close()

ac_table = df.groupby("Num_Air_Conditioners")["Monthly_Units_kWh"].agg(["count", "mean", "median"]).round(1)
print(ac_table)

fig, ax = plt.subplots(figsize=(7.5, 4.4))
bars = ax.bar(ac_table.index.astype(str), ac_table["mean"], color=BLUE, width=0.6)
for b, (n, m) in zip(bars, zip(ac_table["count"], ac_table["mean"])):
    ax.text(b.get_x() + b.get_width() / 2, m + 4, f"{m:.0f}", ha="center", color=INK, fontsize=9)
    ax.text(b.get_x() + b.get_width() / 2, 6, f"n={n}", ha="center", color="white", fontsize=8)
ax.set_title("Every extra AC adds roughly 40 kWh a month")
ax.set_xlabel("Number of air conditioners")
ax.set_ylabel("Average monthly units (kWh)")
plt.tight_layout()
plt.savefig(BASE + "/images/03_acs_vs_units.png", dpi=150, bbox_inches="tight")
plt.close()

fig, ax = plt.subplots(figsize=(6.8, 5))
cm = df[num_cols + ["Monthly_Units_kWh"]].corr()
sns.heatmap(cm, annot=True, fmt=".2f", cmap=sns.diverging_palette(250, 20, as_cmap=True, center="light"),
            vmin=-1, vmax=1, linewidths=1, linecolor="white", cbar_kws={"shrink": 0.8}, ax=ax)
ax.set_title("Correlation between numeric columns")
ax.grid(False)
plt.xticks(rotation=40, ha="right")
plt.tight_layout()
plt.savefig(BASE + "/images/04_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()

for col in ["City", "Housing_Type", "Tariff_Plan"]:
    t = df.groupby(col)["Monthly_Units_kWh"].agg(["count", "mean", "median"]).round(1).sort_values("mean", ascending=False)
    print(t, "\n")

fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), sharey=True)
for ax, col in zip(axes, ["City", "Housing_Type", "Tariff_Plan"]):
    m = df.groupby(col)["Monthly_Units_kWh"].mean().sort_values(ascending=False)
    bars = ax.bar(m.index, m.values, color=BLUE, width=0.6)
    for b, v in zip(bars, m.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 4, f"{v:.0f}", ha="center", color=INK, fontsize=9)
    ax.set_title(col.replace("_", " "))
    ax.tick_params(axis="x", rotation=25)
    ax.set_xlabel("")
axes[0].set_ylabel("Average monthly units (kWh)")
fig.suptitle("Average monthly units by group", x=0.01, ha="left", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(BASE + "/images/05_units_by_category.png", dpi=150, bbox_inches="tight")
plt.close()

hc = df[df["High_Consumer"] == "Yes"]
print("High Consumers:", len(hc), "out of", len(df), f"({len(hc)/len(df)*100:.1f}%)")
print()
print(df["Consumption_Level"].value_counts().reindex(["Low", "Medium", "High"]))
print()
print("Average of High Consumers vs the rest:")
print(df.groupby("High_Consumer")[["Home_Area_Sqft", "Num_Air_Conditioners", "Household_Size", "Monthly_Units_kWh"]].mean().round(1))

print("Share of High Consumers (%) by group")
for col in ["City", "Housing_Type", "Tariff_Plan"]:
    print((df.groupby(col)["High_Consumer"].apply(lambda s: (s == "Yes").mean() * 100)).round(1).sort_values(ascending=False).to_dict())

print()
print("Top 10 households by monthly units:")
print(df.sort_values("Monthly_Units_kWh", ascending=False).head(10)[
    ["Household_ID", "City", "Housing_Type", "Tariff_Plan", "Home_Area_Sqft",
     "Num_Air_Conditioners", "Monthly_Units_kWh", "Estimated_Bill_Rs"]])

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)

by_city = df.groupby("City")["High_Consumer"].apply(lambda s: (s == "Yes").mean() * 100).sort_values(ascending=False)
bars = axes[0].bar(by_city.index, by_city.values, color=BLUE, width=0.6)
for b, v in zip(bars, by_city.values):
    axes[0].text(b.get_x() + b.get_width() / 2, v + 0.6, f"{v:.0f}%", ha="center", color=INK, fontsize=9)
axes[0].set_title("By city")
axes[0].set_ylabel("Households above 300 kWh (%)")

by_ac = df.groupby("Num_Air_Conditioners")["High_Consumer"].apply(lambda s: (s == "Yes").mean() * 100)
bars = axes[1].bar(by_ac.index.astype(str), by_ac.values, color=BLUE, width=0.6)
for b, v in zip(bars, by_ac.values):
    axes[1].text(b.get_x() + b.get_width() / 2, v + 0.6, f"{v:.0f}%", ha="center", color=INK, fontsize=9)
axes[1].set_title("By number of ACs")
axes[1].set_xlabel("Number of air conditioners")

fig.suptitle("Who becomes a High Consumer?", x=0.01, ha="left", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(BASE + "/images/06_high_consumers.png", dpi=150, bbox_inches="tight")
plt.close()

out = df.copy()
out["Billing_Date"] = out["Billing_Date"].dt.strftime("%Y-%m-%d")
out.to_csv(BASE + "/data/processed/electricity_data_clean.csv", index=False)
print("Saved:", out.shape)
