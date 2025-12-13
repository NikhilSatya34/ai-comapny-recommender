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

# -------------------- SIDEBAR AUTO HIDE CSS --------------------
if st.session_state.hide_sidebar:
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="stSidebarNav"] {
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

# -------------------- ROLE → SKILLS MAP --------------------
ROLE_TECH_SKILLS = {
    "ML Engineer": ["Python", "TensorFlow", "PyTorch"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
    "Backend Developer": ["Python", "Java", "SQL", "APIs"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "Python"],
    "Embedded Engineer": ["C", "Embedded C", "Microcontrollers"],
    "Mechanical Engineer": ["AutoCAD", "SolidWorks", "Manufacturing"]
}

ROLE_CORE_SKILLS = {
    "ML Engineer": ["Math", "Problem Solving", "Model Optimization"],
    "Frontend Developer": ["Creativity", "Problem Solving"],
    "Backend Developer": ["Logic Building"],
    "Full Stack Developer": ["System Thinking"],
    "Embedded Engineer": ["Debugging"],
    "Mechanical Engineer": ["Problem Solving", "Design Thinking"]
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

# -------------------- SIDEBAR --------------------
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

    tech_ratings = {}
    for skill in ROLE_TECH_SKILLS.get(role, []):
        tech_ratings[skill] = st.sidebar.slider(skill, 1, 5, 3)

    # ---------- Core Skills ----------
    st.sidebar.markdown("""
    <div style="background:#0f172a;padding:10px;border-radius:10px;margin-top:10px;">
    <h4 style="color:#fbbf24;">🧩 Core Skills</h4>
    </div>
    """, unsafe_allow_html=True)

    core_ratings = {}
    for skill in ROLE_CORE_SKILLS.get(role, []):
        core_ratings[skill] = st.sidebar.slider(skill, 1, 5, 3)

    submit = st.sidebar.button("🔍 Get Recommendations")

# -------------------- AFTER SUBMIT --------------------
if submit:
    st.session_state.submitted = True
    st.session_state.show_profile = False
    st.session_state.hide_sidebar = True

# ==================== RESULTS PAGE ====================
if st.session_state.submitted:

    # ---- SAFE AVERAGES ----
    avg_tech = sum(tech_ratings.values()) / len(tech_ratings) if tech_ratings else 3
    avg_core = sum(core_ratings.values()) / len(core_ratings) if core_ratings else 3

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

    df_final = df_filtered.head(5).copy()

    # -------------------- COMPANY TABLE WITH S.NO --------------------
    st.subheader("🏢 Company Recommendations")

    df_table = df_final[["company_name", "job_role", "company_level"]].copy()
    df_table.insert(0, "S.No", range(1, len(df_table) + 1))

    st.dataframe(df_table, use_container_width=True)

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
