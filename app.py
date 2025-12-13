import streamlit as st
import pandas as pd

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Career Recommendation System",
    page_icon="🎓",
    layout="wide"
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
company_df = pd.read_csv("company.csv")
role_df = pd.read_csv("role_market_data.csv")

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
    """
    <h1 style="text-align:center;color:#0f172a;">
        🎓 AI Career Recommendation System
    </h1>
    <p style="text-align:center;color:#475569;font-size:18px;">
        Department-aware • Role-based • Technology-driven Career Guidance
    </p>
    """,
    unsafe_allow_html=True
)
st.divider()

# -------------------------------------------------
# SIDEBAR INPUTS
# -------------------------------------------------
st.sidebar.header("👤 Student Profile")

department = st.sidebar.selectbox(
    "Department",
    ["CSE", "CSE-DS", "AIML", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]
)

# Department → Role mapping
dept_role_map = {
    "CSE": ["Frontend Developer", "Backend Developer", "Full Stack Developer"],
    "CSE-DS": ["Data Scientist", "Backend Developer", "Full Stack Developer"],
    "AIML": ["ML Engineer", "Data Scientist"],
    "AIDS": ["Data Scientist"],
    "ECE": ["Embedded Engineer"],
    "EEE": ["Power Engineer", "Embedded Engineer"],
    "MECH": ["Automobile Engineer"],
    "CIVIL": ["Site Engineer"]
}

job_role = st.sidebar.selectbox(
    "Interested Role",
    dept_role_map[department]
)

cgpa = st.sidebar.slider("CGPA", 5.0, 10.0, 7.0, step=0.1)
coding_level = st.sidebar.selectbox("Coding Skill Level", ["Low", "Medium", "High"])
core_skill_level = st.sidebar.selectbox("Core Skill Level", ["Low", "Medium", "High"])
internship = st.sidebar.selectbox("Internship Completed?", ["Yes", "No"])

recommend_btn = st.sidebar.button("🔍 Recommend Career Options")

# -------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------
if recommend_btn:

    # -----------------------------
    # PROFILE SUMMARY
    # -----------------------------
    st.subheader("👤 Profile Summary")
    st.write(f"""
    - **Department:** {department}  
    - **Role Interested:** {job_role}  
    - **CGPA:** {cgpa}  
    - **Coding Skill:** {coding_level}  
    - **Core Skill:** {core_skill_level}  
    - **Internship:** {internship}
    """)
    st.divider()

    # -----------------------------
    # USER STRENGTH CALCULATION
    # -----------------------------
    level_map = {"Low": 1, "Medium": 2, "High": 3}

    user_strength = (
        (cgpa / 10) * 0.4 +
        (level_map[coding_level] / 3) * 0.3 +
        (level_map[core_skill_level] / 3) * 0.2 +
        (1 if internship == "Yes" else 0) * 0.1
    )

    if user_strength < 0.45:
        user_level = "LOW"
        st.warning("🔰 Beginner Profile – Startups & entry-level companies")
    elif user_strength < 0.7:
        user_level = "MEDIUM"
        st.info("⚡ Intermediate Profile – Growth-focused companies")
    else:
        user_level = "HIGH"
        st.success("🚀 Advanced Profile – Eligible for top companies")

    # -------------------------------------------------
    # COMPANY RECOMMENDATION (GENERAL)
    # -------------------------------------------------
    st.subheader("🏢 Company Recommendations")

    df_dept = company_df[
        company_df["eligible_departments"].str.contains(department)
    ].copy()

    if user_level == "LOW":
        df_dept = df_dept[df_dept["company_level"] == "LOW"]
    elif user_level == "MEDIUM":
        df_dept = df_dept[df_dept["company_level"].isin(["LOW", "MID"])]

    df_dept["coding_num"] = df_dept["coding_level"].map(level_map)
    df_dept["core_num"] = df_dept["core_skill_level"].map(level_map)
    df_dept["intern_num"] = df_dept["internship_required"].map({"No": 0, "Yes": 1})

    df_dept["match_score"] = (
        (df_dept["min_cgpa"] / 10) * 0.35 +
        (df_dept["coding_num"] / 3) * 0.30 +
        (df_dept["core_num"] / 3) * 0.20 +
        (df_dept["intern_num"]) * 0.15
    )

    df_dept["match_percentage"] = (df_dept["match_score"] * 100).round(2)

    top_companies = df_dept.sort_values(
        "match_score", ascending=False
    ).head(5)

    st.dataframe(
        top_companies[
            ["company_name", "match_percentage", "package_lpa", "company_level"]
        ],
        use_container_width=True
    )

    st.divider()

    # -------------------------------------------------
    # ROLE-BASED MARKET INSIGHTS (KEY FEATURE)
    # -------------------------------------------------
    st.subheader("🧑‍💻 Role-Based Market Insights")

    role_filtered = role_df[
        (role_df["job_role"] == job_role) &
        (role_df["eligible_stream"].str.contains(department))
    ]

    if role_filtered.empty:
        st.warning("No role-based data available.")
    else:
        for _, row in role_filtered.iterrows():
            status = row["hiring_status"]

            if status == "Actively Hiring":
                color = "#22c55e"
            elif status == "Limited Openings":
                color = "#facc15"
            else:
                color = "#ef4444"

            st.markdown(
                f"""
                <div style="
                    border:1px solid #e5e7eb;
                    padding:18px;
                    border-radius:14px;
                    margin-bottom:15px;
                    background:#ffffff;
                ">
                    <h4>{row['company_name']}</h4>
                    <p>📌 <b>Hiring Status:</b>
                       <span style="color:{color};font-weight:bold;">
                       {status}
                       </span>
                    </p>
                    <p>🎓 <b>Eligible Stream:</b> {row['eligible_stream']}</p>
                    <p>🛠 <b>Required Technologies:</b> {row['required_technologies']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.divider()
st.markdown(
    "<p style='text-align:center;color:#64748b;'>Built with ❤️ using Data Science & AI</p>",
    unsafe_allow_html=True
)
