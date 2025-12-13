import streamlit as st
import pandas as pd

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="AI Career Recommendation System",
    layout="wide"
)

# -------------------- SESSION STATE --------------------
if "show_profile" not in st.session_state:
    st.session_state.show_profile = True

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# -------------------- LOAD DATA --------------------
REQUIRED_COLUMNS = {
    "company_name",
    "eligible_departments",
    "job_role",
    "min_cgpa",
    "package_lpa",
    "company_level",
    "company_locations"
}

try:
    df = pd.read_csv("company.csv")
except:
    st.error("company.csv not found. Please upload it.")
    st.stop()

if not REQUIRED_COLUMNS.issubset(df.columns):
    st.error(
        "company.csv columns mismatch.\n\n"
        f"Expected columns:\n{', '.join(REQUIRED_COLUMNS)}"
    )
    st.stop()

# -------------------- DEPARTMENT → ROLE MAP --------------------
DEPT_ROLE_MAP = {}
for _, row in df.iterrows():
    for dept in row["eligible_departments"].split("|"):
        DEPT_ROLE_MAP.setdefault(dept, set()).add(row["job_role"])

DEPT_ROLE_MAP = {k: sorted(v) for k, v in DEPT_ROLE_MAP.items()}

# -------------------- ROLE → SKILLS MAP --------------------
ROLE_TECH_SKILLS = {
    "ML Engineer": ["Python", "TensorFlow", "PyTorch"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
    "Backend Developer": ["Python", "Java", "SQL", "APIs"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "Python", "SQL"],
    "Site Engineer": ["AutoCAD", "Construction Planning"],
    "Automobile Engineer": ["CAD", "Manufacturing"],
    "Embedded Engineer": ["C", "Embedded C", "Microcontrollers"],
}

ROLE_CORE_SKILLS = {
    "ML Engineer": ["Math", "Problem Solving", "Model Optimization"],
    "Frontend Developer": ["Creativity", "Problem Solving"],
    "Backend Developer": ["Logic Building", "Problem Solving"],
    "Full Stack Developer": ["System Thinking", "Problem Solving"],
    "Site Engineer": ["Planning", "Execution"],
    "Automobile Engineer": ["Quality Focus", "Process Understanding"],
    "Embedded Engineer": ["Debugging", "Hardware Understanding"],
}

# -------------------- SIDEBAR --------------------
st.sidebar.markdown("## 👤 Student Profile")

if st.sidebar.button("👁️ Student Profile"):
    st.session_state.show_profile = not st.session_state.show_profile

if st.session_state.show_profile:

    department = st.sidebar.selectbox(
        "Department",
        sorted(DEPT_ROLE_MAP.keys())
    )

    role = st.sidebar.selectbox(
        "Interested Role",
        DEPT_ROLE_MAP.get(department, [])
    )

    cgpa = st.sidebar.slider("CGPA", 5.0, 9.5, 7.0, 0.1)

    internship = st.sidebar.selectbox(
        "Internship Completed?",
        ["Yes", "No"]
    )

    st.sidebar.markdown("## 🧠 Skill Self-Assessment")

    tech_ratings = {
        skill: st.sidebar.slider(skill, 1, 5, 3)
        for skill in ROLE_TECH_SKILLS.get(role, [])
    }

    core_ratings = {
        skill: st.sidebar.slider(skill, 1, 5, 3)
        for skill in ROLE_CORE_SKILLS.get(role, [])
    }

    submit = st.sidebar.button("🔍 Get Recommendations")

else:
    submit = False

# -------------------- MAIN HEADER --------------------
st.markdown(
    """
    <h1 style='text-align:center;'>🎓 AI Career Recommendation System</h1>
    <p style='text-align:center;'>Department-aware • Role-based • Skill-driven</p>
    """,
    unsafe_allow_html=True
)

# -------------------- PROCESS AFTER SUBMIT --------------------
if submit:

    st.session_state.show_profile = False
    st.session_state.submitted = True

    avg_tech = sum(tech_ratings.values()) / len(tech_ratings)
    avg_core = sum(core_ratings.values()) / len(core_ratings)

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

    # -------------------- FILTER COMPANIES --------------------
    df_filtered = df[
        (df["job_role"] == role) &
        (df["eligible_departments"].str.contains(department)) &
        (df["min_cgpa"] <= cgpa) &
        (df["company_level"].isin(allowed_levels))
    ]

    if len(df_filtered) < 5:
        df_filtered = df[
            (df["job_role"] == role) &
            (df["eligible_departments"].str.contains(department))
        ]

    df_final = df_filtered.head(5).reset_index(drop=True)
    df_final.index += 1

    # -------------------- COMPANY TABLE (NO PACKAGE) --------------------
    st.subheader("🏢 Company Recommendations")

    st.dataframe(
        df_final[[
            "company_name",
            "job_role",
            "company_level"
        ]],
        use_container_width=True
    )

    # -------------------- BEAUTIFIED MARKET INSIGHTS --------------------
    st.markdown("## 🚀 Role-Based Market Insights")

    for _, row in df_final.iterrows():
        st.markdown(
            f"""
            <div style="
                background:#0f172a;
                padding:16px;
                border-radius:12px;
                margin-bottom:14px;
                border-left:4px solid #38bdf8;
            ">
            <h4 style="color:#7dd3fc;">🏢 {row['company_name']}</h4>
            <p>👨‍💻 <b>Role:</b> {row['job_role']}</p>
            <p>🎓 <b>Stream:</b> {department}</p>
            <p>⭐ <b>Company Level:</b> {row['company_level']}</p>
            <p>🛠️ <b>Technologies:</b> {", ".join(ROLE_TECH_SKILLS.get(role, []))}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# -------------------- FOOTER --------------------
st.markdown(
    "<p style='text-align:center;'>Built with ❤️ using Data Science & AI</p>",
    unsafe_allow_html=True
)
