import streamlit as st
import pandas as pd

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="AI Career Recommendation System", layout="wide")

# -------------------- SESSION STATE --------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "show_profile" not in st.session_state:
    st.session_state.show_profile = True
if "hide_sidebar" not in st.session_state:
    st.session_state.hide_sidebar = False
if "tech_ratings" not in st.session_state:
    st.session_state.tech_ratings = {}
if "core_ratings" not in st.session_state:
    st.session_state.core_ratings = {}

# -------------------- SIDEBAR AUTO HIDE --------------------
if st.session_state.hide_sidebar:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
            display:none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# -------------------- LOAD DATA --------------------
df = pd.read_csv("company.csv")

# -------------------- DEPT → ROLE MAP --------------------
DEPT_ROLE_MAP = {}
for _, row in df.iterrows():
    for d in row["eligible_departments"].split("|"):
        DEPT_ROLE_MAP.setdefault(d, set()).add(row["job_role"])
DEPT_ROLE_MAP = {k: sorted(v) for k, v in DEPT_ROLE_MAP.items()}

# -------------------- SKILLS --------------------
ROLE_TECH_SKILLS = {
    "ML Engineer": ["Python", "NumPy", "Pandas", "Scikit-learn"],
    "Data Analyst": ["Python", "SQL", "Excel", "Power BI"],
    "Backend Developer": ["Python", "Java", "SQL", "APIs"],
    "Embedded Engineer": ["C", "Embedded C", "Microcontrollers", "RTOS"]
}

ROLE_CORE_SKILLS = {
    "ML Engineer": ["Problem Solving"],
    "Data Analyst": ["Analytical Thinking"],
    "Backend Developer": ["Logic Building", "Debugging"],
    "Embedded Engineer": ["Hardware Understanding"]
}

# -------------------- HEADER --------------------
c1, c2 = st.columns([8, 2])
with c1:
    st.markdown("<h1>🎓 AI Career Recommendation System</h1>", unsafe_allow_html=True)
with c2:
    if st.button("👤 Student Profile"):
        st.session_state.show_profile = True
        st.session_state.hide_sidebar = False
        st.session_state.submitted = False

# -------------------- SIDEBAR --------------------
submit = False

if st.session_state.show_profile:
    st.sidebar.markdown("## 👤 Student Profile")

    st.session_state.department = st.sidebar.selectbox(
        "Department", sorted(DEPT_ROLE_MAP.keys())
    )
    st.session_state.role = st.sidebar.selectbox(
        "Interested Role", DEPT_ROLE_MAP[st.session_state.department]
    )
    st.session_state.cgpa = st.sidebar.slider("CGPA", 5.0, 9.5, 7.0, 0.1)
    st.session_state.internship = st.sidebar.selectbox(
        "Internship Completed?", ["Yes", "No"]
    )

    st.sidebar.markdown("## 🧠 Skill Self-Assessment")

# ---------- TECHNICAL SKILLS ----------
st.sidebar.markdown("""
<div style="background:#0f172a;padding:12px;border-radius:12px;
            border-left:4px solid #38bdf8;margin-bottom:10px;">
<h4 style="color:#38bdf8;">🛠️ Technical Skills</h4>
</div>
""", unsafe_allow_html=True)

st.session_state.tech_ratings = {}

tech_skills = ROLE_TECH_SKILLS.get(st.session_state.role, [])

if len(tech_skills) > 0:
    for skill in tech_skills:
        st.session_state.tech_ratings[skill] = st.sidebar.slider(
            skill, 1, 5, 3, key=f"tech_{skill}"
        )
else:
    st.sidebar.info("No technical skills mapped for this role")

# ---------- CORE SKILLS ----------
st.sidebar.markdown("""
<div style="background:#0f172a;padding:12px;border-radius:12px;
            border-left:4px solid #fbbf24;margin-top:12px;">
<h4 style="color:#fbbf24;">🧩 Core Skills</h4>
</div>
""", unsafe_allow_html=True)

st.session_state.core_ratings = {}

core_skills = ROLE_CORE_SKILLS.get(st.session_state.role, [])

if len(core_skills) > 0:
    for skill in core_skills:
        st.session_state.core_ratings[skill] = st.sidebar.slider(
            skill, 1, 5, 3, key=f"core_{skill}"
    )

else:
    st.sidebar.info("No core skills mapped for this role")

st.sidebar.markdown("<br>", unsafe_allow_html=True)

submit = st.sidebar.button(
    "🔍 Get Recommendations",
    key="get_recommendations_btn"
)


if submit:
    st.session_state.submitted = True
    st.session_state.show_profile = False
    st.session_state.hide_sidebar = True

# ==================== RESULTS ====================
df_final = pd.DataFrame()

if st.session_state.submitted:

    tech_vals = list(st.session_state.tech_ratings.values())
    core_vals = list(st.session_state.core_ratings.values())

    avg_tech = sum(tech_vals)/len(tech_vals) if tech_vals else 3
    avg_core = sum(core_vals)/len(core_vals) if core_vals else 3

    final_score = (
        (st.session_state.cgpa / 10) * 0.30 +
        (avg_tech / 5) * 0.35 +
        (avg_core / 5) * 0.25 +
        (0.10 if st.session_state.internship == "Yes" else 0)
    )

    if final_score >= 0.70:
        profile_label = "🔵 Advanced Profile"
    elif final_score >= 0.45:
        profile_label = "🟡 Intermediate Profile"
    else:
        profile_label = "🟢 Beginner Profile"

    st.info(profile_label)

    def get_companies(level, n):
        return df[
            (df.job_role == st.session_state.role) &
            (df.eligible_departments.str.contains(st.session_state.department)) &
            (df.company_level == level) &
            (df.min_cgpa <= st.session_state.cgpa)
        ].head(n)

    if profile_label.startswith("🔵"):
        df_final = pd.concat([
            get_companies("HIGH", 3),
            get_companies("MID", 4),
            get_companies("LOW", 3)
        ])
    elif profile_label.startswith("🟡"):
        df_final = pd.concat([
            get_companies("MID", 3),
            get_companies("LOW", 2)
        ])
    else:
        df_final = get_companies("LOW", 5)

    if df_final.empty:
        df_final = df.head(5)

    st.subheader("🏢 Company Recommendations")
    st.dataframe(
        df_final[["company_name", "job_role", "company_level"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("## 🚀 Role-Based Market Insights")
    for _, r in df_final.iterrows():
        st.markdown(
            f"""
            <div style="background:#020617;border:1px solid #1e293b;
                        border-radius:12px;padding:14px;margin-bottom:12px;">
                <b>{r.company_name}</b><br>
                Role: {r.job_role}<br>
                Level: {r.company_level}<br>
                Locations: {r.company_locations}
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.info("👉 Fill profile and click Get Recommendations")

# -------------------- FOOTER --------------------
st.markdown(
    "<p style='text-align:center;'>Built with ❤️ using Data Science & AI</p>",
    unsafe_allow_html=True
)


