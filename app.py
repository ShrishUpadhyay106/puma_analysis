"""
app.py  –  Puma Sales Analytics Dashboard
==========================================
Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_cleaner import get_clean_data, summary_by, monthly_trend

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Puma Sales Dashboard",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# CUSTOM CSS  – minimal, clean
# ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Global ── */
    html, body, [class*="css"] { font-family: -apple-system, "Segoe UI", system-ui, sans-serif; }

    /* ── KPI Card ── */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 0;
        overflow: hidden;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .kpi-accent {
        height: 5px;
        width: 100%;
    }
    .kpi-body {
        padding: 18px 20px 16px;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: #57606a;
        margin: 0 0 8px 0;
    }
    .kpi-icon {
        font-size: 1.3rem;
        margin-right: 6px;
        vertical-align: middle;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1f2328;
        margin: 0;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 0.75rem;
        color: #57606a;
        margin: 4px 0 0;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #1f2328;
        color: #ffffff;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #d0d7de !important;
    }

    /* ── Title bar ── */
    .puma-header {
        background: linear-gradient(90deg, #1f2328 60%, #3b82d4 100%);
        padding: 18px 28px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .puma-header h1 { color: #ffffff; margin: 0; font-size: 2rem; }
    .puma-header p  { color: #d0d7de; margin: 4px 0 0; font-size: 0.95rem; }

    /* ── Hide default metric widget ── */
    [data-testid="stMetric"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────
# LOAD & CACHE DATA
# ─────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cleaning data …")
def load_data():
    return get_clean_data()

df_full = load_data()

# ─────────────────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👟 Puma Analytics")
    st.markdown("---")

    st.markdown("### 📅 Date Range")
    min_date = df_full["Invoice Date"].min().date()
    max_date = df_full["Invoice Date"].max().date()
    date_range = st.date_input(
        "Select range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.markdown("### 🏪 Retailer")
    all_retailers = sorted(df_full["Retailer"].dropna().unique())
    sel_retailers = st.multiselect(
        "Select retailer(s)",
        options=all_retailers,
        default=all_retailers,
    )

    st.markdown("### 🌎 Region")
    all_regions = sorted(df_full["Region"].dropna().unique())
    sel_regions = st.multiselect(
        "Select region(s)",
        options=all_regions,
        default=all_regions,
    )

    st.markdown("### 👟 Product")
    all_products = sorted(df_full["Product"].dropna().unique())
    sel_products = st.multiselect(
        "Select product(s)",
        options=all_products,
        default=all_products,
    )

    st.markdown("### 🛒 Sales Method")
    all_methods = sorted(df_full["Sales Method"].dropna().unique())
    sel_methods = st.multiselect(
        "Select method(s)",
        options=all_methods,
        default=all_methods,
    )

    st.markdown("---")
    st.caption("Puma Sales Analytics · IBM Project")

# ─────────────────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────────────────
# Handle partial date_input (user still picking)
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_dt = pd.Timestamp(date_range[0])
    end_dt   = pd.Timestamp(date_range[1])
else:
    start_dt = pd.Timestamp(min_date)
    end_dt   = pd.Timestamp(max_date)

df = df_full[
    (df_full["Invoice Date"] >= start_dt)
    & (df_full["Invoice Date"] <= end_dt)
    & (df_full["Retailer"].isin(sel_retailers))
    & (df_full["Region"].isin(sel_regions))
    & (df_full["Product"].isin(sel_products))
    & (df_full["Sales Method"].isin(sel_methods))
].copy()

# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="puma-header">
      <h1>👟 Puma Sales Analytics Dashboard</h1>
      <p>Filtered dataset: <strong>{len(df):,}</strong> transactions 
         from <strong>{start_dt.date()}</strong> to <strong>{end_dt.date()}</strong></p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────
tab_overview, tab_retailer, tab_product, tab_region, tab_time, tab_data = st.tabs(
    ["📊 Overview", "🏪 By Retailer", "👟 By Product", "🌎 By Region", "📅 Trend", "🗃️ Raw Data"]
)

# ════════════════════════════════════════════════════════
# TAB 1 – OVERVIEW KPIs
# ════════════════════════════════════════════════════════
with tab_overview:

    total_sales   = df["Total Sales"].sum()
    total_units   = df["Units Sold"].sum()
    total_profit  = df["Operating Profit"].sum()
    avg_margin    = df["Operating Margin"].mean()
    num_retailers = df["Retailer"].nunique()
    num_products  = df["Product"].nunique()

    def kpi_card(icon, label, value, sub, accent):
        return f"""
        <div class="kpi-card">
          <div class="kpi-accent" style="background:{accent};"></div>
          <div class="kpi-body">
            <p class="kpi-label"><span class="kpi-icon">{icon}</span>{label}</p>
            <p class="kpi-value">{value}</p>
            <p class="kpi-sub">{sub}</p>
          </div>
        </div>"""

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(kpi_card("💰", "Total Sales",
            f"${total_sales/1e6:.2f}M", "Gross revenue (filtered)",
            "#3b82d4"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("📦", "Units Sold",
            f"{total_units/1e3:.1f}K", "Total quantity sold",
            "#7c5cd8"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("📈", "Operating Profit",
            f"${total_profit/1e6:.2f}M", "After operating costs",
            "#16a34a"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("🎯", "Avg Margin",
            f"{avg_margin:.1f}%", "Operating margin avg",
            "#ea580c"), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card("🏪", "Retailers",
            str(num_retailers), "Active retail partners",
            "#db2777"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card("👟", "Products",
            str(num_products), "Distinct product lines",
            "#0891b2"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    col_l, col_r = st.columns(2)

    # Sales by Sales Method – Pie
    with col_l:
        st.markdown("#### Sales by Method")
        method_df = df.groupby("Sales Method")["Total Sales"].sum().reset_index()
        fig = px.pie(
            method_df,
            names="Sales Method",
            values="Total Sales",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # Sales by Year – Bar
    with col_r:
        st.markdown("#### Annual Sales Comparison")
        year_df = df.groupby("Year")["Total Sales"].sum().reset_index()
        fig = px.bar(
            year_df, x="Year", y="Total Sales",
            color="Year",
            color_discrete_sequence=["#3b82d4", "#7c5cd8"],
            text_auto=".2s",
        )
        fig.update_layout(showlegend=False, xaxis_title="Year",
                          yaxis_title="Total Sales ($)", margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)

    # Calculated vs Reported Sales validation
    st.markdown("#### ✅ Data Quality Check: Calculated vs Reported Sales")
    df["Diff"] = (df["Calculated Sales"] - df["Total Sales"]).abs()
    exact_match = (df["Diff"] < 1).sum()
    pct = exact_match / len(df) * 100
    st.info(
        f"**{exact_match:,} / {len(df):,}** rows ({pct:.1f}%) have Calculated Sales "
        f"(Qty × Price) matching Reported Total Sales within $1. "
        f"Remaining differences are due to bulk discounts or rounding in source data."
    )

# ════════════════════════════════════════════════════════
# TAB 2 – BY RETAILER
# ════════════════════════════════════════════════════════
with tab_retailer:
    st.subheader("Sales Performance by Retailer")

    ret_df = summary_by(df, "Retailer")

    # Bar chart – total sales
    fig = px.bar(
        ret_df, x="Retailer", y="Total_Sales",
        color="Retailer",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"Total_Sales": "Total Sales ($)"},
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Total Sales ($)")
    st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns(2)

    # Avg Margin per retailer
    with col_l:
        st.markdown("#### Average Operating Margin (%)")
        fig2 = px.bar(
            ret_df.sort_values("Avg_Margin", ascending=True),
            x="Avg_Margin", y="Retailer",
            orientation="h",
            color="Avg_Margin",
            color_continuous_scale="Blues",
            text_auto=".1f",
            labels={"Avg_Margin": "Avg Margin (%)"},
        )
        fig2.update_layout(coloraxis_showscale=False, margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)

    # Units sold per retailer
    with col_r:
        st.markdown("#### Total Units Sold")
        fig3 = px.bar(
            ret_df.sort_values("Total_Units", ascending=True),
            x="Total_Units", y="Retailer",
            orientation="h",
            color="Total_Units",
            color_continuous_scale="Purples",
            text_auto=".2s",
            labels={"Total_Units": "Units Sold"},
        )
        fig3.update_layout(coloraxis_showscale=False, margin=dict(t=10))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### Summary Table")
    ret_df_display = ret_df.copy()
    ret_df_display["Total_Sales"]   = ret_df_display["Total_Sales"].map("${:,.0f}".format)
    ret_df_display["Total_Profit"]  = ret_df_display["Total_Profit"].map("${:,.0f}".format)
    ret_df_display["Avg_Margin"]    = ret_df_display["Avg_Margin"].map("{:.1f}%".format)
    ret_df_display["Total_Units"]   = ret_df_display["Total_Units"].map("{:,.0f}".format)
    st.dataframe(ret_df_display, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════
# TAB 3 – BY PRODUCT
# ════════════════════════════════════════════════════════
with tab_product:
    st.subheader("Sales Performance by Product")

    prod_df = summary_by(df, "Product")

    fig = px.bar(
        prod_df, x="Total_Sales", y="Product",
        orientation="h",
        color="Product",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Set3,
        labels={"Total_Sales": "Total Sales ($)"},
    )
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="Total Sales ($)",
                      margin=dict(t=10))
    st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Profit vs Sales – Scatter")
        fig_sc = px.scatter(
            prod_df, x="Total_Sales", y="Total_Profit",
            size="Total_Units", color="Product",
            hover_name="Product",
            labels={"Total_Sales": "Total Sales ($)", "Total_Profit": "Total Profit ($)"},
        )
        fig_sc.update_layout(showlegend=False, margin=dict(t=10))
        st.plotly_chart(fig_sc, use_container_width=True)

    with col_r:
        st.markdown("#### Units Sold per Product")
        fig_u = px.pie(
            prod_df, names="Product", values="Total_Units",
            hole=0.35,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
        fig_u.update_traces(textinfo="percent+label")
        fig_u.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig_u, use_container_width=True)

    st.markdown("#### Summary Table")
    prod_display = prod_df.copy()
    prod_display["Total_Sales"]  = prod_display["Total_Sales"].map("${:,.0f}".format)
    prod_display["Total_Profit"] = prod_display["Total_Profit"].map("${:,.0f}".format)
    prod_display["Avg_Margin"]   = prod_display["Avg_Margin"].map("{:.1f}%".format)
    prod_display["Total_Units"]  = prod_display["Total_Units"].map("{:,.0f}".format)
    st.dataframe(prod_display, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════
# TAB 4 – BY REGION
# ════════════════════════════════════════════════════════
with tab_region:
    st.subheader("Sales Performance by Region")

    reg_df  = summary_by(df, "Region")
    state_df = summary_by(df, "State")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### Total Sales by Region")
        fig = px.pie(
            reg_df, names="Region", values="Total_Sales",
            color_discrete_sequence=px.colors.qualitative.Bold,
            hole=0.3,
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("#### Avg Margin by Region")
        fig2 = px.bar(
            reg_df.sort_values("Avg_Margin"),
            x="Avg_Margin", y="Region", orientation="h",
            color="Avg_Margin", color_continuous_scale="Teal",
            text_auto=".1f",
            labels={"Avg_Margin": "Avg Margin (%)"},
        )
        fig2.update_layout(coloraxis_showscale=False, margin=dict(t=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Top 15 States by Sales")
    top_states = state_df.head(15)
    fig3 = px.bar(
        top_states, x="State", y="Total_Sales",
        color="Total_Sales", color_continuous_scale="Blues",
        text_auto=".2s",
        labels={"Total_Sales": "Total Sales ($)"},
    )
    fig3.update_layout(coloraxis_showscale=False, xaxis_title="",
                       yaxis_title="Total Sales ($)")
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 5 – TREND OVER TIME
# ════════════════════════════════════════════════════════
with tab_time:
    st.subheader("Monthly & Yearly Sales Trend")

    trend = monthly_trend(df)

    # Line chart – monthly sales
    fig = px.line(
        trend, x="Period", y="Total_Sales",
        color="Year", markers=True,
        labels={"Total_Sales": "Total Sales ($)", "Period": "Month"},
        color_discrete_sequence=["#3b82d4", "#7c5cd8"],
    )
    fig.update_layout(xaxis_tickangle=-45, yaxis_title="Total Sales ($)")
    st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns(2)

    # Product × Month heatmap
    with col_l:
        st.markdown("#### Product Sales by Month (Heatmap)")
        heat = (
            df.groupby(["Month Name", "Product"])["Total Sales"]
            .sum()
            .reset_index()
            .pivot(index="Product", columns="Month Name", values="Total Sales")
            .fillna(0)
        )
        month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                       "Jul","Aug","Sep","Oct","Nov","Dec"]
        heat = heat[[c for c in month_order if c in heat.columns]]
        fig_h = go.Figure(
            go.Heatmap(
                z=heat.values,
                x=heat.columns.tolist(),
                y=heat.index.tolist(),
                colorscale="Blues",
                text=[[f"${v:,.0f}" for v in row] for row in heat.values],
                texttemplate="%{text}",
                showscale=True,
            )
        )
        fig_h.update_layout(margin=dict(t=10, b=40))
        st.plotly_chart(fig_h, use_container_width=True)

    # Monthly units sold
    with col_r:
        st.markdown("#### Monthly Units Sold")
        fig_u = px.bar(
            trend, x="Period", y="Total_Units",
            color="Year",
            labels={"Total_Units": "Units Sold"},
            color_discrete_sequence=["#3b82d4", "#7c5cd8"],
        )
        fig_u.update_layout(xaxis_tickangle=-45, yaxis_title="Units Sold",
                             barmode="group")
        st.plotly_chart(fig_u, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 6 – RAW / CLEANED DATA
# ════════════════════════════════════════════════════════
with tab_data:
    st.subheader("Cleaned Dataset Explorer")

    search = st.text_input("🔍 Search (Retailer, Product, City …)", "")
    show_df = df.copy()
    if search:
        mask = show_df.apply(
            lambda col: col.astype(str).str.contains(search, case=False, na=False)
        ).any(axis=1)
        show_df = show_df[mask]

    st.write(f"Showing **{len(show_df):,}** rows")
    st.dataframe(show_df, use_container_width=True, height=460)

    csv_bytes = show_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered CSV",
        data=csv_bytes,
        file_name="puma_cleaned.csv",
        mime="text/csv",
    )
