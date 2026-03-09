import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import io

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Payroll Projection Engine",
    page_icon="P",
    layout="wide"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'DM Serif Display', serif;
    }
    .main { background-color: #F8F7F4; }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid #1B4332;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 12px;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #111827;
        -webkit-text-fill-color: #111827;
        font-family: 'DM Serif Display', serif;
    }
    .metric-value-red {
        font-size: 28px;
        font-weight: 600;
        color: #DC2626 !important;
        -webkit-text-fill-color: #DC2626 !important;
        font-family: 'DM Serif Display', serif;
    }
    .metric-value-green {
        font-size: 28px;
        font-weight: 600;
        color: #065F46 !important;
        -webkit-text-fill-color: #065F46 !important;
        font-family: 'DM Serif Display', serif;
    }
    .metric-sub {
        font-size: 13px;
        color: #6B7280;
        margin-top: 2px;
    }

    .section-header {
        font-family: 'DM Serif Display', serif;
        font-size: 22px;
        color: #111827;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #E5E7EB;
    }

    .badge-active {
        background: #D1FAE5; color: #065F46;
        padding: 2px 10px; border-radius: 999px;
        font-size: 12px; font-weight: 600;
    }
    .badge-inactive {
        background: #FEE2E2; color: #991B1B;
        padding: 2px 10px; border-radius: 999px;
        font-size: 12px; font-weight: 600;
    }
    .badge-new {
        background: #DBEAFE; color: #1E40AF;
        padding: 2px 10px; border-radius: 999px;
        font-size: 12px; font-weight: 600;
    }
    .badge-terminated {
        background: #F3F4F6; color: #374151;
        padding: 2px 10px; border-radius: 999px;
        font-size: 12px; font-weight: 600;
    }

    .stButton > button {
        background-color: #1B4332 !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: #145a32 !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background-color: #1B4332 !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        background-color: #145a32 !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* ── Number input +/- stepper buttons ── */
    .stNumberInput button,
    .stNumberInput button p,
    .stNumberInput button span {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    .stFileUploader {
        background-color: white !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }
    .stFileUploader label, .stFileUploader p, .stFileUploader span,
    .stFileUploader div, [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] small {
        color: #374151 !important;
    }
    [data-testid="stFileUploadDropzone"] {
        background-color: #F9FAFB !important;
        border: 2px dashed #D1D5DB !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploadDropzone"] * {
        color: #374151 !important;
    }
    [data-testid="stFileUploadDropzone"] button {
        background-color: #1B4332 !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
    }
    [data-testid="stFileUploadDropzone"] button * {
        color: white !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background-color: #1B4332 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button:hover {
        background-color: #145a32 !important;
        color: white !important;
    }
    .stDownloadButton > button p, .stDownloadButton > button span {
        color: white !important;
    }

    .info-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 14px;
        color: #1E40AF;
        margin-bottom: 16px;
    }

    /* ── Force light background on main content ── */
    .stApp, .stApp > div, section.main, section.main > div,
    section[data-testid="stMain"], section[data-testid="stMain"] > div {
        background-color: #F8F7F4 !important;
    }

    /* ── All main area text dark ── */
    section[data-testid="stMain"] p,
    section[data-testid="stMain"] div,
    section[data-testid="stMain"] label,
    section[data-testid="stMain"] span,
    .stMarkdown p, .stText {
        color: #111827 !important;
    }

    /* ── Fix code tags in main area (not sidebar) ── */
    .main code, section[data-testid="stMain"] code {
        background-color: #E5E7EB;
        color: #111827;
        padding: 1px 6px;
        border-radius: 4px;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F8F7F4 !important;
        border-bottom: 2px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        color: #374151 !important;
        font-weight: 500;
        font-size: 14px;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1B4332 !important;
        border-bottom: 3px solid #1B4332 !important;
        font-weight: 700;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #F8F7F4 !important;
    }

    /* ── Inputs & selects ── */
    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stSelectbox select, div[data-baseweb="input"] input {
        background-color: white !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] div {
        background-color: white !important;
        color: #111827 !important;
    }

    /* ── Radio buttons ── */
    .stRadio label { color: #111827 !important; }
    .stRadio div { color: #111827 !important; }

    /* ── Checkboxes ── */
    .stCheckbox label { color: #111827 !important; }

    /* ── Sliders (main area) ── */
    .stSlider label { color: #374151 !important; }
    .stSlider [data-testid="stTickBar"] { color: #6B7280 !important; }

    /* ── Sidebar slider track — make filled portion visible ── */
    [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
        background-color: #f8f7f4 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] div[data-testid="stSliderThumbValue"] {
        color: #f8f7f4 !important;
    }

    /* ── Dataframe / table ── */
    .stDataFrame { background: white !important; }
    .stDataFrame th { background: #F3F4F6 !important; color: #111827 !important; }
    .stDataFrame td { color: #111827 !important; }

    /* ── Expanders ── */
    .streamlit-expanderHeader { color: #111827 !important; }
    .streamlit-expanderContent { background: white !important; color: #111827 !important; }

    /* ── Alerts / info / success ── */
    .stAlert { color: #111827 !important; }
    div[data-testid="stNotification"] { color: #111827 !important; }

    /* ── Number input label ── */
    .stNumberInput label { color: #111827 !important; }
    .stDateInput label { color: #111827 !important; }
    .stSelectbox label { color: #111827 !important; }
    .stTextInput label { color: #111827 !important; }
    .stFileUploader label { color: #111827 !important; }

    /* ══════════════════════════════════════════════
       SIDEBAR — nuclear option, every element white
       ══════════════════════════════════════════════ */

    [data-testid="stSidebar"] {
        background-color: #1B4332;
    }

    /* Every single element inside sidebar = white text */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] a {
        color: #f8f7f4 !important;
    }

    /* Slider numbers specifically */
    [data-testid="stSidebar"] [data-testid="stTickBar"] div,
    [data-testid="stSidebar"] [data-testid="stTickBar"] p,
    [data-testid="stSidebar"] [data-testid="stTickBar"] span,
    [data-testid="stSidebar"] .stSlider div,
    [data-testid="stSidebar"] .stSlider span,
    [data-testid="stSidebar"] .stSlider p {
        color: #f8f7f4 !important;
        background-color: transparent !important;
    }

    /* Selectbox in sidebar */
    [data-testid="stSidebar"] [data-baseweb="select"] div,
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] p {
        color: #f8f7f4 !important;
        background-color: #2D6A4F !important;
    }

    /* Sidebar inputs */
    [data-testid="stSidebar"] input {
        background-color: #2D6A4F !important;
        color: #f8f7f4 !important;
        border: 1px solid #40916C !important;
    }

    /* HR divider */
    [data-testid="stSidebar"] hr {
        border-color: #40916C !important;
    }

    /* ── Main area inputs stay white ── */
    section[data-testid="stMain"] input,
    section[data-testid="stMain"] .stDateInput input {
        background-color: white !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
    }

    /* ══════════════════════════════════════════════
       FILE UPLOADER DROPZONE
       ══════════════════════════════════════════════ */

    [data-testid="stFileUploadDropzone"] {
        background-color: #1B4332;
        border: 2px dashed #40916C;
        border-radius: 10px;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] p,
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: #f8f7f4 !important;
        -webkit-text-fill-color: #f8f7f4 !important;
        background-color: transparent !important;
    }
    /* Browse files button — override inherited white color from dark theme section */
    [data-testid="stFileUploadDropzone"] button[data-testid="baseButton-secondary"] {
        background-color: #f8f7f4 !important;
        border: 2px solid #1B4332 !important;
        border-radius: 6px !important;
        color: #1B4332 !important;
        -webkit-text-fill-color: #1B4332 !important;
    }
    [data-testid="stFileUploadDropzone"] button[data-testid="baseButton-secondary"] * {
        color: #1B4332 !important;
        -webkit-text-fill-color: #1B4332 !important;
    }

    /* ── Dataframe — force dark text on light background ── */
    [data-testid="stDataFrame"] *,
    [data-testid="stDataFrame"] td,
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] span,
    [data-testid="stDataFrame"] div {
        color: #111827 !important;
        background-color: transparent !important;
    }
    [data-testid="stDataFrame"] [data-testid="glideDataEditor"] {
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper Functions ──────────────────────────────────────────────────────────

def get_anniversary_this_year(hire_date, ref_date):
    try:
        ann = hire_date.replace(year=ref_date.year)
    except ValueError:
        ann = hire_date.replace(year=ref_date.year, day=28)
    return ann

def calculate_monthly_salary(row, month_date, raise_pct, benefits_pct, payroll_tax_pct,
                             bonus_frequency="Quarterly (Q1/Q2/Q3/Q4)",
                             increment_model="Anniversary Date",
                             fiscal_start_month=1):
    """Core projection logic mirroring the Google Sheet formula."""
    hire_date = pd.to_datetime(row["Hire Date"]).date()
    status = str(row.get("Status", "active")).strip().lower()
    def clean_currency(val):
        if isinstance(val, str):
            return float(val.replace("$", "").replace(",", "").strip() or 0)
        return float(val or 0)
    base = clean_currency(row.get("Base Salary", 0))

    # FTE % — defaults to 1.0 if not provided
    fte = float(row.get("FTE", 1.0) or 1.0)
    fte = max(0.0, min(1.0, fte))  # clamp between 0 and 1

    # Per-employee raise override — optional column, overrides sidebar %
    emp_raise = row.get("Annual Raise %", None)
    if emp_raise is not None and str(emp_raise).strip() not in ["", "nan", "None"]:
        try:
            effective_raise = float(str(emp_raise).replace("%", "").strip()) / 100
        except:
            effective_raise = raise_pct
    else:
        effective_raise = raise_pct

    # Bonus — fixed dollar or % of base
    bonus_raw = row.get("Annual Bonus", 0)
    bonus_type = str(row.get("Bonus Type", "Fixed $")).strip()
    if bonus_type == "% of Base":
        try:
            bonus_pct_val = float(str(bonus_raw).replace("%", "").replace("$", "").strip() or 0)
        except:
            bonus_pct_val = 0.0
        # bonus will be calculated after adj_base is known
        bonus_is_pct = True
    else:
        bonus = clean_currency(bonus_raw)
        bonus_is_pct = False

    # Inactive / terminated employees
    if status in ["inactive", "terminated"]:
        return 0.0, 0.0, 0.0, 0.0

    month_end = (month_date.replace(day=1) + relativedelta(months=1) - relativedelta(days=1))

    # Not yet hired this month
    if hire_date > month_end:
        return 0.0, 0.0, 0.0, 0.0

    # ── Raise logic ──────────────────────────────────────────────────
    today = date.today()

    if increment_model == "Anniversary Date":
        def next_anniversary(hd, from_date):
            ann = hd.replace(year=from_date.year)
            if ann < from_date:
                ann = hd.replace(year=from_date.year + 1)
            return ann

        future_raises = 0
        check = next_anniversary(hire_date, today)
        while check <= month_end:  # use month_end so raise applies in the anniversary month
            future_raises += 1
            try:
                check = hire_date.replace(year=check.year + 1)
            except ValueError:
                check = hire_date.replace(year=check.year + 1, day=28)
        adj_base = base * ((1 + effective_raise) ** future_raises)

    elif increment_model == "Fiscal Year Start — Full Raise":
        def next_fiscal_start(from_date, fy_month):
            fs = from_date.replace(month=fy_month, day=1)
            if fs < from_date:
                fs = fs.replace(year=from_date.year + 1)
            return fs

        future_raises = 0
        check = next_fiscal_start(today, fiscal_start_month)
        while check <= month_date:
            if check > hire_date:
                future_raises += 1
            check = check.replace(year=check.year + 1)
        adj_base = base * ((1 + effective_raise) ** future_raises)

    else:
        def next_fiscal_start(from_date, fy_month):
            fs = from_date.replace(month=fy_month, day=1)
            if fs < from_date:
                fs = fs.replace(year=from_date.year + 1)
            return fs

        adj_base = base
        check = next_fiscal_start(today, fiscal_start_month)
        first_raise = True

        while check <= month_date:
            if check > hire_date:
                if first_raise:
                    months_before_fy = (check.year - hire_date.year) * 12 + (check.month - hire_date.month)
                    months_worked_in_cycle = min(months_before_fy, 12)
                    prorated_raise = effective_raise * (months_worked_in_cycle / 12)
                    adj_base = adj_base * (1 + prorated_raise)
                    first_raise = False
                else:
                    adj_base = adj_base * (1 + effective_raise)
            check = check.replace(year=check.year + 1)

    # If bonus is % of base, calculate against projected (post-raise) salary
    if bonus_is_pct:
        bonus = adj_base * (bonus_pct_val / 100)

    monthly_base = (adj_base / 12) * fte

    # Proration for hire month
    month_start = month_date.replace(day=1)
    hire_month_start = max(month_start, hire_date)
    days_in_month = (month_end - month_start).days + 1
    days_worked = max(0, (month_end - hire_month_start).days + 1)
    monthly_base_prorated = monthly_base * days_worked / days_in_month if days_worked < days_in_month else monthly_base

    # Bonus payout based on selected frequency (also scaled by FTE)
    BONUS_MONTHS = {
        "Quarterly (Q1/Q2/Q3/Q4)": {1, 4, 7, 10},
        "Semi-Annual (Jun/Dec)":    {6, 12},
        "Annual (December)":        {12},
    }
    payout_months = BONUS_MONTHS.get(bonus_frequency, {1, 4, 7, 10})
    num_payouts = len(payout_months)
    bonus_month = ((bonus * fte) / num_payouts) if month_date.month in payout_months else 0.0

    gross = monthly_base_prorated + bonus_month
    benefits = gross * benefits_pct
    payroll_tax = gross * payroll_tax_pct
    ctc = gross + benefits + payroll_tax

    return round(gross, 2), round(benefits, 2), round(payroll_tax, 2), round(ctc, 2)


def run_projection(df, start_date, months, raise_pct, benefits_pct, payroll_tax_pct,
                   new_hires, terminations, dept_budgets,
                   bonus_frequency="Quarterly (Q1/Q2/Q3/Q4)",
                   increment_model="Anniversary Date",
                   fiscal_start_month=1):
    """Run full projection across all months."""
    results = []
    month_dates = [start_date + relativedelta(months=i) for i in range(months)]

    working_df = df.copy()

    # Apply terminations
    for term in terminations:
        mask = working_df["Employee Name"].str.strip().str.lower() == term["name"].strip().lower()
        eff = term["effective_date"]
        working_df.loc[mask, "_term_date"] = eff

    # Apply new hires
    new_hire_rows = []
    for nh in new_hires:
        new_hire_rows.append({
            "Employee ID": nh.get("id", "NH-" + nh["name"][:3].upper()),
            "Employee Name": nh["name"],
            "Department": nh["dept"],
            "Base Salary": nh["salary"],
            "Annual Bonus": nh.get("bonus", 0),
            "Hire Date": nh["hire_date"],
            "Status": "active",
            "_term_date": None,
            "_is_new_hire": True
        })
    if new_hire_rows:
        working_df = pd.concat([working_df, pd.DataFrame(new_hire_rows)], ignore_index=True)

    if "_term_date" not in working_df.columns:
        working_df["_term_date"] = None
    if "_is_new_hire" not in working_df.columns:
        working_df["_is_new_hire"] = False

    for month_date in month_dates:
        for _, row in working_df.iterrows():
            # Check termination
            term_date = row.get("_term_date")
            if pd.notna(term_date) and term_date is not None:
                try:
                    if pd.to_datetime(term_date).date() <= month_date:
                        continue
                except:
                    pass

            gross, benefits, payroll_tax, ctc = calculate_monthly_salary(
                row, month_date, raise_pct, benefits_pct, payroll_tax_pct,
                bonus_frequency, increment_model, fiscal_start_month
            )

            dept = str(row.get("Department", "Unassigned"))
            dept_budget = dept_budgets.get(dept, 0)

            results.append({
                "Month": month_date.strftime("%b %Y"),
                "Month_Date": month_date,
                "Employee ID": row.get("Employee ID", ""),
                "Employee Name": row.get("Employee Name", ""),
                "Department": dept,
                "Status": row.get("Status", "active"),
                "Is New Hire": row.get("_is_new_hire", False),
                "Base Salary": row.get("Base Salary", 0),
                "Gross Pay": gross,
                "Benefits": benefits,
                "Payroll Tax": payroll_tax,
                "Cost to Company": ctc,
                "Dept Monthly Budget": dept_budget / 12 if dept_budget else 0,
            })

    return pd.DataFrame(results)


def sample_data():
    return pd.DataFrame([
        {"Employee ID": "E001", "Employee Name": "Alice Johnson", "Department": "Engineering",
         "Base Salary": 120000, "Annual Bonus": 10, "Bonus Type": "% of Base",
         "Hire Date": "2020-03-15", "Status": "active", "FTE": 1.0, "Annual Raise %": ""},
        {"Employee ID": "E002", "Employee Name": "Bob Smith", "Department": "Finance",
         "Base Salary": 95000, "Annual Bonus": 9500, "Bonus Type": "Fixed $",
         "Hire Date": "2019-07-01", "Status": "active", "FTE": 1.0, "Annual Raise %": ""},
        {"Employee ID": "E003", "Employee Name": "Carol White", "Department": "Engineering",
         "Base Salary": 110000, "Annual Bonus": 10, "Bonus Type": "% of Base",
         "Hire Date": "2021-11-20", "Status": "active", "FTE": 1.0, "Annual Raise %": 6},
        {"Employee ID": "E004", "Employee Name": "David Lee", "Department": "HR",
         "Base Salary": 75000, "Annual Bonus": 5000, "Bonus Type": "Fixed $",
         "Hire Date": "2022-01-10", "Status": "active", "FTE": 0.5, "Annual Raise %": ""},
        {"Employee ID": "E005", "Employee Name": "Emma Davis", "Department": "Finance",
         "Base Salary": 88000, "Annual Bonus": 8000, "Bonus Type": "Fixed $",
         "Hire Date": "2018-05-22", "Status": "inactive", "FTE": 1.0, "Annual Raise %": ""},
        {"Employee ID": "E006", "Employee Name": "Frank Miller", "Department": "Engineering",
         "Base Salary": 130000, "Annual Bonus": 12, "Bonus Type": "% of Base",
         "Hire Date": "2017-09-01", "Status": "active", "FTE": 1.0, "Annual Raise %": ""},
        {"Employee ID": "E007", "Employee Name": "Grace Kim", "Department": "Finance",
         "Base Salary": 92000, "Annual Bonus": 8, "Bonus Type": "% of Base",
         "Hire Date": "2026-06-20", "Status": "active", "FTE": 1.0, "Annual Raise %": ""},
        {"Employee ID": "E008", "Employee Name": "Henry Torres", "Department": "Engineering",
         "Base Salary": 105000, "Annual Bonus": 10500, "Bonus Type": "Fixed $",
         "Hire Date": "2023-02-14", "Status": "active", "FTE": 1.0, "Annual Raise %": ""},
    ])


# ─── App Layout ────────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div style='padding: 32px 0 8px 0;'>
    <h1 style='font-size:38px; margin-bottom:4px; color:#111827;'>Payroll Projection Engine</h1>
    <p style='color:#6B7280; font-size:16px; margin:0;'>AI-assisted workforce cost forecasting — built by <a href='https://thefinanceforge.com' target='_blank' style='color:#1B4332; font-weight:600;'>The Finance Forge</a></p>
</div>
<hr style='border:none; border-top:1px solid #E5E7EB; margin:16px 0 24px 0;'>
""", unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Model Parameters")
    st.markdown("---")

    st.markdown("### Projection Window")
    start_month = st.date_input("Start Month", value=date.today().replace(day=1))
    projection_months = st.slider("Months to Project", 3, 36, 12)

    st.markdown("### Assumptions")
    st.markdown("<small>Industry benchmarks shown for reference</small>", unsafe_allow_html=True)

    raise_pct = st.slider("Annual Increment (%)", 0.0, 20.0, 5.0, 0.5) / 100
    st.markdown("<small>Industry avg: 3.5%</small>", unsafe_allow_html=True)

    benefits_pct = st.slider("Benefits Load (%)", 0.0, 50.0, 20.0, 1.0) / 100
    st.markdown("<small>Includes health, dental, vision, retirement (401k match), and other employer-paid benefits. Industry avg: 29.8%</small>", unsafe_allow_html=True)

    payroll_tax_pct = st.slider("Payroll Tax (%)", 0.0, 20.0, 7.65, 0.5) / 100
    st.markdown("<small>Industry avg: 10.0%</small>", unsafe_allow_html=True)

    st.markdown("### Increment Policy")
    increment_model = st.selectbox(
        "Raise applied on",
        [
            "Anniversary Date",
            "Fiscal Year Start — Full Raise",
            "Fiscal Year Start — Prorated First Year",
        ],
        index=0,
        help="Anniversary: each employee's raise on their hire date. Fiscal Year Full: everyone gets full raise on fiscal year start. Fiscal Year Prorated: first-year raise scaled by months worked."
    )
    if increment_model != "Anniversary Date":
        fiscal_month = st.selectbox(
            "Fiscal year starts in",
            ["January", "April", "July", "October"],
            index=0
        )
        FISCAL_MONTH_MAP = {"January": 1, "April": 4, "July": 7, "October": 10}
        fiscal_start_month = FISCAL_MONTH_MAP[fiscal_month]
    else:
        fiscal_start_month = 1

    st.markdown("### Bonus Frequency")
    bonus_frequency = st.selectbox(
        "Pay bonus",
        ["Quarterly (Q1/Q2/Q3/Q4)", "Semi-Annual (Jun/Dec)", "Annual (December)"],
        index=0
    )

    st.markdown("---")
    st.markdown("<small style='color:#A7F3D0;'>Use the Simulation tab to compare raise scenarios and run attrition analysis.</small>", unsafe_allow_html=True)
    st.markdown("---")

    # Quick-run button in sidebar
    if st.button("▶ Run Payroll Projection", key="sidebar_run_btn", use_container_width=True):
        st.session_state["trigger_run"] = True
        st.rerun()

    if st.session_state.get("projection_done"):
        st.markdown("<small style='color:#A7F3D0;'>✅ Projection complete! View in Projection Results tab.</small>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<small style='color:#A7F3D0;'>The Finance Forge © 2025</small>", unsafe_allow_html=True)

# ─── Main Content ──────────────────────────────────────────────────────────────

active_tab = st.session_state.get("active_tab", 0)

tab1, tab2, tab3, tab4 = st.tabs(["Data Input", "Projection Results", "Department View", "Simulation"])

# ══════════════════════════════════════════════════════════════════════
# TAB 1 — DATA INPUT
# ══════════════════════════════════════════════════════════════════════
with tab1:
    col_upload, col_info = st.columns([3, 2])

    with col_upload:
        st.markdown('<div class="section-header">Employee Data</div>', unsafe_allow_html=True)

        upload_mode = st.radio("Data Source", ["Upload Excel/CSV", "Use Sample Data"], horizontal=True)

        if upload_mode == "Upload Excel/CSV":
            # Template download
            template_df = pd.DataFrame([
                {"Employee ID": "E001", "Employee Name": "Jane Smith", "Department": "Engineering",
                 "Base Salary": 120000, "Annual Bonus": 10, "Bonus Type": "% of Base",
                 "Hire Date": "2022-06-01", "Status": "active", "FTE": 1.0, "Annual Raise %": ""},
                {"Employee ID": "E002", "Employee Name": "John Doe", "Department": "Finance",
                 "Base Salary": 95000, "Annual Bonus": 9500, "Bonus Type": "Fixed $",
                 "Hire Date": "2021-03-15", "Status": "active", "FTE": 1.0, "Annual Raise %": 6},
                {"Employee ID": "E003", "Employee Name": "Sara Lee", "Department": "HR",
                 "Base Salary": 70000, "Annual Bonus": 5000, "Bonus Type": "Fixed $",
                 "Hire Date": "2023-09-01", "Status": "active", "FTE": 0.5, "Annual Raise %": ""},
                {"Employee ID": "E004", "Employee Name": "Future Hire", "Department": "Engineering",
                 "Base Salary": 110000, "Annual Bonus": 8, "Bonus Type": "% of Base",
                 "Hire Date": "2026-07-01", "Status": "active", "FTE": 1.0, "Annual Raise %": ""},
            ])
            template_buffer = io.BytesIO()
            with pd.ExcelWriter(template_buffer, engine="openpyxl") as writer:
                template_df.to_excel(writer, index=False, sheet_name="Employees")
            st.download_button(
                "📥 Download Template",
                data=template_buffer.getvalue(),
                file_name="payroll_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download a pre-formatted Excel template with example rows"
            )

            uploaded_file = st.file_uploader(
                "Upload your employee file",
                type=["xlsx", "csv"],
                help="Required columns: Employee ID, Employee Name, Department, Base Salary, Annual Bonus, Hire Date, Status"
            )
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith(".csv"):
                        df_raw = pd.read_csv(uploaded_file)
                    else:
                        df_raw = pd.read_excel(uploaded_file)
                    st.session_state["df"] = df_raw
                    st.success(f"✅ Loaded {len(df_raw)} employees")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
        else:
            st.session_state["df"] = sample_data()
            st.info("Using sample dataset with 6 employees across 3 departments.")

    with col_info:
        st.markdown('<div class="section-header">Expected Format</div>', unsafe_allow_html=True)
        st.markdown("""
<div class='info-box'>
<b>Required columns:</b><br>
<b>Employee ID</b> · <b>Employee Name</b> · <b>Department</b><br>
<b>Base Salary</b> · <b>Annual Bonus</b> · <b>Hire Date</b> · <b>Status</b>
<br><br>
<b>Optional columns:</b><br>
<b>Bonus Type</b> — <code>Fixed $</code> (default) or <code>% of Base</code><br>
<b>FTE</b> — e.g. <code>0.5</code> for part-time, <code>1.0</code> for full-time (default)<br>
<b>Annual Raise %</b> — per-employee raise, overrides sidebar (e.g. <code>6</code> for 6%)<br><br>
Status values: <code>active</code> or <code>inactive</code><br>
Hire Date format: <code>YYYY-MM-DD</code> or <code>MM/DD/YYYY</code>
</div>
""", unsafe_allow_html=True)

    # Show loaded data
    if "df" in st.session_state:
        df = st.session_state["df"]
        st.markdown('<div class="section-header">Loaded Employees</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Department budgets
        st.markdown('<div class="section-header">Department Annual Budgets (Optional)</div>', unsafe_allow_html=True)
        st.markdown("Set annual payroll budgets per department to track variance.")

        depts = df["Department"].dropna().unique().tolist()
        dept_budgets = {}
        cols = st.columns(min(len(depts), 4))
        for i, dept in enumerate(depts):
            with cols[i % 4]:
                dept_budgets[dept] = st.number_input(
                    f"{dept}", min_value=0, value=0, step=10000,
                    key=f"budget_{dept}", format="%d"
                )
        st.session_state["dept_budgets"] = dept_budgets

        # New Hires
        st.markdown('<div class="section-header">Planned New Hires</div>', unsafe_allow_html=True)
        num_new_hires = st.number_input("Number of planned new hires", 0, 20, 0)
        new_hires = []
        if num_new_hires > 0:
            for i in range(int(num_new_hires)):
                with st.expander(f"New Hire {i+1}"):
                    c1, c2, c3, c4, c5 = st.columns(5)
                    nh_name = c1.text_input("Name", key=f"nh_name_{i}")
                    nh_dept = c2.selectbox("Department", depts, key=f"nh_dept_{i}")
                    nh_sal = c3.number_input("Base Salary", 0, 1000000, 80000, key=f"nh_sal_{i}")
                    nh_bonus = c4.number_input("Annual Bonus", 0, 200000, 0, key=f"nh_bonus_{i}")
                    nh_date = c5.date_input("Hire Date", key=f"nh_date_{i}")
                    new_hires.append({
                        "name": nh_name, "dept": nh_dept,
                        "salary": nh_sal, "bonus": nh_bonus,
                        "hire_date": str(nh_date)
                    })
        st.session_state["new_hires"] = new_hires

        # Terminations
        st.markdown('<div class="section-header">Planned Terminations</div>', unsafe_allow_html=True)
        num_terms = st.number_input("Number of planned terminations", 0, 50, 0)
        terminations = []
        if num_terms > 0:
            emp_names = df["Employee Name"].tolist()
            for i in range(int(num_terms)):
                c1, c2 = st.columns(2)
                term_name = c1.selectbox("Employee", emp_names, key=f"term_name_{i}")
                term_date = c2.date_input("Effective Date", key=f"term_date_{i}")
                terminations.append({"name": term_name, "effective_date": term_date})
        st.session_state["terminations"] = terminations

        st.markdown("---")
        triggered = st.button("Run Payroll Projection", key="main_run_btn") or st.session_state.pop("trigger_run", False)
        if triggered:
            with st.spinner("Calculating projections..."):
                try:
                    result_df = run_projection(
                        df=df,
                        start_date=start_month,
                        months=projection_months,
                        raise_pct=raise_pct,
                        benefits_pct=benefits_pct,
                        payroll_tax_pct=payroll_tax_pct,
                        new_hires=st.session_state.get("new_hires", []),
                        terminations=st.session_state.get("terminations", []),
                        dept_budgets=st.session_state.get("dept_budgets", {}),
                        bonus_frequency=bonus_frequency,
                        increment_model=increment_model,
                        fiscal_start_month=fiscal_start_month
                    )
                    st.session_state["result_df"] = result_df
                    st.session_state["increment_model_used"] = increment_model
                    st.session_state["projection_done"] = True
                except Exception as e:
                    st.error(f"Projection failed: {e}")

        if st.session_state.get("projection_done"):
            st.success("✅ Projection complete! Click the **Projection Results** tab above to view results.")


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — PROJECTION RESULTS
# ══════════════════════════════════════════════════════════════════════
with tab2:
    if "result_df" not in st.session_state:
        st.info("👈 Upload your data and click 'Run Payroll Projection' in the Data Input tab.")
    else:
        result_df = st.session_state["result_df"]
        model_used = st.session_state.get("increment_model_used", "Anniversary Date")
        st.markdown(
            f"<div style='font-size:13px; color:#6B7280; margin-bottom:8px;'>"
            f"Increment policy: <strong style='color:#1B4332;'>{model_used}</strong></div>",
            unsafe_allow_html=True
        )
        total_ctc = result_df["Cost to Company"].sum()
        total_gross = result_df["Gross Pay"].sum()
        total_benefits = result_df["Benefits"].sum()
        total_tax = result_df["Payroll Tax"].sum()
        avg_monthly = result_df.groupby("Month_Date")["Cost to Company"].sum().mean()
        active_emp = result_df[result_df["Month_Date"] == result_df["Month_Date"].min()]["Employee Name"].nunique()

        # Total company budget = sum of all dept budgets
        dept_budgets = st.session_state.get("dept_budgets", {})
        total_budget = sum(dept_budgets.values()) if dept_budgets else 0
        total_variance = total_ctc - total_budget if total_budget > 0 else None

        st.markdown('<div class="section-header">Summary Metrics</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Total Cost to Company</div>
                <div class='metric-value'>${total_ctc:,.0f}</div>
                <div class='metric-sub'>Over {projection_months} months</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Total Gross Pay</div>
                <div class='metric-value'>${total_gross:,.0f}</div>
                <div class='metric-sub'>Base + Bonus</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Avg Monthly CTC</div>
                <div class='metric-value'>${avg_monthly:,.0f}</div>
                <div class='metric-sub'>Per month</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Benefits + Tax Load</div>
                <div class='metric-value'>${(total_benefits+total_tax):,.0f}</div>
                <div class='metric-sub'>{((total_benefits+total_tax)/total_gross*100):.1f}% of gross</div>
            </div>""", unsafe_allow_html=True)

        # Company-level budget vs actual row (only shown if budgets were entered)
        if total_budget > 0:
            variance_color = "#DC2626" if total_variance > 0 else "#065F46"
            variance_label = "Over Budget" if total_variance > 0 else "Under Budget"
            variance_pct = abs(total_variance) / total_budget * 100
            cb1, cb2, cb3 = st.columns(3)
            with cb1:
                st.markdown(f"""<div class='metric-card'>
                    <div class='metric-label'>Total Company Budget</div>
                    <div class='metric-value'>${total_budget:,.0f}</div>
                    <div class='metric-sub'>Sum of all department budgets</div>
                </div>""", unsafe_allow_html=True)
            with cb2:
                st.markdown(f"""<div class='metric-card'>
                    <div class='metric-label'>Budget Variance</div>
                    <div class='{"metric-value-red" if total_variance > 0 else "metric-value-green"}'>${total_variance:+,.0f}</div>
                    <div class='metric-sub'>{variance_label} by {variance_pct:.1f}%</div>
                </div>""", unsafe_allow_html=True)
            with cb3:
                utilization = total_ctc / total_budget * 100
                util_color = "#DC2626" if utilization > 100 else "#1B4332"
                st.markdown(f"""<div class='metric-card'>
                    <div class='metric-label'>Budget Utilization</div>
                    <div class='{"metric-value-red" if utilization > 100 else "metric-value-green"}'>{utilization:.1f}%</div>
                    <div class='metric-sub'>Actual CTC vs total budget</div>
                </div>""", unsafe_allow_html=True)

        # Monthly trend chart
        st.markdown('<div class="section-header">Monthly Cost Trend</div>', unsafe_allow_html=True)
        monthly = result_df.groupby("Month_Date").agg(
            Gross_Pay=("Gross Pay", "sum"),
            Benefits=("Benefits", "sum"),
            Payroll_Tax=("Payroll Tax", "sum"),
            Cost_to_Company=("Cost to Company", "sum")
        ).reset_index()
        monthly["Month"] = monthly["Month_Date"].apply(lambda x: x.strftime("%b %Y"))

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Gross Pay", x=monthly["Month"], y=monthly["Gross_Pay"],
                             marker_color="#1B4332"))
        fig.add_trace(go.Bar(name="Benefits", x=monthly["Month"], y=monthly["Benefits"],
                             marker_color="#2D6A4F"))
        fig.add_trace(go.Bar(name="Payroll Tax", x=monthly["Month"], y=monthly["Payroll_Tax"],
                             marker_color="#74C69D"))
        fig.add_trace(go.Scatter(name="Total CTC", x=monthly["Month"], y=monthly["Cost_to_Company"],
                                 mode="lines+markers", line=dict(color="#B45309", width=2.5),
                                 marker=dict(size=7)))
        fig.update_layout(
            barmode="stack", height=380,
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="DM Sans", color="#111827"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color="#111827")),
            margin=dict(t=40, b=20, l=20, r=20),
            yaxis=dict(tickformat="$,.0f", gridcolor="#E5E7EB", tickfont=dict(color="#374151"), title_font=dict(color="#374151")),
            xaxis=dict(gridcolor="#E5E7EB", tickfont=dict(color="#374151"), title_font=dict(color="#374151"))
        )
        st.plotly_chart(fig, use_container_width=True)

        # Headcount trend
        st.markdown('<div class="section-header">Monthly Headcount</div>', unsafe_allow_html=True)
        headcount_monthly = result_df[result_df["Cost to Company"] > 0].groupby("Month_Date")["Employee Name"].nunique().reset_index()
        headcount_monthly.columns = ["Month_Date", "Headcount"]
        headcount_monthly["Month"] = headcount_monthly["Month_Date"].apply(lambda x: x.strftime("%b %Y"))

        fig_hc = go.Figure()
        fig_hc.add_trace(go.Bar(
            x=headcount_monthly["Month"],
            y=headcount_monthly["Headcount"],
            marker_color="#40916C",
            text=headcount_monthly["Headcount"],
            textposition="outside",
            textfont=dict(color="#374151", size=12)
        ))
        fig_hc.update_layout(
            height=280,
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="DM Sans", color="#111827"),
            yaxis=dict(gridcolor="#E5E7EB", tickfont=dict(color="#374151"),
                      title="Headcount", title_font=dict(color="#374151")),
            xaxis=dict(gridcolor="#E5E7EB", tickfont=dict(color="#374151")),
            margin=dict(t=30, b=20)
        )
        st.plotly_chart(fig_hc, use_container_width=True)
        st.markdown('<div class="section-header">Monthly Detail by Employee</div>', unsafe_allow_html=True)
        display_cols = ["Month", "Employee Name", "Department", "Gross Pay", "Benefits", "Payroll Tax", "Cost to Company"]
        disp = result_df[display_cols].copy()
        for col in ["Gross Pay", "Benefits", "Payroll Tax", "Cost to Company"]:
            disp[col] = disp[col].apply(lambda x: f"${x:,.2f}")
        st.dataframe(disp, use_container_width=True, hide_index=True)

        # Export
        st.markdown("---")
        export_df = result_df[display_cols].copy()
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Projection")
        st.download_button(
            "Download Full Projection (Excel)",
            data=buffer.getvalue(),
            file_name="payroll_projection.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — DEPARTMENT VIEW
# ══════════════════════════════════════════════════════════════════════
with tab3:
    if "result_df" not in st.session_state:
        st.info("👈 Run a projection first.")
    else:
        result_df = st.session_state["result_df"]
        dept_budgets = st.session_state.get("dept_budgets", {})

        st.markdown('<div class="section-header">Cost by Department</div>', unsafe_allow_html=True)

        dept_summary = result_df.groupby("Department").agg(
            Total_CTC=("Cost to Company", "sum"),
            Total_Gross=("Gross Pay", "sum"),
            Headcount=("Employee Name", "nunique")
        ).reset_index()

        dept_summary["Avg CTC / Employee"] = dept_summary["Total_CTC"] / dept_summary["Headcount"]
        dept_summary["Annual Budget"] = dept_summary["Department"].map(lambda d: dept_budgets.get(d, 0))
        dept_summary["Budget Variance"] = dept_summary["Annual Budget"] - dept_summary["Total_CTC"]

        # Donut chart
        col_chart, col_table = st.columns([2, 3])
        with col_chart:
            fig2 = px.pie(dept_summary, values="Total_CTC", names="Department",
                          hole=0.55, color_discrete_sequence=["#1B4332", "#2D6A4F", "#40916C", "#74C69D", "#B7E4C7"])
            fig2.update_layout(height=320, margin=dict(t=20, b=20),
                               font=dict(family="DM Sans"),
                               paper_bgcolor="white",
                               showlegend=True)
            fig2.update_traces(textinfo="percent+label")
            st.plotly_chart(fig2, use_container_width=True)

        with col_table:
            disp2 = dept_summary.copy()
            for col in ["Total_CTC", "Total_Gross", "Avg CTC / Employee", "Annual Budget", "Budget Variance"]:
                disp2[col] = disp2[col].apply(lambda x: f"${x:,.0f}")
            st.dataframe(disp2, use_container_width=True, hide_index=True)

        # Dept monthly trend
        st.markdown('<div class="section-header">Monthly Trend by Department</div>', unsafe_allow_html=True)
        dept_monthly = result_df.groupby(["Month_Date", "Department"])["Cost to Company"].sum().reset_index()
        dept_monthly["Month"] = dept_monthly["Month_Date"].apply(lambda x: x.strftime("%b %Y"))

        fig3 = px.line(dept_monthly, x="Month", y="Cost to Company", color="Department",
                       markers=True,
                       color_discrete_sequence=["#1B4332", "#2D6A4F", "#40916C", "#74C69D", "#B7E4C7", "#D8F3DC"])
        fig3.update_layout(height=350, plot_bgcolor="white", paper_bgcolor="white",
                           font=dict(family="DM Sans", color="#111827"),
                           yaxis=dict(tickformat="$,.0f", gridcolor="#E5E7EB", tickfont=dict(color="#374151")),
                           xaxis=dict(gridcolor="#E5E7EB", tickfont=dict(color="#374151")),
                           margin=dict(t=30, b=20))
        st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════
# TAB 4 — SIMULATION
# ══════════════════════════════════════════════════════════════════════
with tab4:
    if "df" not in st.session_state:
        st.info("👈 Load data first in the Data Input tab.")
    else:
        df = st.session_state["df"]

        # ── Section 1: Raise Sensitivity ──────────────────────────────
        st.markdown('<div class="section-header">What-If: Raise Sensitivity</div>', unsafe_allow_html=True)
        st.markdown("Compare three raise scenarios side by side. All other parameters use sidebar values.")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Scenario A** · Conservative")
            s_raise_a = st.slider("Raise %", 0.0, 20.0, 3.0, 0.5, key="sim_a") / 100
        with c2:
            st.markdown("**Scenario B** · Base Case")
            s_raise_b = st.slider("Raise %", 0.0, 20.0, 6.0, 0.5, key="sim_b") / 100
        with c3:
            st.markdown("**Scenario C** · Aggressive")
            s_raise_c = st.slider("Raise %", 0.0, 20.0, 10.0, 0.5, key="sim_c") / 100

        if st.button("Run Raise Simulation"):
            with st.spinner("Running 3 scenarios..."):
                scenarios = {}
                for label, r in [("Scenario A", s_raise_a), ("Scenario B", s_raise_b), ("Scenario C", s_raise_c)]:
                    sim = run_projection(
                        df=df, start_date=start_month, months=projection_months,
                        raise_pct=r, benefits_pct=benefits_pct, payroll_tax_pct=payroll_tax_pct,
                        new_hires=[], terminations=[], dept_budgets={},
                        bonus_frequency=bonus_frequency,
                        increment_model=increment_model,
                        fiscal_start_month=fiscal_start_month
                    )
                    monthly_sim = sim.groupby("Month_Date")["Cost to Company"].sum().reset_index()
                    monthly_sim["Scenario"] = f"{label} ({r*100:.1f}%)"
                    scenarios[label] = monthly_sim

                combined = pd.concat(scenarios.values())
                combined["Month"] = combined["Month_Date"].apply(lambda x: x.strftime("%b %Y"))

                fig4 = px.line(combined, x="Month", y="Cost to Company", color="Scenario",
                               markers=True,
                               color_discrete_sequence=["#1B4332", "#B45309", "#1D4ED8"])
                fig4.update_layout(height=360, plot_bgcolor="white", paper_bgcolor="white",
                                   font=dict(family="DM Sans", color="#111827"),
                                   yaxis=dict(tickformat="$,.0f", gridcolor="#E5E7EB", tickfont=dict(color="#374151")),
                                   xaxis=dict(gridcolor="#E5E7EB", tickfont=dict(color="#374151")),
                                   legend=dict(font=dict(color="#111827")),
                                   margin=dict(t=30, b=20))
                st.plotly_chart(fig4, use_container_width=True)

                totals = {label: scenarios[label]["Cost to Company"].sum() for label in scenarios}
                base_val = totals["Scenario A"]
                summary_sim = pd.DataFrame([
                    {
                        "Scenario": k,
                        "Total CTC": f"${v:,.0f}",
                        "vs Scenario A": f"+${v-base_val:,.0f}" if v > base_val else f"-${base_val-v:,.0f}"
                    }
                    for k, v in totals.items()
                ])
                st.dataframe(summary_sim, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ── Section 2: Attrition Analysis ─────────────────────────────
        st.markdown('<div class="section-header">Attrition Analysis</div>', unsafe_allow_html=True)
        st.markdown("""
        Model the cost impact of employee attrition over your projection window.
        Attrition rate is applied monthly — employees are probabilistically removed
        and **not backfilled**, showing the true cost reduction from natural turnover.
        """)

        col_a, col_b, col_c = st.columns(3)
        attrition_rate = col_a.slider("Annual Attrition Rate (%)", 0.0, 40.0, 10.0, 1.0) / 100
        col_b.metric("Monthly Exit Rate", f"{(attrition_rate/12)*100:.2f}%")
        active_count = len(df[df["Status"].str.lower() == "active"]) if "Status" in df.columns else len(df)
        expected_exits = round(active_count * attrition_rate)
        col_c.metric("Expected Annual Exits", f"{expected_exits} of {active_count} employees")

        if st.button("Run Attrition Analysis"):
            with st.spinner("Modelling attrition impact..."):

                monthly_attrition_rate = attrition_rate / 12
                active_df = df[df["Status"].str.strip().str.lower() == "active"].copy() if "Status" in df.columns else df.copy()

                no_attrition_results = []
                attrition_results = []
                headcount_track = []

                # Each employee has a survival probability that compounds monthly
                # survival_prob[i] = (1 - monthly_rate)^month_number
                # This shows a smooth, realistic cost reduction from month 1
                month_dates = [start_month + relativedelta(months=i) for i in range(projection_months)]

                for month_idx, month_date in enumerate(month_dates):
                    # Survival probability after month_idx+1 months of attrition
                    survival_prob = (1 - monthly_attrition_rate) ** (month_idx + 1)

                    base_cost = 0.0
                    att_cost = 0.0

                    for _, row in active_df.iterrows():
                        ctc = calculate_monthly_salary(
                            row, month_date, raise_pct, benefits_pct, payroll_tax_pct,
                            bonus_frequency, increment_model, fiscal_start_month
                        )[3]
                        base_cost += ctc
                        att_cost += ctc * survival_prob

                    no_attrition_results.append({"Month_Date": month_date, "Cost": base_cost, "Scenario": "No Attrition"})
                    attrition_results.append({
                        "Month_Date": month_date,
                        "Cost": att_cost,
                        "Scenario": f"With {attrition_rate*100:.0f}% Attrition"
                    })
                    # Expected headcount = active count × survival probability
                    headcount_track.append({
                        "Month_Date": month_date,
                        "Headcount": round(len(active_df) * survival_prob, 1),
                        "Month": month_date.strftime("%b %Y")
                    })

                att_combined = pd.DataFrame(no_attrition_results + attrition_results)
                att_combined["Month"] = att_combined["Month_Date"].apply(lambda x: x.strftime("%b %Y"))

                # Cost comparison chart
                fig5 = px.line(att_combined, x="Month", y="Cost", color="Scenario",
                               markers=True,
                               color_discrete_sequence=["#1B4332", "#DC2626"])
                fig5.update_layout(height=320, plot_bgcolor="white", paper_bgcolor="white",
                                   font=dict(family="DM Sans", color="#111827"),
                                   yaxis=dict(tickformat="$,.0f", gridcolor="#E5E7EB", tickfont=dict(color="#374151"), title="Monthly CTC", title_font=dict(color="#374151")),
                                   xaxis=dict(gridcolor="#E5E7EB", tickfont=dict(color="#374151")),
                                   legend=dict(font=dict(color="#111827")),
                                   margin=dict(t=30, b=20))
                st.plotly_chart(fig5, use_container_width=True)

                # Headcount trend
                hc_df = pd.DataFrame(headcount_track)
                fig6 = px.bar(hc_df, x="Month", y="Headcount",
                              color_discrete_sequence=["#40916C"])
                fig6.update_layout(height=240, plot_bgcolor="white", paper_bgcolor="white",
                                   font=dict(family="DM Sans", color="#111827"),
                                   yaxis=dict(gridcolor="#E5E7EB", tickfont=dict(color="#374151"), title="Headcount", title_font=dict(color="#374151")),
                                   xaxis=dict(gridcolor="#E5E7EB", tickfont=dict(color="#374151")),
                                   margin=dict(t=20, b=20))
                st.plotly_chart(fig6, use_container_width=True)

                # Summary
                total_no_att = sum(r["Cost"] for r in no_attrition_results)
                total_att = sum(r["Cost"] for r in attrition_results)
                savings = total_no_att - total_att
                final_headcount = round(len(active_df) * survival_prob)

                col1, col2, col3 = st.columns(3)
                col1.metric("Cost Without Attrition", f"${total_no_att:,.0f}")
                col2.metric("Cost With Attrition", f"${total_att:,.0f}")
                col3.metric("Total Cost Saving", f"${savings:,.0f}", delta=f"-{savings/total_no_att*100:.1f}%")
                st.caption(f"Final headcount after {projection_months} months: **{final_headcount}** employees (started with {active_count})")

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style='border:none; border-top:1px solid #E5E7EB; margin:40px 0 16px 0;'>
<div style='text-align:center; color:#9CA3AF; font-size:13px; padding-bottom:24px;'>
    Built by <a href='https://thefinanceforge.com' target='_blank' style='color:#1B4332; font-weight:600;'>The Finance Forge</a> · 
    Powered by Python + Streamlit · AI-assisted development
</div>
""", unsafe_allow_html=True)
