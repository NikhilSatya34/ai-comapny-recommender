import streamlit as st
import pandas as pd

# Load data
df = pd.read_csv("company.csv")

st.title("🎓 AI-Based Company Recommendation System")

# User inputs
department = st.selectbox(
    "Select Department",
    ["CSE", "CSE-DS", "AIML", "AIDS", "ECE", "EEE", "MECH", "CIVIL"]
)

cgpa = st.slider("CGPA", 5.0, 10.0, 7.0)

coding_level = st.selectbox("Coding Skill Level", ["Low", "Medium", "High"])
core_skill_level = st.selectbox("Core Skill Level", ["Low", "Medium", "High"])
internship = st.selectbox("Internship Completed?", ["Yes", "No"])

if st.button("🔍 Recommend Companies"):

    # Filter by department
    df_dept = df[df["eligible_departments"].str.contains(department)].copy()

    level_map = {"Low": 1, "Medium": 2, "High": 3}

    df_dept.loc[:, "coding_num"] = df_dept["coding_level"].map(level_map)
    df_dept.loc[:, "core_num"] = df_dept["core_skill_level"].map(level_map)
    df_dept.loc[:, "intern_num"] = df_dept["internship_required"].map({"No": 0, "Yes": 1})

    df_dept["match_score"] = (
        (df_dept["min_cgpa"] / 10) * 0.35 +
        (df_dept["coding_num"] / 3) * 0.30 +
        (df_dept["core_num"] / 3) * 0.20 +
        (df_dept["intern_num"]) * 0.15
    )

    df_dept["match_percentage"] = (df_dept["match_score"] * 100).round(2)

    top5 = df_dept.sort_values("match_score", ascending=False).head(5)

    st.subheader("✅ Top Recommended Companies")
    st.dataframe(top5[["company_name", "match_percentage", "package_lpa"]])
