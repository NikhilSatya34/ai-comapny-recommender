import streamlit as st
import pandas as pd

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("company.csv")

st.set_page_config(page_title="AI Career Recommendation System", layout="centered")

st.title("🎓 AI-Based Company Recommendation System")
st.caption("Department-aware • Technology-driven • Adaptive AI Career Guidance")

# -----------------------------
# Department → Technology Mapping
# -----------------------------
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

# Technology → Domain Mapping
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

# -----------------------------
# User Inputs
# -----------------------------
department = st.selectbox(
    "Select Department",
    ["CSE", "CSE-DS", "AIML", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]
)

technology = st.selectbox(
    "Interested Technology",
    dept_tech_map[department]
)

cgpa = st.slider("CGPA", 5.0, 10.0, 7.0, step=0.1)

coding_level = st.selectbox("Coding Skill Level", ["Low", "Medium", "High"])
core_skill_level = st.selectbox("Core Skill Level", ["Low", "Medium", "High"])
internship = st.selectbox("Internship Completed?", ["Yes", "No"])

# -----------------------------
# Button Action
# -----------------------------
if st.button("🔍 Recommend Companies"):

    # -----------------------------
    # Step 1: Department Filter
    # -----------------------------
    df_dept = df[df["eligible_departments"].str.contains(department)].copy()

    # -----------------------------
    # Step 2: Numeric Mapping
    # -----------------------------
    level_map = {"Low": 1, "Medium": 2, "High": 3}

    df_dept.loc[:, "coding_num"] = df_dept["coding_level"].map(level_map)
    df_dept.loc[:, "core_num"] = df_dept["core_skill_level"].map(level_map)
    df_dept.loc[:, "intern_num"] = df_dept["internship_required"].map({"No": 0, "Yes": 1})

    # -----------------------------
    # Step 3: USER STRENGTH SCORE
    # -----------------------------
    user_strength = (
        (cgpa / 10) * 0.4 +
        (level_map[coding_level] / 3) * 0.3 +
        (level_map[core_skill_level] / 3) * 0.2 +
        (1 if internship == "Yes" else 0) * 0.1
    )

    if user_strength < 0.45:
        user_level = "LOW"
    elif user_strength < 0.7:
        user_level = "MEDIUM"
    else:
        user_level = "HIGH"

    # -----------------------------
    # Step 4: Adaptive Company Filtering
    # -----------------------------
    if user_level == "LOW":
        df_filtered = df_dept[df_dept["company_level"] == "LOW"]
        st.warning("🔰 Profile Level: Beginner – Showing startups & low-package companies")

    elif user_level == "MEDIUM":
        df_filtered = df_dept[df_dept["company_level"].isin(["LOW", "MID"])]
        st.info("⚡ Profile Level: Intermediate – Showing realistic growth opportunities")

    else:
        df_filtered = df_dept.copy()
        st.success("🚀 Profile Level: Advanced – Eligible for all companies")

    # -----------------------------
    # Step 5: Technology Filter
    # -----------------------------
    selected_domains = tech_domain_map[technology]
    df_filtered = df_filtered[df_filtered["preferred_domain"].isin(selected_domains)]

    # -----------------------------
    # Step 6: AI Match Scoring
    # -----------------------------
    df_filtered["match_score"] = (
        (df_filtered["min_cgpa"] / 10) * 0.35 +
        (df_filtered["coding_num"] / 3) * 0.30 +
        (df_filtered["core_num"] / 3) * 0.20 +
        (df_filtered["intern_num"]) * 0.15
    )

    df_filtered["match_percentage"] = (df_filtered["match_score"] * 100).round(2)

    # -----------------------------
    # Step 7: Output
    # -----------------------------
    top5 = df_filtered.sort_values("match_score", ascending=False).head(5)

    st.subheader("✅ Top Recommended Companies")
    st.dataframe(
        top5[["company_name", "match_percentage", "package_lpa"]],
        use_container_width=True
    )

    # -----------------------------
    # Guidance Message
    # -----------------------------
    if user_level == "LOW":
        st.caption("💡 Improve core skills and internships to unlock mid & high-tier companies.")
    elif user_level == "MEDIUM":
        st.caption("💡 Strengthen skills to reach top product-based companies.")
    else:
        st.caption("💡 Excellent profile! You are eligible for both startups and top MNCs.")
