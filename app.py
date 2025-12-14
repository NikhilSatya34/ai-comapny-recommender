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
# -------------------- ROLE → TECHNICAL SKILLS --------------------
ROLE_TECH_SKILLS = {

    # ===== CSE / AIML / AIDS =====
    "ML Engineer": ["Python", "NumPy", "Pandas", "Scikit-learn", "TensorFlow", "PyTorch"],
    "Data Scientist": ["Python", "Statistics", "Machine Learning", "Data Visualization"],
    "Data Analyst": ["Python", "SQL", "Excel", "Power BI", "Tableau"],
    "AI Engineer": ["Python", "Deep Learning", "Neural Networks", "TensorFlow"],
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React"],
    "Backend Developer": ["Python", "Java", "SQL", "APIs"],
    "Full Stack Developer": ["HTML", "CSS", "JavaScript", "Python", "SQL"],

    # ===== CIVIL =====
    "Site Engineer": ["AutoCAD", "Estimation", "Surveying", "Construction Planning"],
    "Structural Engineer": ["AutoCAD", "STAAD Pro", "ETABS"],
    "Planning Engineer": ["MS Project", "Primavera", "Scheduling"],

    # ===== MECHANICAL =====
    "Mechanical Engineer": ["AutoCAD", "SolidWorks", "Manufacturing"],
    "Design Engineer": ["SolidWorks", "CATIA", "ANSYS"],
    "Production Engineer": ["Quality Control", "Lean Manufacturing"],

    # ===== ECE =====
    "Embedded Engineer": ["C", "Embedded C", "Microcontrollers", "RTOS"],
    "VLSI Engineer": ["Verilog", "VHDL", "FPGA"],

    # ===== EEE =====
    "Electrical Engineer": ["Power Systems", "MATLAB", "SCADA"],
    "Control Systems Engineer": ["PLC", "Automation", "MATLAB"]
}

# -------------------- ROLE → CORE SKILLS --------------------
ROLE_CORE_SKILLS = {

    # CSE / AIML / AIDS
    "ML Engineer": ["Problem Solving", "Analytical Thinking"],
    "Data Scientist": ["Critical Thinking", "Research Mindset"],
    "Data Analyst": ["Attention to Detail", "Analytical Thinking"],
    "AI Engineer": ["Logical Reasoning"],
    "Frontend Developer": ["Creativity", "UI Thinking"],
    "Backend Developer": ["Logic Building", "Debugging"],
    "Full Stack Developer": ["System Thinking"],

    # CIVIL
    "Site Engineer": ["Planning", "Execution", "Safety Awareness"],
    "Structural Engineer": ["Attention to Detail"],
    "Planning Engineer": ["Time Management"],

    # MECH
    "Mechanical Engineer": ["Problem Solving"],
    "Design Engineer": ["Creativity"],
    "Production Engineer": ["Process Optimization"],

    # ECE
    "Embedded Engineer": ["Debugging", "Hardware Understanding"],
    "VLSI Engineer": ["Analytical Thinking"],

    # EEE
    "Electrical Engineer": ["Troubleshooting", "Safety Awareness"],
    "Control Systems Engineer": ["Precision"]
}


# -------------------- HEADER --------------------
c1, c2 = st.columns([8, 2])
with c1:
    st.markdown("<h1>🎓 AI Career Recommendation System</h1>", unsafe_allow_html=True)
with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("👤 Student Profile"):
        st.session_state.show_profile = True
        st.session_state.hide_sidebar = False
        st.session_state.submitted = False

# -------------------- SIDEBAR --------------------
submit = False
if st.session_state.show_profile:
    st.sidebar.markdown("## 👤 Student Profile")

    department = st.sidebar.selectbox("Department", sorted(DEPT_ROLE_MAP.keys()))
    role = st.sidebar.selectbox("Interested Role", DEPT_ROLE_MAP[department])
    cgpa = st.sidebar.slider("CGPA", 5.0, 9.5, 7.0, 0.1)
    internship = st.sidebar.selectbox("Internship Completed?", ["Yes", "No"])
