import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Career Recommendation System",
    page_icon="🎓",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("company.csv")

# -----------------------------
# HEADER (PROFESSIONAL)
# -----------------------------
st.markdown(
    """
    <div style="padding:20px 0">
        <h1 style="text-align:center;color:#0f172a;">
            🎓 AI Career Recommendation System
        </h1>
        <p style="text-align:center;color:#475569;font-size:18px;">
            Smart • Department-aware • Technology-driven Career Guidance
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# SIDEBAR (USER INPUTS)
# -----------------------------
st.sidebar.header("👤 Student Profile")

department = st.sidebar.selectbox(
    "Department",
    ["CSE", "CSE-DS", "AIML", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]
)

dept_tech_map = {
    "CSE": ["Software Development", "Web Development", "Cloud / DevOps", "AI / ML", "Data Science", "FinTech"],
    "CSE-DS": ["Data Science", "AI / ML", "Cloud / DevOps", "Software Development"],
    "AIML": ["AI / ML", "Data Science", "Cloud / DevOps"],
    "AIDS": ["Data Science", "AI / ML", "Software Development"],
    "ECE": ["Embedded Systems", "Core Engineering", "AI / ML"],
    "EEE": ["Core Engineering", "Embedded Systems", "Energy Systems"],
    "MECH": ["Core Engineering", "Automobile", "Manufacturing"],
    "CIVIL": ["Core Engineering", "Construction", "Infrastructure"]
}

technology = st.sidebar.selectbox(
    "Interested Technology",
    dept_tech_map[department]
)

cgpa = st.sidebar.slider("CGPA", 5.0, 10.0, 7.0, step=0.1)
coding_level = st.sidebar.selectbox("Coding Skill Level", ["Low", "Medium", "High"])
core_skill_level = st.sidebar.selectbox("Core Skill Level", ["Low", "Medium", "High"])
internship = st.sidebar.selectbox("Internship Completed?", ["Yes", "No"])

st.sidebar.markdown("---")
recommend_btn = st.sidebar.button("🔍 Recommend Companies")

# -----------------------------
# MAIN CONTENT
# -----------------------------
if recommend_btn:

    # -----------------------------
    # PROFILE SUMMARY CARD
    # -----------------------------
    st.markdown(
        f"""
        <div style="
            background:#f8fafc;
            padding:20px;
            border-radius:12px;
            margin-bottom:20px;
            border:1px solid #e2e8f0;
        ">
        <h3>👤 Profile Summary</h3>
        <ul>
            <li><b>Department:</b> {department}</li>
            <li><b>Technology Interest:</b> {technology}</li>
            <li><b>CGPA:</b> {cgpa}</li>
            <li><b>Coding Skill:</b> {coding_level}</li>
            <li><b>Core Skill:</b> {core_skill_level}</li>
            <li><b>Internship:</b> {internship}</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------
    # FILTER BY DEPARTMENT
    # -----------------------------
    df_dept = df[df["eligible_departments"].str.contains(department)].copy()

    level_map = {"Low": 1, "Medium": 2, "High": 3}
    df_dept["coding_num"] = df_dept["coding_level"].map(level_map)
    df_dept["core_num"] = df_dept["core_skill_level"].map(level_map)
    df_dept["intern_num"] = df_dept["internship_required"].map({"No": 0, "Yes": 1})

    # -----------------------------
    # USER STRENGTH
    # -----------------------------
    user_strength = (
        (cgpa / 10) * 0.4 +
        (level_map[coding_level] / 3) * 0.3 +
        (level_map[core_skill_level] / 3) * 0.2 +
        (1 if internship == "Yes" else 0) * 0.1
    )

    if user_strength < 0.45:
        user_level = "LOW"
        st.warning("🔰 Beginner Profile – Startups & service companies recommended")
        df_filtered = df_dept[df_dept["company_level"] == "LOW"]

    elif user_strength < 0.7:
        user_level = "MEDIUM"
        st.info("⚡ Intermediate Profile – Growth-focused companies recommended")
        df_filtered = df_dept[df_dept["company_level"].isin(["LOW", "MID"])]

    else:
        user_level = "HIGH"
        st.success("🚀 Advanced Profile – Eligible for all companies")
        df_filtered = df_dept.copy()

    # -----------------------------
    # TECHNOLOGY FILTER
    # -----------------------------
    tech_domain_map = {
        "AI / ML": ["AI", "Data"],
        "Data Science": ["Data", "AI"],
        "Web Development": ["Software", "Ecommerce"],
        "Software Development": ["Software", "SaaS"],
        "Cloud / DevOps": ["Cloud"],
        "Embedded Systems": ["Embedded", "Hardware", "Semiconductor"],
        "Core Engineering": ["Automobile", "Construction", "Infrastructure", "Industrial", "Energy"],
        "FinTech": ["FinTech"],
        "Automobile": ["Automobile"],
        "Manufacturing": ["Industrial"],
        "Construction": ["Construction"],
        "Infrastructure": ["Infrastructure"],
        "Energy Systems": ["Energy"]
    }

    df_filtered = df_filtered[
        df_filtered["preferred_domain"].isin(tech_domain_map[technology])
    ]

    # -----------------------------
    # AI MATCH SCORE
    # -----------------------------
    df_filtered["match_score"] = (
        (df_filtered["min_cgpa"] / 10) * 0.35 +
        (df_filtered["coding_num"] / 3) * 0.30 +
        (df_filtered["core_num"] / 3) * 0.20 +
        (df_filtered["intern_num"]) * 0.15
    )

    df_filtered["match_percentage"] = (df_filtered["match_score"] * 100).round(2)
    top5 = df_filtered.sort_values("match_score", ascending=False).head(5)

    # -----------------------------
    # RESULTS DISPLAY (CARDS)
    # -----------------------------
    st.subheader("🏆 Top Recommended Companies")

    cols = st.columns(2)
    for idx, row in enumerate(top5.itertuples()):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div style="
                    background:white;
                    padding:20px;
                    border-radius:14px;
                    border:1px solid #e5e7eb;
                    box-shadow:0 4px 10px rgba(0,0,0,0.05);
                    margin-bottom:20px;
                ">
                <h3>{row.company_name}</h3>
                <p>🎯 <b>Match:</b> {row.match_percentage}%</p>
                <p>💰 <b>Package:</b> {row.package_lpa} LPA</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# -----------------------------
# FOOTER
# -----------------------------
st.divider()
st.markdown(
    "<p style='text-align:center;color:#64748b;'>Built with ❤️ using Data Science & AI</p>",
    unsafe_allow_html=True
)
