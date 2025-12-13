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
# HEADER (theme-safe)
# -------------------------------------------------
st.markdown(
    """
    <div style="
        background: linear-gradient(90deg, #2563eb, #1e40af);
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 18px;
    ">
        <h1 style="color:white; margin:0; font-size:28px;">
            🎓 AI Career Recommendation System
        </h1>
        <p style="color:#e0e7ff; margin:6px 0 0 0;">
            Department-aware • Role-based • Skill-driven • Location-aware
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# UTILS: safe read and helpers
# -------------------------------------------------
def safe_read_csv(path):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Failed to read {path}: {e}")
        return pd.DataFrame()

def parse_pipe_list(value):
    """Convert pipe-separated string into comma-joined string for display."""
    if pd.isna(value):
        return ""
    if isinstance(value, str):
        return ", ".join([p.strip() for p in value.split("|") if p.strip()])
    return str(value)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
company_df = safe_read_csv("company.csv")
role_df = safe_read_csv("role_market_data.csv")

# quick checks
required_company_cols = {"company_name", "eligible_departments", "job_role", "min_cgpa",
                         "package_lpa", "company_level", "company_locations"}
if not required_company_cols.issubset(set(company_df.columns)):
    st.warning("company.csv missing some expected columns. Expected columns: "
               + ", ".join(sorted(required_company_cols)))
# ensure numeric types
if "package_lpa" in company_df.columns:
    company_df["package_lpa"] = pd.to_numeric(company_df["package_lpa"], errors="coerce")
if "min_cgpa" in company_df.columns:
    company_df["min_cgpa"] = pd.to_numeric(company_df["min_cgpa"], errors="coerce")

# -------------------------------------------------
# ROLE → SKILL MAP (same as before)
# -------------------------------------------------
role_skill_map = {
    "Frontend Developer": {
        "technical": ["HTML", "CSS", "JavaScript", "React", "Git"],
        "core": ["UI Design", "Problem Solving", "Debugging"]
    },
    "Backend Developer": {
        "technical": ["Python", "Java", "Node.js", "SQL", "APIs"],
        "core": ["Logic Building", "System Design", "Debugging"]
    },
    "Full Stack Developer": {
        "technical": ["React", "Node.js", "SQL", "Docker"],
        "core": ["Architecture", "Problem Solving"]
    },
    "Data Analyst": {
        "technical": ["Python", "SQL", "Excel", "Power BI"],
        "core": ["Analytical Thinking", "Data Interpretation"]
    },
    "Data Scientist": {
        "technical": ["Python", "Pandas", "ML", "Statistics"],
        "core": ["Analytical Thinking", "Math"]
    },
    "ML Engineer": {
        "technical": ["Python", "TensorFlow", "PyTorch"],
        "core": ["Model Optimization", "Math"]
    },
    "Embedded Engineer": {
        "technical": ["C", "C++", "Embedded C", "RTOS"],
        "core": ["Hardware Debugging", "Circuit Analysis"]
    },
    "Power Engineer": {
        "technical": ["Power Systems", "PLC", "SCADA"],
        "core": ["Electrical Analysis", "Safety Standards"]
    },
    "Automobile Engineer": {
        "technical": ["Automobile Design", "CATIA"],
        "core": ["Mechanical Analysis", "Material Science"]
    },
    "Mechanical Design Engineer": {
        "technical": ["CAD", "SolidWorks", "ANSYS"],
        "core": ["Design Thinking", "Problem Solving"]
    },
    "Site Engineer": {
        "technical": ["AutoCAD", "Construction Planning"],
        "core": ["Site Management", "Quality Control"]
    },
    "Planning Engineer": {
        "technical": ["Estimation", "Primavera"],
        "core": ["Project Planning", "Cost Control"]
    }
}

# -------------------------------------------------
# SIDEBAR: inputs
# -------------------------------------------------
st.sidebar.header("👤 Student Profile")

department = st.sidebar.selectbox(
    "Department",
    ["CSE", "CSE-DS", "AIML", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]
)

dept_role_map = {
    "CSE": ["Frontend Developer", "Backend Developer", "Full Stack Developer"],
    "CSE-DS": ["Backend Developer", "Data Analyst", "Data Scientist"],
    "AIML": ["Data Scientist", "ML Engineer"],
    "AIDS": ["Data Analyst", "Data Scientist"],
    "ECE": ["Embedded Engineer"],
    "EEE": ["Power Engineer", "Embedded Engineer"],
    "MECH": ["Automobile Engineer", "Mechanical Design Engineer"],
    "CIVIL": ["Site Engineer", "Planning Engineer"]
}

job_role = st.sidebar.selectbox(
    "Interested Role",
    dept_role_map[department]
)

cgpa = st.sidebar.slider("CGPA", 5.0, 10.0, 7.0, step=0.1)

# skill rating using sliders (5-star feel)
st.sidebar.subheader("🧠 Skill Self-Assessment")
with st.sidebar.expander("💻 Technical Skill (Role-based)"):
    skills_text = ", ".join(role_skill_map.get(job_role, {}).get("technical", []))
    st.markdown("**Recommended Technologies to Learn:**  " + (skills_text or "—"))
    technical_skill = st.slider(
        "Rate your Technical Skill ⭐",
        1, 5, 3,
        help="1 = Beginner, 5 = Expert"
    )

with st.sidebar.expander("⚙️ Core Skill (Role-based)"):
    core_text = ", ".join(role_skill_map.get(job_role, {}).get("core", []))
    st.markdown("**Core skills required:**  " + (core_text or "—"))
    core_skill = st.slider(
        "Rate your Core Skill ⭐",
        1, 5, 3,
        help="1 = Beginner, 5 = Expert"
    )

internship = st.sidebar.selectbox("Internship Completed?", ["Yes", "No"])
recommend_btn = st.sidebar.button("🔍 Recommend Career Options")

# -------------------------------------------------
# MAIN: when user clicks recommend
# -------------------------------------------------
if recommend_btn:
    st.subheader("👤 Profile Summary")
    st.write(f"""
    • **Department:** {department}  
    • **Interested Role:** {job_role}  
    • **CGPA:** {cgpa}  
    • **Technical Skill:** ⭐ {technical_skill}/5  
    • **Core Skill:** ⭐ {core_skill}/5  
    • **Internship:** {internship}
    """)
    st.divider()

    # user strength calculation
    user_strength = (
        (cgpa / 10) * 0.5 +
        (technical_skill / 5) * 0.3 +
        (core_skill / 5) * 0.2
    )

    if user_strength < 0.45:
        user_level = "LOW"
        st.warning("🔰 Beginner Profile – Entry-level companies recommended")
    elif user_strength < 0.7:
        user_level = "MEDIUM"
        st.info("⚡ Intermediate Profile – Growth-focused companies recommended")
    else:
        user_level = "HIGH"
        st.success("🚀 Advanced Profile – Eligible for top companies")

    # -----------------------
    # Company recommendations
    # -----------------------
    st.subheader("🏢 Company Recommendations")

    # filter companies: department substring match (works with pipe-separated), role exact match, CGPA eligibility
    if company_df.empty:
        st.error("company.csv not loaded or empty.")
    else:
        df_filtered = company_df[
            company_df["eligible_departments"].str.contains(department, na=False) &
            (company_df["job_role"] == job_role) &
            (company_df["min_cgpa"] <= cgpa)
        ].copy()

        # apply company_level filter based on user_level
        if user_level == "LOW":
            df_filtered = df_filtered[df_filtered["company_level"].str.upper() == "LOW"]
        elif user_level == "MEDIUM":
            df_filtered = df_filtered[df_filtered["company_level"].str.upper().isin(["LOW", "MID"])]

        if df_filtered.empty:
            st.warning("No companies found matching your profile.")
        else:
            # ensure package_lpa numeric and fillna
            if "package_lpa" in df_filtered.columns:
                df_filtered["package_lpa"] = pd.to_numeric(df_filtered["package_lpa"], errors="coerce").fillna(0)

            top_companies = df_filtered.sort_values("package_lpa", ascending=False).head(10).reset_index(drop=True)
            # add S.No
            top_companies.insert(0, "S.No", range(1, len(top_companies) + 1))
            # format locations for display
            top_companies["company_locations"] = top_companies["company_locations"].apply(lambda v: parse_pipe_list(v))

            display_cols = ["S.No", "company_name", "job_role", "package_lpa", "company_level", "company_locations"]
            st.dataframe(top_companies[display_cols], use_container_width=True)

    st.divider()

    # -----------------------
    # Role-Based Market Insights (text display)
    # -----------------------
    st.subheader("🧑‍💻 Role-Based Market Insights")

    if role_df.empty:
        st.info("role_market_data.csv not loaded or empty.")
    else:
        role_filtered = role_df[
            (role_df["job_role"] == job_role) &
            (role_df["eligible_stream"].str.contains(department, na=False))
        ]

        if role_filtered.empty:
            st.info("No role-based market data available for this selection.")
        else:
            # Simple, readable text blocks for each company
            for _, row in role_filtered.iterrows():
                company_name = row.get("company_name", "")
                hiring_status = row.get("hiring_status", "")
                eligible_stream = row.get("eligible_stream", "")
                required_technologies = row.get("required_technologies", "")

                # convert possible pipe lists to readable form
                required_technologies_readable = parse_pipe_list(required_technologies)

                st.markdown(f"""
**🏢 Company:** {company_name}  
**📌 Hiring Status:** {hiring_status}  
**🎓 Eligible Stream:** {eligible_stream}  
**🛠 Recommended Technologies to Learn:** {required_technologies_readable}  

---
""")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.divider()
st.markdown(
    "<p style='text-align:center;color:#64748b;'>Built with ❤️ using Data Science & AI</p>",
    unsafe_allow_html=True
)
