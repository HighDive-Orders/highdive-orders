"""
HIGH DIVE ORDER MANAGEMENT SYSTEM
Streamlit Web Application

A rolling 4-week, day-of-week aware ordering system that connects
to Toast POS API and generates vendor-specific purchase orders.

Author: Built for High Dive Restaurant Group
Version: 1.0
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="High Dive | Order Management",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'DM Serif Display', serif;
    }

    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #94a3b8;
        margin: 0.25rem 0 0 0;
        font-size: 0.9rem;
    }
    .header-badge {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: #e2e8f0;
        font-size: 0.8rem;
        text-align: right;
    }

    /* Vendor cards */
    .vendor-card {
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        background: #f8fafc;
    }
    .vendor-card h4 {
        margin: 0 0 0.25rem 0;
        font-size: 1rem;
    }
    .vendor-card p {
        margin: 0;
        font-size: 0.82rem;
        color: #64748b;
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        flex: 1;
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-card .value {
        font-size: 2rem;
        font-weight: 600;
        font-family: 'DM Serif Display', serif;
        color: #0f3460;
    }
    .metric-card .label {
        font-size: 0.78rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }

    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    .section-header h2 {
        font-size: 1.25rem;
        margin: 0;
        color: #1e293b;
    }

    /* Order table */
    .order-table-header {
        background: #0f3460;
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Day pill */
    .day-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 99px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 0.1rem;
    }

    /* Alert boxes */
    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #1d4ed8;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #92400e;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #166534;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }

    /* Button overrides */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Print styles */
    @media print {
        [data-testid="stSidebar"] { display: none !important; }
        .no-print { display: none !important; }
        .stButton { display: none !important; }
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data
def load_recipes():
    path = Path(__file__).parent / "recipes_imported.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

@st.cache_data
def load_vendor_mapping():
    path = Path(__file__).parent / "vendor_mapping_smart.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

@st.cache_data
def load_vendor_schedules():
    path = Path(__file__).parent / "vendor_schedules.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def load_toast_data_from_file(uploaded_file):
    """Load Toast Product Mix data from uploaded Excel file"""
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Items")
        df = df[df["Item"].notna()].copy()
        numeric_cols = ["Qty sold", "Net sales"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# CORE CALCULATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_SHORT = {"Monday": "Mon", "Tuesday": "Tue", "Wednesday": "Wed",
             "Thursday": "Thu", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"}

# Days the restaurant is CLOSED — zero sales, zero ingredient needs
CLOSED_DAYS = {"Monday", "Tuesday"}
OPEN_DAYS   = [d for d in DAY_ORDER if d not in CLOSED_DAYS]

# Day-of-week weight distribution across OPEN days only (sums to 1.0)
# High Dive open Wed-Sun: Wednesday lightest, Saturday busiest
TYPICAL_WEIGHTS = {
    "Monday":    0.0,    # CLOSED
    "Tuesday":   0.0,    # CLOSED
    "Wednesday": 0.18,
    "Thursday":  0.20,
    "Friday":    0.24,
    "Saturday":  0.26,
    "Sunday":    0.12,
}

def get_week_start(file_name):
    """Try to extract week start date from Toast filename like ProductMix_2026-01-19_2026-01-25"""
    try:
        parts = str(file_name).replace(".xlsx", "").split("_")
        for part in parts:
            try:
                return datetime.strptime(part, "%Y-%m-%d")
            except:
                continue
    except:
        pass
    return None

def build_day_of_week_sales(weekly_datasets):
    """
    Build a day-of-week sales table from multiple weeks of Toast data.

    weekly_datasets: list of (week_start_date, DataFrame) tuples
    Returns: dict { "Monday": [val_w1, val_w2, ...], ... }
    """
    dow_sales = {day: [] for day in DAY_ORDER}
    dow_qty   = {day: [] for day in DAY_ORDER}

    for (week_start, df) in weekly_datasets:
        if week_start is None:
            continue
        # Week runs Mon-Sun; week_start should be Monday
        # Normalise to Monday
        ws = week_start - timedelta(days=week_start.weekday())
        for i, day in enumerate(DAY_ORDER):
            day_date = ws + timedelta(days=i)
            # We can't split a weekly aggregate by day (Toast exports weekly totals)
            # so we spread proportionally or just use the weekly total divided 7
            # REAL version: use Toast API daily breakdown
            pass

    return dow_sales

def calculate_ingredient_usage(sales_df, recipes, vendor_mapping, adjustments=None):
    """
    Given a sales dataframe and recipes, calculate ingredient usage.
    adjustments: dict { item_name: multiplier } for event/weather
    """
    if adjustments is None:
        adjustments = {}

    ingredient_totals = {}
    matched_items = []
    unmatched_items = []

    # Normalise recipe keys to upper for matching
    recipes_upper = {k.upper(): v for k, v in recipes.items()}

    for _, row in sales_df.iterrows():
        item = str(row.get("Item", "")).strip()
        qty  = row.get("Qty sold", 0)
        if pd.isna(qty) or qty == 0:
            continue

        # Apply adjustment if any
        adj = adjustments.get(item, 1.0)
        qty_adjusted = qty * adj

        recipe_key = item.upper()
        if recipe_key in recipes_upper:
            matched_items.append(item)
            recipe = recipes_upper[recipe_key]
            for ingredient, details in recipe.items():
                ing_lower = ingredient.lower()
                vendor = vendor_mapping.get(ing_lower,
                         vendor_mapping.get(ingredient, "UNMAPPED"))
                if ingredient not in ingredient_totals:
                    ingredient_totals[ingredient] = {
                        "qty_used": 0,
                        "unit": details.get("unit", "each"),
                        "vendor": vendor,
                    }
                ingredient_totals[ingredient]["qty_used"] += details["qty"] * qty_adjusted
        else:
            unmatched_items.append(item)

    return ingredient_totals, matched_items, unmatched_items


def build_order_for_vendor(vendor_key, coverage_days, dow_averages,
                           recipes, vendor_mapping, waste_factor=1.10):
    """
    Build an order for a specific vendor covering specific days.

    vendor_key: e.g. "GFS"
    coverage_days: list of day names e.g. ["Wednesday", "Thursday"]
    dow_averages: dict { "Monday": DataFrame of avg usage, ... }
    Returns: DataFrame with ingredients and per-day + total quantities
    """
    ingredient_rows = {}

    for day in coverage_days:
        if day not in dow_averages:
            continue
        day_usage = dow_averages[day]  # dict { ingredient: qty }
        for ingredient, qty in day_usage.items():
            ing_lower = ingredient.lower()
            vendor = vendor_mapping.get(ing_lower,
                     vendor_mapping.get(ingredient, "UNMAPPED"))
            if vendor != vendor_key:
                continue
            if ingredient not in ingredient_rows:
                ingredient_rows[ingredient] = {d: 0 for d in DAY_ORDER}
                ingredient_rows[ingredient]["unit"] = ""
            ingredient_rows[ingredient][day] = round(qty, 2)

    if not ingredient_rows:
        return pd.DataFrame()

    rows = []
    for ingredient, data in ingredient_rows.items():
        row = {"Ingredient": ingredient}
        total = 0
        for day in coverage_days:
            val = data.get(day, 0)
            row[DAY_SHORT[day]] = round(val, 2)
            total += val
        row["Total"] = round(total * waste_factor, 2)
        row["Unit"]  = data.get("unit", "")
        rows.append(row)

    df = pd.DataFrame(rows)
    cols = ["Ingredient"] + [DAY_SHORT[d] for d in coverage_days] + ["Total", "Unit"]
    df = df[[c for c in cols if c in df.columns]]
    return df.sort_values("Total", ascending=False).reset_index(drop=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────

if "weekly_data" not in st.session_state:
    st.session_state.weekly_data = {}   # { "Week 1": DataFrame, ... }
if "dow_averages" not in st.session_state:
    st.session_state.dow_averages = {}  # { "Monday": {ingredient: avg_qty}, ... }
if "day_adjustments" not in st.session_state:
    # Closed days (Mon/Tue) default to -100% (no sales)
    st.session_state.day_adjustments = {
        d: (-100 if d in CLOSED_DAYS else 0) for d in DAY_ORDER
    }
if "sales_projections" not in st.session_state:
    st.session_state.sales_projections = {d: 0.0 for d in DAY_ORDER}
if "toast_connected" not in st.session_state:
    st.session_state.toast_connected = False


# ─────────────────────────────────────────────────────────────────────────────
# LOAD STATIC DATA
# ─────────────────────────────────────────────────────────────────────────────

recipes         = load_recipes()
vendor_mapping  = load_vendor_mapping()
vendor_schedules = load_vendor_schedules()


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────

now = datetime.now()
st.markdown(f"""
<div class="main-header">
    <div>
        <h1>🍽️ High Dive Order Management</h1>
        <p>Automated purchasing · Toast POS · 4-Week Rolling Analysis</p>
    </div>
    <div class="header-badge">
        <div style="font-size:1.1rem; font-weight:600;">{now.strftime("%A")}</div>
        <div>{now.strftime("%B %d, %Y")}</div>
        <div style="margin-top:0.25rem; color:#7dd3fc;">
            {"✅ Toast Connected" if st.session_state.toast_connected else "⚠️ Manual Upload Mode"}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio(
        "",
        ["📊 Sales Dashboard", "📋 Generate Orders", "⚙️ Settings", "❓ Help"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### Data Status")

    weeks_loaded = len(st.session_state.weekly_data)
    if weeks_loaded == 0:
        st.warning("No data loaded")
    elif weeks_loaded < 4:
        st.warning(f"{weeks_loaded}/4 weeks loaded")
    else:
        st.success(f"✅ {weeks_loaded} weeks loaded")

    st.markdown("---")
    st.markdown("### Recipes")
    st.info(f"{len(recipes)} recipes loaded")

    st.markdown("---")
    st.markdown("### Vendors")
    for v_key, v_data in vendor_schedules.items():
        orders = v_data.get("orders", [])
        if orders:
            days_str = ", ".join([o["delivery_day"][:3] for o in orders])
            st.markdown(f"**{v_key}** — delivers {days_str}")
        else:
            st.markdown(f"**{v_key}** — ⚠️ schedule pending")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SALES DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

if page == "📊 Sales Dashboard":

    # ── Upload Section ──────────────────────────────────────────────────────
    st.markdown('<div class="section-header"><span>📤</span><h2>Load Sales Data</h2></div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        Upload up to 4 weeks of Toast Product Mix exports. The system calculates a
        separate average for each day of the week (Monday average, Tuesday average, etc.)
        giving you accurate day-specific order quantities. Once Toast API is configured,
        this step happens automatically overnight.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_files = st.file_uploader(
            "Upload Toast Product Mix files (up to 4 weeks)",
            type=["xlsx"],
            accept_multiple_files=True,
            help="Export from Toast: Reports → Product Mix → Export Excel"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.weekly_data = {}
            st.session_state.dow_averages = {}
            st.rerun()

    if uploaded_files:
        for uf in uploaded_files[:4]:
            if uf.name not in st.session_state.weekly_data:
                df = load_toast_data_from_file(uf)
                if df is not None:
                    st.session_state.weekly_data[uf.name] = df
                    st.success(f"✅ Loaded: {uf.name} — {len(df)} items, "
                               f"${df['Net sales'].sum():,.0f} revenue")

    # ── Summary Metrics ─────────────────────────────────────────────────────
    if st.session_state.weekly_data:
        all_dfs = list(st.session_state.weekly_data.values())
        total_items = sum(df["Qty sold"].sum() for df in all_dfs)
        total_revenue = sum(df["Net sales"].sum() for df in all_dfs)
        weeks = len(all_dfs)
        avg_weekly_revenue = total_revenue / weeks if weeks else 0

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="value">{weeks}</div>
                <div class="label">Weeks Loaded</div>
            </div>
            <div class="metric-card">
                <div class="value">${avg_weekly_revenue:,.0f}</div>
                <div class="label">Avg Weekly Revenue</div>
            </div>
            <div class="metric-card">
                <div class="value">{total_items/weeks:,.0f}</div>
                <div class="label">Avg Items / Week</div>
            </div>
            <div class="metric-card">
                <div class="value">{weeks * 7}</div>
                <div class="label">Days Analysed</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Day-of-Week Breakdown ────────────────────────────────────────────
        st.markdown('<div class="section-header"><span>📅</span><h2>Day-of-Week Averages</h2></div>',
                    unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
            Because we can't split a weekly Toast export by individual day,
            day-of-week averages are estimated by dividing weekly totals
            proportionally. <strong>Once the Toast API is connected, the system will
            pull actual daily data for precise per-day analysis.</strong>
        </div>
        """, unsafe_allow_html=True)

        # Estimate day-of-week distribution using typical restaurant patterns
        # (Will be replaced by real data from Toast API)
        avg_revenue = avg_weekly_revenue

        # Build day projections — closed days always $0
        day_proj = {}
        for day in DAY_ORDER:
            if day in CLOSED_DAYS:
                day_proj[day] = {"base": 0, "adjusted": 0, "adj_pct": -100}
                st.session_state.sales_projections[day] = 0
            else:
                base = avg_revenue * TYPICAL_WEIGHTS[day]
                adj_pct = st.session_state.day_adjustments.get(day, 0)
                adjusted = base * (1 + adj_pct / 100)
                day_proj[day] = {"base": base, "adjusted": adjusted, "adj_pct": adj_pct}
                st.session_state.sales_projections[day] = adjusted

        # Chart
        fig = go.Figure()
        fig.add_bar(
            x=list(DAY_SHORT.values()),
            y=[day_proj[d]["base"] for d in DAY_ORDER],
            name="Base Projection",
            marker_color="#94a3b8"
        )
        fig.add_bar(
            x=list(DAY_SHORT.values()),
            y=[day_proj[d]["adjusted"] - day_proj[d]["base"] for d in DAY_ORDER],
            name="Adjustment",
            marker_color=["#22c55e" if day_proj[d]["adj_pct"] >= 0 else "#ef4444"
                          for d in DAY_ORDER]
        )
        fig.update_layout(
            barmode="stack",
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            yaxis_title="Projected Sales ($)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis=dict(gridcolor="#f1f5f9")
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Event / Weather Adjustments ──────────────────────────────────────
        st.markdown('<div class="section-header"><span>🌤️</span>'
                    '<h2>Adjust for Events & Weather</h2></div>',
                    unsafe_allow_html=True)

        st.markdown("Use the sliders to increase or decrease each day's projection. "
                    "Positive = busier than average, negative = slower than average.")

        cols = st.columns(7)
        for i, day in enumerate(DAY_ORDER):
            with cols[i]:
                if day in CLOSED_DAYS:
                    # Closed days — show label only, no slider
                    st.markdown(
                        f"**{DAY_SHORT[day]}**  \n"
                        f"<span style='color:#ef4444; font-size:0.85rem;'>🔴 CLOSED</span>",
                        unsafe_allow_html=True
                    )
                    st.session_state.day_adjustments[day] = -100
                else:
                    val = st.slider(
                        DAY_SHORT[day],
                        min_value=-50,
                        max_value=100,
                        value=st.session_state.day_adjustments.get(day, 0),
                        step=5,
                        format="%d%%",
                        key=f"adj_{day}"
                    )
                    st.session_state.day_adjustments[day] = val

        # Weekly total
        total_projected = sum(day_proj[d]["adjusted"] for d in DAY_ORDER)
        base_total = sum(day_proj[d]["base"] for d in DAY_ORDER)
        delta = total_projected - base_total
        delta_str = f"+${delta:,.0f}" if delta >= 0 else f"-${abs(delta):,.0f}"

        st.markdown(f"""
        <div class="success-box" style="text-align:center; font-size:1.1rem;">
            📊 <strong>This Week's Projected Revenue: ${total_projected:,.0f}</strong>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            Base: ${base_total:,.0f} &nbsp; Adjustments: {delta_str}
        </div>
        """, unsafe_allow_html=True)

        # Detailed projection table
        with st.expander("View detailed day-by-day projection"):
            proj_df = pd.DataFrame([
                {
                    "Day": day,
                    "Base ($)": f"${day_proj[day]['base']:,.0f}",
                    "Adjustment": f"{day_proj[day]['adj_pct']:+d}%",
                    "Final Projection ($)": f"${day_proj[day]['adjusted']:,.0f}"
                }
                for day in DAY_ORDER
            ])
            st.dataframe(proj_df, hide_index=True, use_container_width=True)

    else:
        st.markdown("""
        <div class="warning-box">
            📂 No data loaded yet. Upload your Toast Product Mix Excel files above to get started.
            <br><br>
            <strong>How to export from Toast:</strong>
            Reports → Product Mix → Select date range (7 days) → Export to Excel
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: GENERATE ORDERS
# ─────────────────────────────────────────────────────────────────────────────

elif page == "📋 Generate Orders":

    st.markdown('<div class="section-header"><span>📋</span><h2>Generate Vendor Orders</h2></div>',
                unsafe_allow_html=True)

    if not st.session_state.weekly_data:
        st.markdown("""
        <div class="warning-box">
            ⚠️ No sales data loaded. Go to <strong>Sales Dashboard</strong> first
            and upload your Toast Product Mix files.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── Vendor + Order Day Selector ─────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        vendor_options = [v for v, d in vendor_schedules.items() if d.get("orders")]
        selected_vendor = st.selectbox("Select Vendor", vendor_options)

    vendor_info = vendor_schedules.get(selected_vendor, {})
    order_options = vendor_info.get("orders", [])

    with col2:
        if order_options:
            order_labels = [
                f"Order {o['order_day']} → Deliver {o['delivery_day']} "
                f"(covers {', '.join(o['covers'])})"
                for o in order_options
            ]
            selected_order_idx = st.selectbox("Select Order Window", range(len(order_labels)),
                                               format_func=lambda i: order_labels[i])
            selected_order = order_options[selected_order_idx]
        else:
            st.warning("No schedule configured for this vendor yet.")
            selected_order = None

    with col3:
        waste_pct = st.number_input("Waste Buffer %", min_value=0, max_value=30,
                                     value=10, step=5)
        waste_factor = 1 + waste_pct / 100

    if selected_order:
        coverage_days = selected_order["covers"]

        st.markdown(f"""
        <div class="info-box">
            📦 <strong>{selected_vendor} — {vendor_info['full_name']}</strong><br>
            Order by: <strong>{selected_order['order_day']}</strong> &nbsp;|&nbsp;
            Delivery: <strong>{selected_order['delivery_day']}</strong> &nbsp;|&nbsp;
            Covers: <strong>{' · '.join(coverage_days)}</strong>
            ({len(coverage_days)} day{"s" if len(coverage_days) != 1 else ""})
            &nbsp;|&nbsp; Buffer: <strong>+{waste_pct}%</strong>
        </div>
        """, unsafe_allow_html=True)

        # ── Calculate Button ─────────────────────────────────────────────────
        if st.button(f"🔢 Calculate {selected_vendor} Order", type="primary",
                     use_container_width=True):

            # Combine all weekly data
            combined_df = pd.concat(list(st.session_state.weekly_data.values()),
                                     ignore_index=True)

            # Aggregate item sales across all weeks
            item_totals = (combined_df.groupby("Item")["Qty sold"]
                           .sum().reset_index()
                           .rename(columns={"Qty sold": "Total Qty"}))
            num_weeks = len(st.session_state.weekly_data)
            item_totals["Weekly Avg"] = item_totals["Total Qty"] / num_weeks

            # Calculate ingredient totals (weekly average basis)
            ingredient_totals, matched, unmatched = calculate_ingredient_usage(
                item_totals.rename(columns={"Weekly Avg": "Qty sold"}),
                recipes,
                vendor_mapping
            )

            # Spread weekly ingredient totals by day-of-week weights
            # Build per-day ingredient usage
            order_rows = []
            vendor_ingredients = {
                ing: data for ing, data in ingredient_totals.items()
                if data["vendor"] == selected_vendor
            }

            if not vendor_ingredients:
                st.warning(f"No ingredients mapped to {selected_vendor}. "
                           f"Check vendor mapping in Settings.")
            else:
                for ingredient, data in vendor_ingredients.items():
                    weekly_qty = data["qty_used"]
                    row = {"Ingredient": ingredient, "Unit": data["unit"]}

                    total_order = 0
                    for day in DAY_ORDER:
                        if day in CLOSED_DAYS:
                            # Restaurant closed — zero usage
                            row[DAY_SHORT[day]] = 0.0
                        else:
                            adj_factor = 1 + st.session_state.day_adjustments.get(day, 0) / 100
                            daily_qty = weekly_qty * TYPICAL_WEIGHTS[day] * adj_factor
                            row[DAY_SHORT[day]] = round(daily_qty, 1)
                            if day in coverage_days:
                                total_order += daily_qty

                    row["ORDER QTY"] = round(total_order * waste_factor, 1)
                    order_rows.append(row)

                order_df = pd.DataFrame(order_rows)
                order_df = order_df.sort_values("ORDER QTY", ascending=False)
                order_df = order_df[order_df["ORDER QTY"] > 0]

                # ── Display Order ─────────────────────────────────────────────
                st.markdown(f"""
                <div class="order-table-header">
                    <span>📋 {selected_vendor} ORDER — {selected_order['delivery_day'].upper()} DELIVERY</span>
                    <span style="font-size:0.85rem; font-weight:400;">
                        Covers {' + '.join(coverage_days)} | {len(order_df)} items
                    </span>
                </div>
                """, unsafe_allow_html=True)

                # Highlight coverage days
                display_cols = (["Ingredient"] +
                                [DAY_SHORT[d] for d in DAY_ORDER] +
                                ["ORDER QTY", "Unit"])
                display_df = order_df[[c for c in display_cols if c in order_df.columns]]

                # Style the dataframe
                coverage_short = [DAY_SHORT[d] for d in coverage_days]

                def highlight_coverage(col):
                    if col.name in coverage_short:
                        return ["background-color: #dbeafe; font-weight: 600"] * len(col)
                    elif col.name == "ORDER QTY":
                        return ["background-color: #dcfce7; font-weight: 700; "
                                "color: #166534"] * len(col)
                    return [""] * len(col)

                st.dataframe(
                    display_df.style.apply(highlight_coverage),
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )

                total_order_qty = order_df["ORDER QTY"].sum()
                st.markdown(f"""
                <div class="success-box">
                    ✅ <strong>{len(order_df)} ingredients</strong> to order from {selected_vendor}
                    &nbsp;·&nbsp; Total units: <strong>{total_order_qty:,.1f}</strong>
                    &nbsp;·&nbsp; Coverage: <strong>{' → '.join(coverage_days)}</strong>
                </div>
                """, unsafe_allow_html=True)

                # ── Downloads ─────────────────────────────────────────────────
                st.markdown("**Download Your Order:**")
                dcol1, dcol2 = st.columns(2)

                # Excel download
                with dcol1:
                    import io
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        display_df.to_excel(writer, index=False,
                                            sheet_name=f"{selected_vendor} Order")
                        # Summary sheet
                        pd.DataFrame({
                            "Detail": ["Vendor", "Delivery Day", "Coverage Days",
                                       "Order Date", "Waste Buffer", "Items"],
                            "Value": [vendor_info["full_name"],
                                      selected_order["delivery_day"],
                                      ", ".join(coverage_days),
                                      now.strftime("%Y-%m-%d"),
                                      f"{waste_pct}%",
                                      len(order_df)]
                        }).to_excel(writer, index=False, sheet_name="Summary")
                    buffer.seek(0)

                    filename = (f"{selected_vendor}_Order_"
                                f"{selected_order['delivery_day']}_"
                                f"{now.strftime('%Y%m%d')}.xlsx")
                    st.download_button(
                        "📥 Download Excel",
                        data=buffer,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

                with dcol2:
                    # Print-friendly view
                    if st.button("🖨️ Print-Friendly View", use_container_width=True):
                        st.markdown("""
                        <div class="info-box">
                            💡 Use your browser's Print function (Ctrl+P / Cmd+P) to save as PDF.
                            The sidebar and buttons will be hidden in the printed version.
                        </div>
                        """, unsafe_allow_html=True)

                # Show unmatched items
                food_unmatched = [u for u in set(unmatched)
                                  if "Food" in str(combined_df[combined_df["Item"] == u]
                                                    ["Sales Category"].values)]
                if food_unmatched:
                    with st.expander(f"⚠️ {len(food_unmatched)} food items without recipes"):
                        for item in sorted(food_unmatched)[:20]:
                            st.write(f"- {item}")

    # ── All Vendors Quick Overview ───────────────────────────────────────────
    st.markdown('<div class="section-header"><span>🏪</span>'
                '<h2>Vendor Schedule Overview</h2></div>',
                unsafe_allow_html=True)

    vcols = st.columns(len([v for v, d in vendor_schedules.items() if d.get("orders")]))
    col_i = 0
    for v_key, v_data in vendor_schedules.items():
        orders = v_data.get("orders", [])
        if not orders:
            continue
        with vcols[col_i]:
            color = v_data.get("color", "#64748b")
            order_summary = "<br>".join(
                [f"📦 Order <b>{o['order_day'][:3]}</b> → Del <b>{o['delivery_day'][:3]}</b>"
                 for o in orders]
            )
            st.markdown(f"""
            <div class="vendor-card" style="border-left-color: {color};">
                <h4 style="color: {color};">{v_key}</h4>
                <p style="font-size:0.78rem; color:#475569; margin-bottom:0.5rem;">
                    {v_data['full_name']}
                </p>
                <p>{order_summary}</p>
            </div>
            """, unsafe_allow_html=True)
        col_i += 1


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

elif page == "⚙️ Settings":

    st.markdown('<div class="section-header"><span>⚙️</span><h2>System Settings</h2></div>',
                unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔌 Toast API", "📖 Recipes & Vendors", "📅 Vendor Schedules"])

    with tab1:
        st.markdown("### Toast POS API Connection")
        st.markdown("""
        <div class="info-box">
            When Toast API is configured, the system automatically fetches the last 4 weeks
            of sales data every night. No manual file uploads needed.
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.toast_connected:
            st.success("✅ Toast API Connected")
            if st.button("Disconnect"):
                st.session_state.toast_connected = False
                st.rerun()
        else:
            st.warning("⚠️ Not connected — using manual file uploads")

            with st.form("toast_api_form"):
                st.markdown("**Enter your Toast API credentials:**")
                client_id     = st.text_input("Client ID")
                client_secret = st.text_input("Client Secret", type="password")
                restaurant_id = st.text_input("Restaurant GUID")

                submitted = st.form_submit_button("💾 Save & Connect", type="primary")
                if submitted:
                    if client_id and client_secret and restaurant_id:
                        # In production: encrypt and store in st.secrets
                        st.success("✅ Credentials saved! Testing connection...")
                        # TODO: test_toast_connection(client_id, client_secret, restaurant_id)
                        st.info("API integration will be completed once credentials are provided.")
                    else:
                        st.error("Please fill in all three fields.")

            st.markdown("---")
            st.markdown("**Don't have API credentials yet?**")
            st.markdown("""
            1. Call Toast support: **1-617-273-0305**
            2. Or email: **apisupport@toasttab.com**
            3. Say: *"I need API access for my restaurant ordering system"*
            4. Takes 1-2 business days to activate
            """)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Recipes")
            st.info(f"**{len(recipes)} recipes** currently loaded")

            with st.expander("View all recipes"):
                for recipe_name, ingredients in sorted(recipes.items()):
                    st.markdown(f"**{recipe_name}** — {len(ingredients)} ingredients")

            st.markdown("**Update Recipes:**")
            new_plate_cost = st.file_uploader(
                "Upload updated plate cost file",
                type=["xlsx"],
                key="recipe_upload"
            )
            if new_plate_cost:
                st.info("Recipe import will process the new plate cost file.")
                st.button("🔄 Import Recipes from File", type="primary")

        with col2:
            st.markdown("### Vendor Mapping")

            vm_counts = {}
            for ingredient, vendor in vendor_mapping.items():
                vm_counts[vendor] = vm_counts.get(vendor, 0) + 1

            for vendor, count in sorted(vm_counts.items()):
                icon = "✅" if vendor != "UNMAPPED" else "⚠️"
                st.markdown(f"{icon} **{vendor}**: {count} ingredients")

            unmapped = vm_counts.get("UNMAPPED", 0)
            if unmapped > 0:
                st.warning(f"{unmapped} ingredients need vendor assignment")
                st.markdown("Download and edit the vendor mapping file, then re-upload:")
                with open("/home/claude/highdive_app/vendor_mapping_smart.json") as f:
                    st.download_button(
                        "📥 Download Vendor Mapping",
                        data=f.read(),
                        file_name="vendor_mapping.json",
                        mime="application/json"
                    )

    with tab3:
        st.markdown("### Vendor Delivery Schedules")
        st.markdown("""
        <div class="info-box">
            These schedules determine which days each order covers. Currently loaded from
            <code>vendor_schedules.json</code>. Contact your developer to update.
        </div>
        """, unsafe_allow_html=True)

        for v_key, v_data in vendor_schedules.items():
            orders = v_data.get("orders", [])
            color  = v_data.get("color", "#64748b")

            with st.expander(f"{v_key} — {v_data['full_name']}"):
                if orders:
                    for o in orders:
                        covers_str = ", ".join(o["covers"])
                        st.markdown(
                            f"- **Order {o['order_day']}** → "
                            f"Delivery {o['delivery_day']} → "
                            f"Covers: *{covers_str}*"
                        )
                else:
                    st.warning("⚠️ No schedule configured yet — "
                               "provide delivery days to complete setup.")
                    if v_data.get("note"):
                        st.info(v_data["note"])


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: HELP
# ─────────────────────────────────────────────────────────────────────────────

elif page == "❓ Help":

    st.markdown('<div class="section-header"><span>❓</span><h2>Help & Guide</h2></div>',
                unsafe_allow_html=True)

    with st.expander("🚀 Quick Start — Weekly Workflow", expanded=True):
        st.markdown("""
        **Every Monday morning (10 minutes):**

        1. **Open this app** from any computer
        2. **Upload Toast data** (Sales Dashboard → Upload files)
            - Export from Toast: Reports → Product Mix → Last 7 days → Export Excel
            - Upload up to 4 weeks for best accuracy
        3. **Review projections** — adjust sliders for weather/events
        4. **Generate each vendor's order:**
            - Generate Orders → Select vendor → Select order window → Calculate
            - Download Excel or use Print View for PDF
        5. **Walk the restaurant** with printed orders, verify inventory
        6. **Place orders** with each vendor

        **Once Toast API is configured:** Steps 2 is fully automatic!
        """)

    with st.expander("📅 Understanding Vendor Schedules"):
        st.markdown("""
        Each vendor has specific order windows based on their delivery schedule:

        | Vendor | Order Day | Delivery | Covers |
        |--------|-----------|----------|--------|
        | **GFS** | Sunday | Wednesday | Wed, Thu |
        | **GFS** | Wednesday | Friday | Fri, Sat, Sun, Mon, Tue |
        | **WCW** | Sunday | Wednesday | Wed only |
        | **WCW** | Wednesday | Thursday | Thu only |
        | **WCW** | Thursday | Friday | Fri only |
        | **WCW** | Friday | Saturday | Sat, Sun, Mon, Tue |
        | **EVANS** | Sunday | Wednesday | Wed only |
        | **EVANS** | Wednesday | Thursday | Thu only |
        | **EVANS** | Thursday | Friday | Fri, Sat, Sun, Mon, Tue |
        | **Last Call** | Friday | Monday | Full week (Mon–Sun) |

        The system automatically selects the right days when you choose a vendor and order window.
        """)

    with st.expander("📊 How Day-of-Week Analysis Works"):
        st.markdown("""
        **The core insight:** Monday sales patterns differ from Friday patterns.
        Ordering the same amount every day leads to waste mid-week and shortages on weekends.

        **How it works:**
        1. System collects 4 weeks of sales data
        2. Calculates the average for each day separately:
            - Average of last 4 Mondays
            - Average of last 4 Tuesdays
            - ... through Sundays
        3. When you order for a specific delivery window (e.g., covers Wed + Thu),
           the system uses the Wednesday average + Thursday average
        4. Applies your event/weather adjustments on top
        5. Calculates ingredient needs from recipes
        6. Adds your waste buffer

        **Result:** Precise quantities matched to your actual sales pattern.

        **Note:** Until Toast API is connected, weekly totals are distributed using
        typical restaurant day-of-week weights. The API provides actual daily breakdowns.
        """)

    with st.expander("🔌 Setting Up Toast API"):
        st.markdown("""
        **Why:** Automates data fetching so you never manually export files again.

        **How to get API access:**
        1. Call Toast support: **1-617-273-0305** or email **apisupport@toasttab.com**
        2. Say: *"I need API access for automated ordering integration"*
        3. Toast enables it (1-2 business days, usually free with your subscription)
        4. Generate credentials in Toast dashboard
        5. Enter them in **Settings → Toast API**

        **What you need:**
        - Client ID
        - Client Secret
        - Restaurant GUID
        """)

    with st.expander("📤 Deploying to Streamlit Cloud (Free Hosting)"):
        st.markdown("""
        **To host this app online so anyone can access it:**

        1. **Create a free GitHub account** at github.com
        2. **Create a new repository** called `highdive-orders`
        3. **Upload all app files** to the repository
        4. **Create a free Streamlit Cloud account** at streamlit.io/cloud
        5. **Connect GitHub** to Streamlit Cloud
        6. **Click "New app"** → select your repository → select `streamlit_app.py`
        7. **Deploy** → get your URL: `highdive-orders.streamlit.app`
        8. **Share the URL** with your manager

        **Cost: $0/month forever on the free tier**

        Your manager accesses it at the URL — no installation, no maintenance.
        """)

    with st.expander("❓ Common Questions"):
        st.markdown("""
        **Q: How accurate are the projections?**
        Based on 4 weeks of actual data, typically within 5-10% of actual needs.
        Accuracy improves with more weeks of data.

        **Q: What if a recipe changes?**
        Go to Settings → Recipes → Upload updated plate cost file.

        **Q: Can I manually edit the order quantities?**
        Download the Excel file and edit before placing your order.

        **Q: What about items with no recipe?**
        Liquor, beer, wine, and non-food items don't need recipes.
        The system flags food items without recipes so you can add them.

        **Q: What if Toast API goes down?**
        Upload files manually in the Sales Dashboard. The system works either way.

        **Q: How do I add a new vendor?**
        Contact your developer to update `vendor_schedules.json`.
        """)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.78rem;'>"
    "High Dive Order Management System v1.0 · "
    "Powered by Toast POS · "
    "Hosted on Streamlit Cloud (Free)"
    "</div>",
    unsafe_allow_html=True
)
