import streamlit as st
import pandas as pd

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="AI Career Recommendation System",
    layout="wide"
)

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

# -------------------- ROLE → SKILLS MAP --------------------
ROLE_TECH_SKILLS = {
    "ML Engineer": ["Python", "TensorFlow", "PyTorch"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
    "Backend Developer": ["Python", "Java", "SQL", "APIs"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "Python", "SQL"],
    "Site Engineer": ["AutoCAD", "Construction Planning"],
    "Automobile Engineer": ["CAD", "Manufacturing", "Quality Control"],
    "Embedded Engineer": ["C", "Embedded C", "Microcontrollers"],
}

ROLE_CORE_SKILLS = {
    "ML Engineer": ["Math", "Problem Solving", "Model Optimization"],
    "Frontend Developer": ["Creativity", "Problem Solving"],
    "Backend Developer": ["Logic Building", "Problem Solving"],
    "Full Stack Developer": ["Problem Solving", "System Thinking"],
    "Site Engineer": ["Planning", "Execution", "Safety Awareness"],
    "Automobile Engineer": ["Process Understanding", "Quality Focus"],
    "Embedded Engineer": ["Debugging", "Hardware Understanding"],
}

# -------------------- SIDEBAR INPUT --------------------
st.sidebar.title("👤 Student Profile")

department = st.sidebar.selectbox(
    "Department",
    sorted(
        set(
            "|".join(df["eligible_departments"].unique()).split("|")
        )
    )
)

role = st.sidebar.selectbox(
    "Interested Role",
    sorted(df["job_role"].unique())
)

cgpa = st.sidebar.slider("CGPA", 5.0, 9.5, 7.0, 0.1)

internship = st.sidebar.selectbox(
    "Internship Completed?",
    ["Yes", "No"]
)

# -------------------- SKILL SELF-ASSESSMENT --------------------
st.sidebar.markdown("## 🧠 Skill Self-Assessment")

st.sidebar.markdown("### Technical Skills")
tech_ratings = {}
for skill in ROLE_TECH_SKILLS.get(role, []):
    tech_ratings[skill] = st.sidebar.slider(
        skill, 1, 5, 3
    )

st.sidebar.markdown("### Core Skills")
core_ratings = {}
for skill in ROLE_CORE_SKILLS.get(role, []):
    core_ratings[skill] = st.sidebar.slider(
        skill, 1, 5, 3
    )

avg_tech = sum(tech_ratings.values()) / len(tech_ratings)
avg_core = sum(core_ratings.values()) / len(core_ratings)

# -------------------- MAIN HEADER --------------------
st.markdown(
    """
    <h1 style='text-align:center;'>🎓 AI Career Recommendation System</h1>
    <p style='text-align:center;'>
    Department-aware • Role-based • Skill-driven • Realistic Guidance
    </p>
    """,
    unsafe_allow_html=True
)

# -------------------- PROFILE SUMMARY --------------------
st.subheader("👤 Profile Summary")
st.markdown(f"""
- **Department:** {department}  
- **Interested Role:** {role}  
- **CGPA:** {cgpa}  
- **Technical Skill Avg:** ⭐ {avg_tech:.1f}/5  
- **Core Skill Avg:** ⭐ {avg_core:.1f}/5  
- **Internship:** {internship}
""")

# -------------------- SCORE CALCULATION --------------------
final_score = (
    (cgpa / 10) * 0.30 +
    (avg_tech / 5) * 0.35 +
    (avg_core / 5) * 0.25 +
    (0.10 if internship == "Yes" else 0)
)

if final_score < 0.45:
    allowed_levels = ["LOW"]
    profile_label = "🟢 Beginner Profile – Startup & Entry-level companies shown"
elif final_score < 0.70:
    allowed_levels = ["LOW", "MID"]
    profile_label = "🟡 Intermediate Profile – Growth-focused companies shown"
else:
    allowed_levels = ["MID", "HIGH"]
    profile_label = "🔵 Advanced Profile – Product & top companies shown"

st.info(profile_label)

# -------------------- FILTER COMPANIES --------------------
df_filtered = df[
    (df["job_role"] == role) &
    (df["eligible_departments"].str.contains(department)) &
    (df["min_cgpa"] <= cgpa) &
    (df["company_level"].isin(allowed_levels))
]

# Fallback → always minimum 5 companies
if len(df_filtered) < 5:
    df_filtered = df[
        (df["job_role"] == role) &
        (df["eligible_departments"].str.contains(department))
    ]

df_final = df_filtered.head(5).reset_index(drop=True)
df_final.index += 1
df_final.index.name = "S.No"

# -------------------- COMPANY TABLE --------------------
st.subheader("🏢 Company Recommendations")

st.table(
    df_final[[
        "company_name",
        "job_role",
        "package_lpa",
        "company_level"
    ]]
)

# -------------------- MARKET INSIGHTS --------------------
st.subheader("🧑‍💼 Role-Based Market Insights")

for _, row in df_final.iterrows():
    st.markdown(f"""
**Company:** {row['company_name']}  
**Job Role:** {row['job_role']}  
**Eligible Stream:** {department}  
**Company Level:** {row['company_level']}  
**Recommended Technologies:** {", ".join(ROLE_TECH_SKILLS.get(role, []))}  
---
""")

st.markdown(
    "<p style='text-align:center;'>Built with ❤️ using Data Science & AI</p>",
    unsafe_allow_html=True
)
