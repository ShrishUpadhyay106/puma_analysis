# 👟 Puma Sales Analytics Dashboard

An end-to-end data analysis project built on the **Puma Sales Dataset**.  
The project cleans raw data, performs statistical analysis, and presents
interactive visualisations through a **Streamlit** web dashboard.

---

## 📁 Project Structure

```
puma-analysis/
├── data/
│   └── Puma-Dashboard-START.csv   ← raw dataset (9 000+ rows)
├── app.py                          ← Streamlit dashboard (frontend)
├── data_cleaner.py                 ← data loading, cleaning & helpers
├── requirements.txt                ← Python dependencies
└── README.md                       ← this file
```

---

## 🔍 Analysis Steps

| Step | Description |
|------|-------------|
| 1 | **Collect & Load** – Skip the 4 title/blank header rows; load 9 000+ transactions |
| 2 | **Clean** – Strip currency symbols (`$`, `,`), parse dates (`DD-MM-YYYY`), handle missing values, remove duplicates |
| 3 | **Calculate Sales** – Derive `Calculated Sales = Units Sold × Price per Unit` and compare with reported `Total Sales` |
| 4 | **Summarise** – Group by Retailer, Product, Region, State, Month to compute totals, counts & averages |
| 5 | **Visualise** – Bar charts, pie charts, scatter plots, heatmaps, and trend lines |
| 6 | **Decide** – Dashboard filters let stakeholders explore results and drive business decisions |

---

## 🚀 Quick Start

### 1 – Clone / copy the project

```bash
cd puma-analysis
```

### 2 – Create a virtual environment (recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 – Install dependencies

```bash
pip install -r requirements.txt
```

### 4 – Run the dashboard

```bash
streamlit run app.py
```

Open the URL shown in the terminal (default: `http://localhost:8501`).

---

## 🧹 Data Cleaning Details (`data_cleaner.py`)

| Issue | Fix Applied |
|-------|-------------|
| 4 blank / title rows at top of CSV | `skiprows=4` in `pd.read_csv` |
| Currency strings (`$50.00`, `$6,00,000`) | Strip `$` and `,`, cast to `float` |
| Percentage strings (`50%`) | Strip `%`, cast to `float` (0–100 scale) |
| Units with thousand-commas (`1,200`) | Strip `,`, cast to `float` |
| Date format `DD-MM-YYYY` | `pd.to_datetime(format="%d-%m-%Y")` |
| Duplicate rows | `drop_duplicates()` |
| Completely empty rows | `dropna(how="all")` |

---

## 📊 Dashboard Pages

| Tab | Content |
|-----|---------|
| 📊 **Overview** | KPI cards (Sales, Units, Profit, Margin), Sales Method pie chart, Annual bar chart, data-quality validation |
| 🏪 **By Retailer** | Total sales bar, margin & units horizontal bars, summary table |
| 👟 **By Product** | Horizontal sales bar, profit-vs-sales scatter, units pie, summary table |
| 🌎 **By Region** | Regional pie, margin bar, top-15 states bar |
| 📅 **Trend** | Monthly line chart, product heatmap, monthly units bar |
| 🗃️ **Raw Data** | Searchable & filterable cleaned dataset with CSV download |

All tabs respond to the **sidebar filters** (Date Range, Retailer, Region, Product, Sales Method).

---

## 🛠 Tech Stack

| Library | Purpose |
|---------|---------|
| `pandas` | Data loading, cleaning, aggregation |
| `numpy`  | Numeric operations |
| `plotly` | Interactive charts |
| `streamlit` | Web dashboard / UI |

---

## 📌 Key Business Insights (from full dataset)

- **Men's Street Footwear** is the highest-grossing product category.
- **West Gear** and **Foot Locker** lead in total sales across retailers.
- **In-store** sales dominate, but **Online** shows strong growth in 2021.
- **West** region contributes the largest share of revenue.
- Average operating margin is ≈ **42%** across all channels.

---

## 📄 License

For educational and demonstration purposes only.  
Dataset: Puma Sales (publicly available sample data).
