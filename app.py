import os
import sqlite3
import hashlib
import pandas as pd
import streamlit as st
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MedPulse Clinical Data Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HIGH-CONTRAST STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #9edde6;
        color: #0F2942;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .hero-banner {
        background: linear-gradient(135deg, #0F2942 0%, #008080 100%);
        padding: 22px 28px;
        border-radius: 14px;
        margin-bottom: 18px;
        box-shadow: 0 6px 18px rgba(15, 41, 66, 0.14);
    }
    .hero-banner h1 {
        color: #FFFFFF !important;
        margin: 0;
        font-size: 1.9rem;
        font-weight: 700;
    }
    .hero-banner p {
        color: #E0FBFC !important;
        margin: 6px 0 0 0;
        font-size: 1rem;
    }

    /* Dark & crisp subheadings / section labels */
    h2, h3, .stMarkdown h2, .stMarkdown h3, [data-testid="stSubheader"] {
        color: #0F2942 !important;
        font-weight: 700 !important;
    }
    label, .stTextInput label, .stNumberInput label, .stSelectbox label,
    .stMultiSelect label, .stTextArea label, .stFileUploader label {
        color: #0F2942 !important;
        font-weight: 600 !important;
    }

    /* File uploader box color */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
        background-color: #a99b8b !important;
        color: #0F2942 !important;
    }
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] * {
        color: #0F2942 !important;
    }

    /* Tabs styling so every tab text is dark and clear */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #82ced8;
        padding: 6px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #0F2942 !important;
        font-weight: 700 !important;
        background-color: transparent;
        border-radius: 8px;
        padding: 8px 16px;
    }
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] div {
        color: #0F2942 !important;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F2942 !important;
        box-shadow: 0 2px 6px rgba(15, 41, 66, 0.12);
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-left: 5px solid #008080;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {
        color: #0F2942 !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {
        color: #0F2942 !important;
        font-weight: 800 !important;
    }

    .insight-card {
        background-color: #FFFFFF;
        border-left: 5px solid #0F2942;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(15, 41, 66, 0.06);
        color: #0F2942;
    }
    .insight-card.alert-high {
        border-left-color: #E63946;
    }
    .insight-card.alert-mod {
        border-left-color: #F4A261;
    }
    .insight-card.alert-ok {
        border-left-color: #008080;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F2942 0%, #1A3E5C 100%);
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: #E63946 !important;
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        font-weight: 700;
    }

    .stDownloadButton > button {
        background-color: #008080 !important;
        color: #FFFFFF !important;
        border-radius: 8px;
        border: none;
        padding: 10px 22px;
        font-weight: 600;
    }
    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: #FFFFFF !important;
    }
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #008080 0%, #0F2942 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 11px 22px !important;
        font-weight: 700 !important;
    }
    [data-testid="stFormSubmitButton"] button p,
    [data-testid="stFormSubmitButton"] button span {
        color: #FFFFFF !important;
    }
    .login-header {
        background: linear-gradient(135deg, #0F2942 0%, #008080 100%);
        padding: 24px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 16px;
    }
    .login-header h2 {
        color: #FFFFFF !important;
        margin: 0;
    }
    .login-header p {
        color: #E0FBFC !important;
        margin: 6px 0 0 0;
    }
</style>
""", unsafe_allow_html=True)

# --- SECURITY & DATABASE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "patients.db")


def hash_password(password: str) -> str:
    return hashlib.sha256(str(password).encode("utf-8")).hexdigest()


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", hash_password("med2026"))
        )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age REAL,
            height REAL,
            weight REAL,
            bmi REAL,
            condition TEXT,
            bp TEXT,
            status TEXT,
            age_group TEXT,
            risk_level TEXT,
            clinical_notes TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] == 0:
        initial_data = [
            ("Nimal", 45, 170.0, 68.0, 23.5, "Fever", "130/85", "Checked", "Junior", "Moderate Risk", "Mild fever and fatigue observed."),
            ("Kamal", 60, 165.0, 75.0, 27.5, "Normal", "120/85", "Checked", "Senior", "Normal", "Routine checkup, stable condition."),
            ("Sunil", 50, 175.0, 88.0, 28.7, "Hypertension", "160/100", "Checked", "Junior", "High Risk", "High BP recorded, prescribed medication."),
            ("Kumara", 38, 180.0, 72.0, 22.2, "Viral Flu", "125/80", "Checked", "Junior", "Moderate Risk", "Viral flu symptoms."),
            ("Asha", 29, 160.0, 54.0, 21.1, "Normal", "118/75", "Checked", "Junior", "Normal", "Healthy vitals."),
            ("Geetha", 65, 155.0, 70.0, 29.1, "Cardiac Risk", "170/110", "Checked", "Senior", "High Risk", "Hypertension advisory given.")
        ]
        cursor.executemany("""
            INSERT INTO patients (name, age, height, weight, bmi, condition, bp, status, age_group, risk_level, clinical_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_data)

    conn.commit()
    conn.close()


init_db()


def verify_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return bool(row and row[0] == hash_password(password))


def create_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "csv_df" not in st.session_state:
    st.session_state.csv_df = None
if "csv_name" not in st.session_state:
    st.session_state.csv_name = ""
if "last_uploaded_file_id" not in st.session_state:
    st.session_state.last_uploaded_file_id = None
if "use_csv_toggle" not in st.session_state:
    st.session_state.use_csv_toggle = False
if "auto_enable_csv" not in st.session_state:
    st.session_state.auto_enable_csv = False
if "filter_reset_nonce" not in st.session_state:
    st.session_state.filter_reset_nonce = 0


# --- AUTH SCREEN ---
def auth_screen():
    st.write("")
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.markdown("""
            <div class="login-header">
                <h2>🏥 MedPulse Clinical Portal</h2>
                <p>Healthcare Data Analytics & Patient Management System</p>
            </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔐 Staff Login", "📝 Create Account"])

        with tab_login:
            st.info("Demo Credentials — Username: `admin` | Password: `med2026`")
            with st.form("login_form"):
                u_name = st.text_input("Username")
                u_pass = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Sign In", use_container_width=True)

                if login_btn:
                    if verify_user(u_name.strip(), u_pass):
                        st.session_state.logged_in = True
                        st.session_state.current_user = u_name.strip()
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_signup:
            with st.form("signup_form"):
                new_u = st.text_input("New Username")
                new_p = st.text_input("New Password", type="password")
                conf_p = st.text_input("Confirm Password", type="password")
                signup_btn = st.form_submit_button("Create Account", use_container_width=True)

                if signup_btn:
                    if not new_u.strip() or not new_p:
                        st.warning("Username and password are required.")
                    elif new_p != conf_p:
                        st.error("Passwords do not match.")
                    elif len(new_p) < 4:
                        st.warning("Password must be at least 4 characters.")
                    else:
                        if create_user(new_u.strip(), new_p):
                            st.success("Account created! Please log in from the Staff Login tab.")
                        else:
                            st.error("Username already exists.")


if not st.session_state.logged_in:
    auth_screen()
    st.stop()


# --- DATA CLEANING & KAGGLE MAPPING ---
def normalize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.dropna(how="all", inplace=True)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    if "age" not in df.columns:
        for cand in ["patient_age", "age_years", "age_in_days"]:
            if cand in df.columns:
                vals = pd.to_numeric(df[cand], errors="coerce")
                df["age"] = (vals / 365.25).round(1) if cand == "age_in_days" else vals
                break
    else:
        df["age"] = pd.to_numeric(df["age"], errors="coerce")

    if "bmi" in df.columns:
        df["bmi"] = pd.to_numeric(df["bmi"], errors="coerce")
    elif "body_mass_index" in df.columns:
        df["bmi"] = pd.to_numeric(df["body_mass_index"], errors="coerce")
    elif "weight" in df.columns and "height" in df.columns:
        w = pd.to_numeric(df["weight"], errors="coerce")
        h = pd.to_numeric(df["height"], errors="coerce")
        h_m = h.where(h < 3.0, h / 100.0)
        df["bmi"] = (w / (h_m ** 2)).round(1)

    if "name" in df.columns and not df["name"].isna().all():
        df["record_label"] = df["name"].astype(str)
    elif "patient_id" in df.columns:
        df["record_label"] = df["patient_id"].astype(str)
    else:
        df["record_label"] = [f"Patient #{i + 1}" for i in range(len(df))]

    if "risk_level" not in df.columns:
        target_col = None
        for cand in ["outcome", "target", "cardio", "diagnosis", "risk", "class"]:
            if cand in df.columns:
                target_col = cand
                break

        if target_col is not None:
            def map_risk(val):
                s = str(val).strip().lower()
                if s in ["1", "true", "yes", "high", "high risk", "positive", "disease"]:
                    return "High Risk"
                if s in ["2", "moderate", "moderate risk", "medium"]:
                    return "Moderate Risk"
                return "Normal"
            df["risk_level"] = df[target_col].apply(map_risk)
        else:
            df["risk_level"] = "Normal"
    else:
        df["risk_level"] = df["risk_level"].fillna("Normal").astype(str)

    if "condition" not in df.columns:
        for cand in ["diagnosis", "outcome", "target", "class"]:
            if cand in df.columns:
                df["condition"] = df[cand].astype(str)
                break
        if "condition" not in df.columns:
            df["condition"] = df["risk_level"]

    if "clinical_notes" not in df.columns:
        df["clinical_notes"] = ""
    else:
        df["clinical_notes"] = df["clinical_notes"].fillna("")

    return df


def load_db_patients() -> pd.DataFrame:
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM patients", conn)
    conn.close()
    return normalize_dataset(df)


def style_chart(fig, title: str, height: int = 380):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#FFFFFF", size=16, family="Segoe UI")),
        paper_bgcolor="#0F2942",
        plot_bgcolor="#0F2942",
        font=dict(color="#FFFFFF", family="Segoe UI"),
        legend=dict(font=dict(color="#FFFFFF")),
        margin=dict(l=20, r=20, t=50, b=20),
        height=height
    )
    fig.update_xaxes(
        gridcolor="rgba(255, 255, 255, 0.14)",
        tickfont=dict(color="#FFFFFF"),
        title_font=dict(color="#FFFFFF")
    )
    fig.update_yaxes(
        gridcolor="rgba(255, 255, 255, 0.14)",
        tickfont=dict(color="#FFFFFF"),
        title_font=dict(color="#FFFFFF")
    )
    return fig


def build_clinical_summary(dataframe: pd.DataFrame, source_label: str) -> str:
    total = len(dataframe)
    high = int((dataframe["risk_level"] == "High Risk").sum()) if "risk_level" in dataframe.columns else 0
    mod = int((dataframe["risk_level"] == "Moderate Risk").sum()) if "risk_level" in dataframe.columns else 0
    norm = int((dataframe["risk_level"] == "Normal").sum()) if "risk_level" in dataframe.columns else 0
    mean_age = round(dataframe["age"].mean(), 1) if "age" in dataframe.columns and not dataframe["age"].dropna().empty else "N/A"
    mean_bmi = round(dataframe["bmi"].mean(), 1) if "bmi" in dataframe.columns and not dataframe["bmi"].dropna().empty else "N/A"

    return (
        f"MEDPULSE CLINICAL COHORT SUMMARY REPORT\n"
        f"========================================\n"
        f"Data Source      : {source_label}\n"
        f"Total Records    : {total}\n"
        f"High Risk Cases  : {high} ({round((high / total) * 100, 1) if total else 0}%)\n"
        f"Moderate Risk    : {mod}\n"
        f"Normal Cohort    : {norm}\n"
        f"Mean Patient Age : {mean_age} yrs\n"
        f"Mean Patient BMI : {mean_bmi}\n"
    )


# --- SIDEBAR ---
st.sidebar.markdown("## 🏥 MedPulse System")
st.sidebar.markdown(f"User: **{st.session_state.current_user}**")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.current_user = ""
    st.session_state.use_csv_toggle = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📂 Active Data Source")

csv_available = st.session_state.csv_df is not None
if not csv_available:
    st.session_state.use_csv_toggle = False
elif st.session_state.auto_enable_csv:
    st.session_state.use_csv_toggle = True
    st.session_state.auto_enable_csv = False

use_csv = st.sidebar.checkbox(
    "Use Uploaded Kaggle CSV Data",
    key="use_csv_toggle",
    disabled=not csv_available
)

if use_csv and csv_available:
    raw_active_df = st.session_state.csv_df.copy()
    active_source_name = f"CSV ({st.session_state.csv_name})"
    st.sidebar.success(f"CSV Active: {st.session_state.csv_name}")
else:
    raw_active_df = load_db_patients()
    active_source_name = "SQLite Database (patients.db)"
    st.sidebar.info("SQLite Database Active (patients.db)")

# --- SIDEBAR QUICK FILTERS ---
st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Quick Cohort Filters")

nonce = st.session_state.filter_reset_nonce
df = raw_active_df.copy()

if "age" in df.columns and not df["age"].dropna().empty:
    min_a = int(max(0, df["age"].min()))
    max_a = int(min(120, df["age"].max()))
    if min_a < max_a:
        age_range = st.sidebar.slider(
            "Age Range (Years)",
            min_value=min_a,
            max_value=max_a,
            value=(min_a, max_a),
            key=f"age_slider_{nonce}"
        )
        df = df[(df["age"].isna()) | ((df["age"] >= age_range[0]) & (df["age"] <= age_range[1]))]

if "bmi" in df.columns and not df["bmi"].dropna().empty:
    min_b = float(round(df["bmi"].min(), 1))
    max_b = float(round(df["bmi"].max(), 1))
    if min_b < max_b:
        bmi_cap = st.sidebar.slider(
            "Max BMI Filter",
            min_value=min_b,
            max_value=max_b,
            value=max_b,
            key=f"bmi_slider_{nonce}"
        )
        df = df[(df["bmi"].isna()) | (df["bmi"] <= bmi_cap)]

if st.sidebar.button("🔄 Reset Cohort Filters", use_container_width=True):
    st.session_state.filter_reset_nonce += 1
    st.rerun()

# --- HERO BANNER ---
st.markdown("""
    <div class="hero-banner">
        <h1>🏥 MedPulse Clinical Data Analytics</h1>
        <p>Real-time Patient Risk Stratification, Electronic Health Records & Interactive Insights</p>
    </div>
""", unsafe_allow_html=True)

# --- MAIN TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Clinical Overview",
    "📋 Patient Records & Search",
    "📈 Analytics & Charts",
    "➕ Register & BMI"
])

risk_palette = {
    "High Risk": "#E63946",
    "Moderate Risk": "#F4A261",
    "Normal": "#2A9D8F"
}

# --- TAB 1: CLINICAL OVERVIEW & KPIs ---
with tab1:
    st.subheader("Key Clinical Performance Indicators")
    k1, k2, k3, k4 = st.columns(4)
    total_rec = len(df)
    high_risk_rec = int((df["risk_level"] == "High Risk").sum()) if "risk_level" in df.columns else 0
    avg_age_val = round(df["age"].mean(), 1) if "age" in df.columns and not df["age"].dropna().empty else None
    avg_bmi_val = round(df["bmi"].mean(), 1) if "bmi" in df.columns and not df["bmi"].dropna().empty else None

    k1.metric("Total Registered Patients", total_rec)
    k2.metric("Critical / High Risk Cases", high_risk_rec)
    k3.metric("Mean Patient Age", f"{avg_age_val} yrs" if avg_age_val is not None else "N/A")
    k4.metric("Mean BMI", avg_bmi_val if avg_bmi_val is not None else "N/A")

    st.markdown("---")
    st.subheader("Automated Clinical Triage & Risk Alerts")
    i1, i2, i3 = st.columns(3)

    high_risk_pct = round((high_risk_rec / total_rec) * 100, 1) if total_rec > 0 else 0.0
    obese_cnt = int((df["bmi"] >= 30.0).sum()) if "bmi" in df.columns and not df["bmi"].dropna().empty else 0
    senior_high_cnt = int(((df["age"] >= 50) & (df["risk_level"] == "High Risk")).sum()) if ("age" in df.columns and "risk_level" in df.columns) else 0

    with i1:
        st.markdown(f"""
            <div class="insight-card alert-high">
                <strong>🚨 High-Risk Cohort Share</strong><br>
                <span>{high_risk_rec} of {total_rec} active records ({high_risk_pct}%) flagged as High Risk.</span>
            </div>
        """, unsafe_allow_html=True)
    with i2:
        st.markdown(f"""
            <div class="insight-card alert-mod">
                <strong>⚖️ Obesity Threshold (BMI ≥ 30)</strong><br>
                <span>{obese_cnt} patient(s) in current view meet clinical obesity criteria.</span>
            </div>
        """, unsafe_allow_html=True)
    with i3:
        st.markdown(f"""
            <div class="insight-card alert-ok">
                <strong>🩺 Senior High-Risk Priority (Age ≥ 50)</strong><br>
                <span>{senior_high_cnt} older adult(s) in High Risk category requiring close follow-up.</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Upload & Map Kaggle Medical CSV Dataset")
    uploaded_csv = st.file_uploader("Choose a CSV file", type=["csv"], key="overview_csv_uploader")
    if uploaded_csv is not None:
        file_token = f"{uploaded_csv.name}_{uploaded_csv.size}"
        if st.session_state.last_uploaded_file_id != file_token:
            try:
                raw_csv = pd.read_csv(uploaded_csv)
                cleaned_csv = normalize_dataset(raw_csv)
                st.session_state.csv_df = cleaned_csv
                st.session_state.csv_name = uploaded_csv.name
                st.session_state.last_uploaded_file_id = file_token
                st.session_state.auto_enable_csv = True
                st.rerun()
            except Exception as err:
                st.error(f"Could not process CSV file: {err}")
        elif st.session_state.csv_df is not None:
            st.success(f"Loaded '{st.session_state.csv_name}' ({len(st.session_state.csv_df)} rows). Toggle 'Use Uploaded Kaggle CSV Data' in the sidebar anytime to switch.")

# --- TAB 2: PATIENT RECORDS & SEARCH ---
with tab2:
    st.subheader("Search & Filter Patient Records")
    f1, f2 = st.columns([2, 1])
    risk_choices = list(df["risk_level"].dropna().unique()) if "risk_level" in df.columns else []
    with f1:
        chosen_risks = st.multiselect(
            "Filter by Risk Level",
            options=risk_choices,
            default=risk_choices
        )
    with f2:
        search_term = st.text_input("Search by Patient Name / ID", "")

    filtered_df = df.copy()
    if chosen_risks and "risk_level" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["risk_level"].isin(chosen_risks)]
    if search_term.strip():
        mask = filtered_df["record_label"].astype(str).str.contains(search_term.strip(), case=False, na=False)
        filtered_df = filtered_df[mask]

    st.subheader("Patient & Clinical Records Table")
    st.dataframe(filtered_df, use_container_width=True)

    ex1, ex2 = st.columns(2)
    with ex1:
        csv_export = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Filtered Records (CSV)",
            data=csv_export,
            file_name="medpulse_clinical_records.csv",
            mime="text/csv"
        )
    with ex2:
        summary_txt = build_clinical_summary(filtered_df, active_source_name).encode("utf-8")
        st.download_button(
            label="📄 Download Cohort Summary Report (.TXT)",
            data=summary_txt,
            file_name="medpulse_cohort_summary.txt",
            mime="text/plain"
        )

    if not (use_csv and csv_available) and "id" in raw_active_df.columns and not raw_active_df.empty:
        db_ids = raw_active_df["id"].dropna().astype(int).tolist()
        if db_ids:
            st.markdown("---")
            st.subheader("✏️ Update Patient Record (SQLite)")
            edit_id = st.selectbox("Select Patient ID to Update", options=db_ids, key="update_patient_id")
            cur_row = raw_active_df[raw_active_df["id"] == edit_id].iloc[0]

            with st.form("update_patient_form"):
                u_c1, u_c2 = st.columns(2)
                with u_c1:
                    upd_cond = st.text_input("Condition", value=str(cur_row.get("condition", "Normal")))
                    upd_bp = st.text_input("Blood Pressure (mmHg)", value=str(cur_row.get("bp", "120/80")))
                with u_c2:
                    risk_opts = ["Normal", "Moderate Risk", "High Risk"]
                    cur_risk = str(cur_row.get("risk_level", "Normal"))
                    r_idx = risk_opts.index(cur_risk) if cur_risk in risk_opts else 0
                    upd_risk = st.selectbox("Risk Level", options=risk_opts, index=r_idx)
                    upd_status = st.text_input("Status", value=str(cur_row.get("status", "Checked")))
                upd_notes = st.text_area("Clinical Notes", value=str(cur_row.get("clinical_notes", "")))

                if st.form_submit_button("🔄 Update Patient Record"):
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE patients
                        SET condition = ?, bp = ?, risk_level = ?, status = ?, clinical_notes = ?
                        WHERE id = ?
                    """, (upd_cond.strip(), upd_bp.strip(), upd_risk, upd_status.strip(), upd_notes.strip(), int(edit_id)))
                    conn.commit()
                    conn.close()
                    st.success(f"Updated record #{edit_id}.")
                    st.rerun()

            st.markdown("---")
            st.subheader("🗑️ Delete Patient Record (SQLite)")
            d_col1, d_col2 = st.columns([2, 1])
            with d_col1:
                selected_id = st.selectbox("Select Patient ID to Delete", options=db_ids, key="delete_patient_id")
            with d_col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete Selected Record", key="confirm_delete_btn"):
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM patients WHERE id = ?", (int(selected_id),))
                    conn.commit()
                    conn.close()
                    st.success(f"Deleted record with ID #{selected_id}.")
                    st.rerun()

# --- TAB 3: ANALYTICS & CHARTS ---
with tab3:
    st.subheader("Clinical Risk & Vitals Analytics")
    ch1, ch2 = st.columns(2)

    with ch1:
        if not df.empty and "risk_level" in df.columns:
            fig_pie = px.pie(
                df,
                names="risk_level",
                title="Patient Risk Distribution",
                hole=0.45,
                color="risk_level",
                color_discrete_map=risk_palette
            )
            st.plotly_chart(style_chart(fig_pie, "Patient Risk Distribution"), use_container_width=True)
        else:
            st.info("No risk data available.")

    with ch2:
        if not df.empty and "bmi" in df.columns and not df["bmi"].dropna().empty:
            plot_df = df.dropna(subset=["bmi"]).head(25)
            fig_bmi = px.bar(
                plot_df,
                x="record_label",
                y="bmi",
                color="risk_level",
                title="BMI by Patient (Up to 25 Records)",
                color_discrete_map=risk_palette
            )
            st.plotly_chart(style_chart(fig_bmi, "BMI by Patient (Up to 25 Records)"), use_container_width=True)
        elif not df.empty and "age" in df.columns and not df["age"].dropna().empty:
            plot_df = df.dropna(subset=["age"]).head(25)
            fig_age = px.bar(
                plot_df,
                x="record_label",
                y="age",
                color="risk_level",
                title="Age by Patient (Up to 25 Records)",
                color_discrete_map=risk_palette
            )
            st.plotly_chart(style_chart(fig_age, "Age by Patient (Up to 25 Records)"), use_container_width=True)
        else:
            st.info("No numeric BMI or Age values to plot.")

    st.markdown("---")
    st.subheader("Age vs. BMI Risk Correlation & Condition Breakdown")
    ch3, ch4 = st.columns(2)

    with ch3:
        if not df.empty and "age" in df.columns and "bmi" in df.columns:
            scat_df = df.dropna(subset=["age", "bmi"]).head(300)
            if not scat_df.empty:
                fig_scat = px.scatter(
                    scat_df,
                    x="age",
                    y="bmi",
                    color="risk_level",
                    hover_name="record_label",
                    title="Age vs. BMI Scatter (WHO Thresholds)",
                    color_discrete_map=risk_palette
                )
                fig_scat.add_hline(y=30.0, line_dash="dash", line_color="#E63946", annotation_text="Obesity (30)")
                fig_scat.add_hline(y=25.0, line_dash="dot", line_color="#F4A261", annotation_text="Overweight (25)")
                st.plotly_chart(style_chart(fig_scat, "Age vs. BMI Scatter (WHO Thresholds)"), use_container_width=True)
            else:
                st.info("Insufficient Age & BMI pairs for scatter plot.")
        else:
            st.info("Age or BMI columns not found in active dataset.")

    with ch4:
        biomarker_col = None
        for cand in ["glucose", "bloodpressure", "cholesterol", "ap_hi", "insulin"]:
            if cand in df.columns and not pd.to_numeric(df[cand], errors="coerce").dropna().empty:
                biomarker_col = cand
                break

        if biomarker_col is not None and "risk_level" in df.columns:
            bio_df = df.copy()
            bio_df[biomarker_col] = pd.to_numeric(bio_df[biomarker_col], errors="coerce")
            bio_df = bio_df.dropna(subset=[biomarker_col])
            fig_bio = px.box(
                bio_df,
                x="risk_level",
                y=biomarker_col,
                color="risk_level",
                title=f"{biomarker_col.replace('_', ' ').title()} Distribution by Risk Level",
                color_discrete_map=risk_palette
            )
            st.plotly_chart(style_chart(fig_bio, f"{biomarker_col.replace('_', ' ').title()} Distribution by Risk Level"), use_container_width=True)
        elif not df.empty and "condition" in df.columns:
            cond_counts = df["condition"].astype(str).value_counts().head(10).reset_index()
            cond_counts.columns = ["condition", "count"]
            fig_cond = px.bar(
                cond_counts,
                x="count",
                y="condition",
                orientation="h",
                title="Top Clinical Conditions / Categories",
                color="count",
                color_continuous_scale=["#82ced8", "#008080", "#0F2942"]
            )
            st.plotly_chart(style_chart(fig_cond, "Top Clinical Conditions / Categories"), use_container_width=True)
        else:
            st.info("No condition or biomarker data available.")

# --- TAB 4: REGISTER & BMI ---
with tab4:
    st.subheader("Register Patient, Calculate BMI & Save Clinical Notes")
    with st.form("intake_form"):
        c_left, c_right = st.columns(2)
        with c_left:
            p_name = st.text_input("Patient Full Name")
            p_age = st.number_input("Age (Years)", min_value=1, max_value=120, value=35)
            p_height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=168.0)
            p_weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=68.0)
        with c_right:
            p_condition = st.selectbox("Clinical Condition", ["Normal", "Fever", "Hypertension", "Diabetes", "Cardiac Risk", "Other"])
            p_bp = st.text_input("Blood Pressure (mmHg)", value="120/80")
            p_risk = st.selectbox("Risk Level", ["Normal", "Moderate Risk", "High Risk"])
            p_notes = st.text_area("Clinical Notes", placeholder="Enter symptoms, vitals summary, or follow-up notes...")

        save_btn = st.form_submit_button("💾 Save Patient Record to SQLite")
        if save_btn:
            if not p_name.strip():
                st.warning("Please enter the patient's name.")
            else:
                height_m = p_height / 100.0
                calc_bmi = round(p_weight / (height_m ** 2), 1)
                age_grp = "Senior" if p_age > 50 else "Junior"

                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO patients (name, age, height, weight, bmi, condition, bp, status, age_group, risk_level, clinical_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p_name.strip(),
                    float(p_age),
                    float(p_height),
                    float(p_weight),
                    float(calc_bmi),
                    p_condition,
                    p_bp.strip(),
                    "Checked",
                    age_grp,
                    p_risk,
                    p_notes.strip()
                ))
                conn.commit()
                conn.close()

                st.success(f"Saved '{p_name.strip()}' with calculated BMI: {calc_bmi}")
                st.rerun()