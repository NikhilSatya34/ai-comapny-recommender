import streamlit as st
import pandas as pd

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="AI Career Recommendation System",
    layout="wide"
)

# -------------------- SESSION STATE --------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "show_profile" not in st.session_state:
    st.session_state.show_profile = True
if "hide_sidebar" not in st.session_state:
    st.session_state.hide_sidebar = False

# -------------------- SIDEBAR AUTO-HIDE CSS --------------------
if st.session_state.hide_sidebar:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# -------------------- LOAD DATA --------------------
df = pd.read_csv("company.csv")

# -------------------- DEPARTMENT → ROLE MAP --------------------
DEPT_ROLE_MAP = {}
for _, row in df.iterrows():
    for dept in row["eligible_departments"].split("|"):
        DEPT_ROLE_MAP.setdefault(dept, set()).add(row["job_role"])
DEPT_ROLE_MAP = {k: sorted(v) for k, v in DEPT_ROLE_MAP.items()}

# -------------------- ROLE → SKILLS MAP (FINAL) --------------------
ROLE_TECH_SKILLS = {
    # CSE / AIML
    "ML Engineer": ["Python", "TensorFlow", "PyTorch", "Pandas"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
    "Backend Developer": ["Python", "Java", "SQL", "APIs"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "Python", "SQL"],

    # CIVIL
    "Site Engineer": ["AutoCAD", "Estimation", "Surveying", "Construction Planning"],
    "Structural Engineer": ["STAAD Pro", "ETABS", "AutoCAD"],

    # MECH
    "Mechanical Engineer": ["AutoCAD", "SolidWorks", "Manufacturing"],

    # ECE / EEE
    "Embedded Engineer": ["C", "Embedded C", "Microcontrollers"]
}

ROLE_CORE_SKILLS = {
    # CSE / AIML
    "ML Engineer": ["Math", "Problem Solving", "Model Optimization"],
    "Frontend Developer": ["Creativity", "Problem Solving"],
    "Backend Developer": ["Logic Building", "Debugging"],
    "Full Stack Developer": ["System Thinking", "Problem Solving"],

    # CIVIL
    "Site Engineer": ["Planning", "Execution", "Safety Awareness"],
    "Structural Engineer": ["Analytical Thinking", "Attention to Detail"],

    # MECH
    "Mechanical Engineer": ["Problem Solving", "Design Thinking"],

    # ECE / EEE
    "Embedded Engineer": ["Debugging", "Hardware Understanding"]
}

# -------------------- HEADER WITH RIGHT BUTTON --------------------
col1, col2 = st.columns([8, 2])

with col1:
    st.markdown(
        """
        <h1>🎓 AI Career Recommendation System</h1>
        <p>Department-aware • Role-based • Skill-driven</p>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("👤 Student Profile"):
        st.session_state.show_profile = True
        st.session_state.hide_sidebar = False
        st.session_state.submitted = False

# -------------------- SIDEBAR INPUTS --------------------
submit = False

if st.session_state.show_profile:

    st.sidebar.markdown("## 👤 Student Profile")

    department = st.sidebar.selectbox(
        "Department",
        sorted(DEPT_ROLE_MAP.keys())
    )

    role = st.sidebar.selectbox(
        "Interested Role",
        DEPT_ROLE_MAP[department]
    )

    cgpa = st.sidebar.slider("CGPA", 5.0, 9.5, 7.0, 0.1)

    internship = st.sidebar.selectbox(
        "Internship Completed?",
        ["Yes", "No"]
    )

    st.sidebar.markdown("## 🧠 Skill Self-Assessment")

    # ---------- Technical Skills ----------
    st.sidebar.markdown("""
    <div style="background:#0f172a;padding:10px;border-radius:10px;">
    <h4 style="color:#38bdf8;">🛠️ Technical Skills</h4>
    </div>
    """, unsafe_allow_html=True)
   
    st.session_state.tech_ratings = {}
    
    for skill in ROLE_TECH_SKILLS.get(role, []):
        st.session_state.tech_ratings[skill] = st.sidebar.slider(
            skill, 1, 5, 3
        )


    # ---------- Core Skills ----------
    st.sidebar.markdown("""
    <div style="background:#0f172a;padding:10px;border-radius:10px;margin-top:10px;">
    <h4 style="color:#fbbf24;">🧩 Core Skills</h4>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.core_ratings = {}

    for skill in ROLE_CORE_SKILLS.get(role, []):
        st.session_state.core_ratings[skill] = st.sidebar.slider(
            skill, 1, 5, 3
        )


    submit = st.sidebar.button("🔍 Get Recommendations")

# -------------------- AFTER SUBMIT --------------------
if submit:
    st.session_state.submitted = True
    st.session_state.show_profile = False
    st.session_state.hide_sidebar = True

# ==================== RESULTS PAGE ====================
if st.session_state.submitted:

    tech_vals = st.session_state.tech_ratings.values()
    core_vals = st.session_state.core_ratings.values()

    avg_tech = sum(tech_vals) / len(tech_vals) if tech_vals else 3
    avg_core = sum(core_vals) / len(core_vals) if core_vals else 3


    final_score = (
        (cgpa / 10) * 0.30 +
        (avg_tech / 5) * 0.35 +
        (avg_core / 5) * 0.25 +
        (0.10 if internship == "Yes" else 0)
    )

    if final_score < 0.45:
        allowed_levels = ["LOW"]
        profile_label = "🟢 Beginner Profile"
    elif final_score < 0.70:
        allowed_levels = ["LOW", "MID"]
        profile_label = "🟡 Intermediate Profile"
    else:
        allowed_levels = ["MID", "HIGH"]
        profile_label = "🔵 Advanced Profile"

    st.info(profile_label)

    # -------------------- PROFILE BASED COMPANY SELECTION --------------------

def get_companies_by_level(level, limit):
    return df[
        (df["job_role"] == role) &
        (df["eligible_departments"].str.contains(department)) &
        (df["company_level"] == level) &
        (df["min_cgpa"] <= cgpa)
    ].head(limit)


# 🔵 Advanced Profile → 10 companies
if profile_label.startswith("🔵"):

    df_high = get_companies_by_level("HIGH", 3)
    df_mid  = get_companies_by_level("MID", 4)
    df_low  = get_companies_by_level("LOW", 3)

    df_final = pd.concat([df_high, df_mid, df_low])

# 🟡 Intermediate Profile → 5 companies
elif profile_label.startswith("🟡"):

    df_mid = get_companies_by_level("MID", 3)
    df_low = get_companies_by_level("LOW", 2)

    df_final = pd.concat([df_mid, df_low])

# 🟢 Beginner Profile → 5 companies
else:
    df_final = get_companies_by_level("LOW", 5)


# Safety fallback (if no data)
if df_final.empty:
    df_final = df[
        (df["job_role"] == role) &
        (df["eligible_departments"].str.contains(department))
    ].head(5)

    # -------------------- COMPANY TABLE (NO ROW NUMBERS) --------------------
    st.subheader("🏢 Company Recommendations")

    df_table = df_final[["company_name", "job_role", "company_level"]].reset_index(drop=True)

    st.dataframe(
        df_table,
        use_container_width=True,
        hide_index=True
    )

    # -------------------- MARKET INSIGHTS --------------------
    st.markdown("## 🚀 Role-Based Market Insights")

    for _, row in df_final.iterrows():
        st.markdown(
            f"""
            <div style="background:#0f172a;padding:16px;border-radius:12px;
                        margin-bottom:14px;border-left:4px solid #38bdf8;">
            <h4 style="color:#7dd3fc;">🏢 {row['company_name']}</h4>
            <p>👨‍💻 <b>Role:</b> {row['job_role']}</p>
            <p>🎓 <b>Stream:</b> {department}</p>
            <p>⭐ <b>Company Level:</b> {row['company_level']}</p>
            <p>📍 <b>Branches:</b> {row['company_locations']}</p>
            <p>🛠️ <b>Technologies:</b> {", ".join(ROLE_TECH_SKILLS.get(role, []))}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.info("👈 Please fill student profile and click **Get Recommendations**")

# -------------------- FOOTER --------------------
st.markdown(
    "<p style='text-align:center;'>Built with ❤️ using Data Science & AI</p>",
    unsafe_allow_html=True
)