st.sidebar.markdown("## 🧠 Skill Self-Assessment")

# ================= TECHNICAL SKILLS BLOCK =================
st.sidebar.markdown("""
<div style="
    background:#0f172a;
    padding:12px;
    border-radius:12px;
    border-left:4px solid #38bdf8;
    margin-bottom:10px;
">
<h4 style="color:#38bdf8;">🛠️ Technical Skills</h4>
</div>
""", unsafe_allow_html=True)

st.session_state.tech_ratings = {}

for skill in ROLE_TECH_SKILLS.get(role, []):
    st.session_state.tech_ratings[skill] = st.sidebar.slider(
        skill, 1, 5, 3
    )

# ================= CORE SKILLS BLOCK =================
st.sidebar.markdown("""
<div style="
    background:#0f172a;
    padding:12px;
    border-radius:12px;
    border-left:4px solid #fbbf24;
    margin-top:12px;
">
<h4 style="color:#fbbf24;">🧩 Core Skills</h4>
</div>
""", unsafe_allow_html=True)

st.session_state.core_ratings = {}

for skill in ROLE_CORE_SKILLS.get(role, []):
    st.session_state.core_ratings[skill] = st.sidebar.slider(
        skill, 1, 5, 3
    )


submit = st.sidebar.button(
    "🔍 Get Recommendations",
    key="get_recommendations_btn"
)

if submit:
    st.session_state.submitted = True
    st.session_state.show_profile = False
    st.session_state.hide_sidebar = True

# ==================== RESULTS ====================
if st.session_state.submitted:

    tech_vals = list(st.session_state.tech_ratings.values())
    core_vals = list(st.session_state.core_ratings.values())

    avg_tech = sum(tech_vals)/len(tech_vals) if tech_vals else 3
    avg_core = sum(core_vals)/len(core_vals) if core_vals else 3

    final_score = (
        (cgpa / 10) * 0.30 +
        (avg_tech / 5) * 0.35 +
        (avg_core / 5) * 0.25 +
        (0.10 if internship == "Yes" else 0)
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
            (df.job_role == role) &
            (df.eligible_departments.str.contains(department)) &
            (df.company_level == level) &
            (df.min_cgpa <= cgpa)
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
        <div style="
            background: linear-gradient(135deg, #020617, #020617);
            border: 1px solid #1e293b;
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 18px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.35);
        ">

            <div style="display:flex;align-items:center;gap:12px;">
                <div style="
                    background:#0ea5e9;
                    color:black;
                    padding:10px;
                    border-radius:12px;
                    font-size:18px;
                ">🏢</div>

                <div>
                    <h3 style="margin:0;color:#e5e7eb;">
                        {r.company_name}
                    </h3>
                    <span style="
                        border:1px solid #334155;
                        padding:4px 10px;
                        border-radius:999px;
                        font-size:12px;
                        color:#38bdf8;
                    ">
                        {r.company_level} LEVEL
                    </span>
                </div>
            </div>

            <hr style="border:0;border-top:1px solid #1e293b;margin:14px 0;">

            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:12px;
                font-size:14px;
                color:#cbd5f5;
            ">
                <div>👨‍💻 <b>Role:</b> {r.job_role}</div>
                <div>🎓 <b>Stream:</b> {department}</div>
                <div>📍 <b>Locations:</b> {r.company_locations}</div>
                <div>🛠️ <b>Skills:</b> {", ".join(ROLE_TECH_SKILLS.get(role, []))}</div>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


else:
    st.info("👈 Fill profile and click Get Recommendations")

# -------------------- FOOTER --------------------
st.markdown("<p style='text-align:center;'>Built with ❤️ using Data Science & AI</p>", unsafe_allow_html=True)




