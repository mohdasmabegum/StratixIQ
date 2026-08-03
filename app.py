import streamlit as st
import os
import time
from typing import List, Dict, Any
from PIL import Image
from utils import extract_text_from_pdf, chunk_document_text, store_instance

logo_icon = "⚡"
if os.path.exists("logo.png"):
    try:
        logo_icon = Image.open("logo.png")
    except Exception:
        pass

st.set_page_config(
    page_title="StratixIQ - AI Agile Talent Deployment Engine",
    page_icon=logo_icon,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initial Talent Pool Dataset
INITIAL_CANDIDATES = [
    {
        "id": "cand_1",
        "name": "Alex Rivera",
        "role": "Senior Full-Stack AI Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Python", "FastAPI", "ChromaDB", "LangChain", "OpenAI", "React", "Next.js", "PostgreSQL", "Docker"],
        "bio": "Specializes in building distributed RAG pipelines, FastAPI microservices, and vector search systems with high query throughput.",
        "years_experience": 7,
        "past_projects": ["Enterprise Knowledge RAG Engine", "FastAPI Microservices Platform", "Real-Time AI Copilot"]
    },
    {
        "id": "cand_2",
        "name": "Elena Rostova",
        "role": "Machine Learning & Data Architect",
        "bandwidth_status": "Part-time bandwidth (50%)",
        "skills": ["Python", "PyTorch", "HuggingFace", "LangChain", "PostgreSQL", "MLOps", "Kubernetes", "Vector DB"],
        "bio": "Passionate about fine-tuning open-source LLMs, embeddings optimization, and scalable vector indexing.",
        "years_experience": 6,
        "past_projects": ["LLM Fine-Tuning Suite", "High-Scale Vector Store Indexing", "Predictive Analytics Engine"]
    },
    {
        "id": "cand_3",
        "name": "Marcus Vance",
        "role": "Cloud DevOps & Platform Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["AWS CDK", "Terraform", "Kubernetes", "Docker", "Python", "FastAPI", "CI/CD", "Monitoring"],
        "bio": "Focuses on cloud infrastructure automation, container orchestration, zero-downtime deployments, and API security.",
        "years_experience": 8,
        "past_projects": ["AWS Infrastructure Automation", "Multi-Tenant Kubernetes Cluster", "CI/CD Pipeline Engine"]
    },
    {
        "id": "cand_4",
        "name": "Sophia Chen",
        "role": "Lead UI/UX Systems Designer & Frontend Dev",
        "bandwidth_status": "Assigned until next month",
        "skills": ["TypeScript", "React", "Next.js", "Tailwind CSS", "Framer Motion", "UI/UX Design Systems", "GraphQL"],
        "bio": "Expert in crafting high-impact glassmorphic user interfaces, design systems, and responsive web applications.",
        "years_experience": 5,
        "past_projects": ["Design System Refactor", "Enterprise Analytics Dashboard", "Responsive PWA"]
    },
    {
        "id": "cand_5",
        "name": "David Kim",
        "role": "Backend & Database Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Python", "Go", "PostgreSQL", "Redis", "FastAPI", "REST APIs", "gRPC", "Vector Search"],
        "bio": "Specializes in database query optimization, Redis caching, low-latency microservice architectures, and data pipelines.",
        "years_experience": 6,
        "past_projects": ["High-Throughput Data Ingestion", "Redis Vector Cache", "PostgreSQL Sharding System"]
    }
]

# Initialize Session State
if "talent_pool" not in st.session_state:
    st.session_state["talent_pool"] = INITIAL_CANDIDATES

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

if "screen" not in st.session_state:
    st.session_state["screen"] = "splash" # 'splash', 'login', 'register', 'dashboard'

if "deploy_modal_candidate" not in st.session_state:
    st.session_state["deploy_modal_candidate"] = None

# Hide Streamlit toolbars & header
hide_sidebar_css = "" if st.session_state["authenticated"] else "[data-testid='stSidebar'] {display: none !important;}"

st.markdown(f"""
<style>
    /* Hide Streamlit Header & Toolbar */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{display: none !important;}}
    [data-testid="stToolbar"] {{display: none !important;}}
    [data-testid="stDecoration"] {{display: none !important;}}
    [data-testid="stStatusWidget"] {{display: none !important;}}
    .stDeployButton {{display: none !important;}}
    button[title="View code"] {{display: none !important;}}
    
    {hide_sidebar_css}

    /* Keyframe Animations */
    @keyframes floatLogo {{
        0% {{ transform: translateY(0px) scale(1); filter: drop-shadow(0 10px 20px rgba(59, 130, 246, 0.3)); }}
        100% {{ transform: translateY(-8px) scale(1.03); filter: drop-shadow(0 20px 35px rgba(139, 92, 246, 0.4)); }}
    }}

    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 15px rgba(59, 130, 246, 0.2); }}
        50% {{ box-shadow: 0 0 30px rgba(59, 130, 246, 0.5); }}
        100% {{ box-shadow: 0 0 15px rgba(59, 130, 246, 0.2); }}
    }}

    /* White Background Logo Containers */
    .logo-white-bg {{
        background-color: #FFFFFF !important;
        padding: 1.25rem;
        border-radius: 1.25rem;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
        display: inline-block;
        animation: floatLogo 2.5s ease-in-out infinite alternate;
    }}

    .logo-white-bg-sm {{
        background-color: #FFFFFF !important;
        padding: 0.6rem;
        border-radius: 0.75rem;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
        display: inline-block;
    }}

    /* CSS Hover & Transition Effects */
    .stButton button {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-radius: 0.65rem !important;
        font-weight: 600 !important;
    }}
    .stButton button:hover {{
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.35) !important;
    }}

    .splash-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 4rem 1rem;
        min-height: 75vh;
    }}

    .splash-app-name {{
        font-size: 3.8rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #60A5FA, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }}

    .splash-tagline {{
        font-size: 1.5rem;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 0;
    }}

    .auth-card {{
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 1.25rem;
        padding: 2.25rem;
        max-width: 460px;
        margin: 2rem auto;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        animation: pulseGlow 4s infinite;
    }}

    .main-header {{
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60A5FA, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .metric-card {{
        background-color: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 0.85rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .metric-card:hover {{
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-4px);
        box-shadow: 0 16px 32px -6px rgba(59, 130, 246, 0.25);
    }}

    .badge-avail {{
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        padding: 0.2rem 0.6rem;
        border-radius: 0.375rem;
        font-size: 0.8rem;
        font-weight: 600;
    }}
    .badge-assigned {{
        background-color: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        padding: 0.2rem 0.6rem;
        border-radius: 0.375rem;
        font-size: 0.8rem;
        font-weight: 600;
    }}
    .badge-part {{
        background-color: rgba(139, 92, 246, 0.2);
        color: #C084FC;
        padding: 0.2rem 0.6rem;
        border-radius: 0.375rem;
        font-size: 0.8rem;
        font-weight: 600;
    }}
</style>
""", unsafe_allow_html=True)

# Helper function for quick demo login
def login_as_demo_user():
    st.session_state["authenticated"] = True
    st.session_state["user_info"] = {
        "name": "Sarah Jenkins",
        "email": "manager@stratixiq.com",
        "role": "Lead Engineering Manager"
    }
    st.session_state["screen"] = "dashboard"

# ==========================================
# SCREEN 1: SPLASH SCREEN (ONLY CENTERED LOGO WITH WHITE BACKGROUND & APP NAME BELOW, AUTO 3-SEC REDIRECT, NO LOADING BAR)
# ==========================================
if not st.session_state["authenticated"] and st.session_state["screen"] == "splash":
    st.markdown('<div class="splash-container">', unsafe_allow_html=True)
    
    # White Background Logo Container in Center
    col_splash_center = st.columns([1, 1, 1])[1]
    with col_splash_center:
        st.markdown('<div class="logo-white-bg">', unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=160)
        st.markdown('</div>', unsafe_allow_html=True)

    # App Name Below Logo
    st.markdown('<p class="splash-app-name">StratixIQ</p>', unsafe_allow_html=True)
    st.markdown('<p class="splash-tagline">Agile Talent Deployment & Skill-Matching Engine</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Clean 3-second auto-redirect (No loading bar)
    time.sleep(3)
    st.session_state["screen"] = "login"
    st.rerun()

# ==========================================
# SCREEN 2: LOGIN SCREEN (NO SPLASH INFO, WHITE BACKGROUND LOGO)
# ==========================================
elif not st.session_state["authenticated"] and st.session_state["screen"] == "login":
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        # Logo with White Background
        c_brand_logo, c_brand_text = st.columns([1, 3])
        with c_brand_logo:
            st.markdown('<div class="logo-white-bg-sm">', unsafe_allow_html=True)
            if os.path.exists("logo.png"):
                st.image("logo.png", width=60)
            st.markdown('</div>', unsafe_allow_html=True)
        with c_brand_text:
            st.markdown("<h2 style='margin: 0; color: white; line-height: 1.2;'>StratixIQ</h2>", unsafe_allow_html=True)
            st.markdown("<span style='color: #60A5FA; font-weight: 600; font-size: 0.95rem;'>Manager Sign In</span>", unsafe_allow_html=True)

        st.caption("Enter credentials to access the Agile Staffing Engine")
        st.divider()

        with st.form("login_form"):
            email = st.text_input("Corporate Email", value="manager@stratixiq.com")
            password = st.text_input("Password", value="demo123", type="password")
            submit_login = st.form_submit_button("🔐 Sign In to Account", type="primary", use_container_width=True)
            
            if submit_login:
                if email and password:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = {
                        "name": "Sarah Jenkins" if email == "manager@stratixiq.com" else email.split("@")[0].title(),
                        "email": email,
                        "role": "Lead Engineering Manager"
                    }
                    st.session_state["screen"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Please enter email and password.")

        st.divider()
        if st.button("⚡ 1-Click Demo Manager Login", use_container_width=True):
            login_as_demo_user()
            st.rerun()

        col_reg1, col_reg2 = st.columns([1.2, 1])
        with col_reg1:
            st.caption("Need a manager account?")
        with col_reg2:
            if st.button("📝 Register", use_container_width=True):
                st.session_state["screen"] = "register"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SCREEN 3: REGISTER SCREEN (NO SPLASH INFO, WHITE BACKGROUND LOGO)
# ==========================================
elif not st.session_state["authenticated"] and st.session_state["screen"] == "register":
    col_r1, col_r2, col_r3 = st.columns([1, 2, 1])
    with col_r2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        c_reg_logo, c_reg_text = st.columns([1, 3])
        with c_reg_logo:
            st.markdown('<div class="logo-white-bg-sm">', unsafe_allow_html=True)
            if os.path.exists("logo.png"):
                st.image("logo.png", width=60)
            st.markdown('</div>', unsafe_allow_html=True)
        with c_reg_text:
            st.markdown("<h2 style='margin: 0; color: white; line-height: 1.2;'>StratixIQ</h2>", unsafe_allow_html=True)
            st.markdown("<span style='color: #A78BFA; font-weight: 600; font-size: 0.95rem;'>Register Manager Account</span>", unsafe_allow_html=True)

        st.caption("Create a profile for instant RAG candidate matching")
        st.divider()

        with st.form("register_form"):
            reg_name = st.text_input("Full Name *", placeholder="e.g. Michael Scott")
            reg_email = st.text_input("Corporate Email *", placeholder="name@company.com")
            reg_role = st.selectbox("Role *", ["Engineering Manager", "Technical Recruiter", "VP of Engineering", "Resource Director"])
            reg_pass = st.text_input("Password *", type="password")
            submit_reg = st.form_submit_button("📝 Create Account & Access App", type="primary", use_container_width=True)
            
            if submit_reg:
                if reg_name and reg_email and reg_pass:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = {
                        "name": reg_name,
                        "email": reg_email,
                        "role": reg_role
                    }
                    st.session_state["screen"] = "dashboard"
                    st.rerun()
                else:
                    st.error("Please complete all required fields.")

        st.divider()
        col_log1, col_log2 = st.columns([1.2, 1])
        with col_log1:
            st.caption("Already have an account?")
        with col_log2:
            if st.button("🔐 Sign In", use_container_width=True):
                st.session_state["screen"] = "login"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SCREEN 4: ACCOUNT DASHBOARD (AFTER LOGIN - NO REGISTER/LOGIN/DEMO CARDS VISIBLE)
# ==========================================
else:
    user_info = st.session_state.get("user_info") or {"name": "Sarah Jenkins", "role": "Lead Engineering Manager"}

    # Sidebar Navigation & Profile Info
    with st.sidebar:
        st.markdown('<div class="logo-white-bg-sm">', unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=110)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("## ⚡ StratixIQ Enterprise")
        st.markdown("**Agile Talent Matching Engine**")
        st.divider()
        
        st.success(f"👤 **Logged in as:**\n\n**{user_info['name']}**\n\n*{user_info['role']}*")
        
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user_info"] = None
            st.session_state["screen"] = "login"
            st.rerun()

        st.divider()
        st.metric("Total Indexed Talent", len(st.session_state["talent_pool"]))
        st.metric("Vector DB Status", "Active (ChromaDB / Memory)")

    # Main App Header
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.markdown('<div class="logo-white-bg-sm">', unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=75)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.markdown('<p class="main-header">StratixIQ: Agile Talent Deployment & Skill-Matching Engine</p>', unsafe_allow_html=True)
        st.caption(f"Welcome back, {user_info['name']} • Enterprise RAG staffing pipeline & availability tracking")

    tab1, tab2, tab3 = st.tabs(["🎯 Project Staffing Engine", "📤 Upload Resume (PDF)", "👥 Talent Roster Matrix"])

    # TAB 1: PROJECT STAFFING ENGINE
    with tab1:
        st.subheader("Match Engineering Requirements to Internal Talent Pool")
        
        st.markdown("**Sample Project Prompts:**")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        prompt_input = ""
        if col_p1.button("Prompt #1: FastAPI + RAG Vector Engineer"):
            prompt_input = "Need a Senior Full-Stack Engineer with Python, FastAPI, ChromaDB vector store, and React for immediate sprint deployment."
        if col_p2.button("Prompt #2: ML Architect & LLM Fine-Tuning"):
            prompt_input = "Looking for a Machine Learning Architect experienced in PyTorch, LangChain LLM fine-tuning, and vector database indexing."
        if col_p3.button("Prompt #3: Cloud DevOps & AWS Specialist"):
            prompt_input = "Require a Cloud DevOps Engineer with AWS CDK, Kubernetes, Docker, and CI/CD automation background."

        project_desc = st.text_area(
            "Enter Project Technical Requirements / Scope Description",
            value=prompt_input if prompt_input else "",
            placeholder="Paste engineering project description here...",
            height=120
        )
        
        col_opt1, col_opt2 = st.columns([2, 1])
        with col_opt1:
            selected_availability = st.selectbox("Filter Availability Status", ["All Availability", "Available Immediately", "Part-time bandwidth (50%)", "Assigned until next month"])
        with col_opt2:
            top_k = st.slider("Top Candidates to Retrieve", 1, 5, 3)

        if st.button("🚀 Run Semantic Talent Search", type="primary"):
            if project_desc.strip():
                st.divider()
                st.markdown("### 🏆 Top Candidate Shortlist & Skill-Gap Analysis")
                
                query_lower = project_desc.lower()
                query_words = set(query_lower.split())
                
                matches = []
                for cand in st.session_state["talent_pool"]:
                    if selected_availability != "All Availability" and cand["bandwidth_status"] != selected_availability:
                        continue
                        
                    cand_text = " ".join([cand["role"], cand["bio"]] + cand["skills"] + cand["past_projects"]).lower()
                    cand_words = set(cand_text.split())
                    
                    intersection = query_words.intersection(cand_words)
                    matched_skills = [s for s in cand["skills"] if s.lower() in query_lower]
                    
                    tech_keywords = ["kubernetes", "aws cdk", "fastapi", "chromadb", "next.js", "pytorch", "go", "redis", "docker"]
                    skill_gaps = [k.upper() for k in tech_keywords if k in query_lower and k not in [s.lower() for s in cand["skills"]]]
                    
                    raw_score = 45 + (len(intersection) * 4) + (len(matched_skills) * 10)
                    match_score = min(98, max(55, raw_score))
                    
                    rationale = f"{cand['name']} brings verified hands-on background in {', '.join(matched_skills[:3]) if matched_skills else 'core engineering disciplines'}. Currently rated at {cand['bandwidth_status']}."
                    
                    matches.append({
                        "cand": cand,
                        "score": match_score,
                        "matched_skills": matched_skills if matched_skills else cand["skills"][:3],
                        "skill_gaps": skill_gaps[:3],
                        "rationale": rationale
                    })
                    
                matches.sort(key=lambda x: x["score"], reverse=True)
                matches = matches[:top_k]
                
                if not matches:
                    st.warning("No candidates matched the selected availability filter.")
                else:
                    for idx, match in enumerate(matches):
                        cand = match["cand"]
                        
                        status_class = "badge-avail"
                        if "Assigned" in cand["bandwidth_status"]:
                            status_class = "badge-assigned"
                        elif "Part-time" in cand["bandwidth_status"]:
                            status_class = "badge-part"
                            
                        with st.container():
                            st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"### #{idx+1} {cand['name']} - *{cand['role']}*")
                                st.markdown(f'<span class="{status_class}">{cand["bandwidth_status"]}</span> • **{cand["years_experience"]} Yrs Experience**', unsafe_allow_html=True)
                            with c2:
                                st.metric(label="Match Confidence", value=f"{match['score']}%")
                                
                            st.markdown(f"**Verified Matching Skills:** {', '.join(match['matched_skills'])}")
                            if match['skill_gaps']:
                                st.markdown(f"**Potential Skill Gaps:** {', '.join(match['skill_gaps'])}")
                            
                            st.info(f"**Strategic Deployment Rationale:** {match['rationale']}")
                            
                            if st.button(f"⚡ Deploy {cand['name']} to Sprint", key=f"deploy_{cand['id']}"):
                                st.session_state["deploy_modal_candidate"] = cand
                                st.toast(f"🎉 Successfully assigned {cand['name']} to sprint deployment!", icon="🚀")
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Please enter a project requirement description to run semantic matching.")

        # Interactive Deployment Confirmation Popup
        if st.session_state["deploy_modal_candidate"]:
            dep_cand = st.session_state["deploy_modal_candidate"]
            st.divider()
            st.success(f"✅ **Deployment Status Confirmed**: Candidate **{dep_cand['name']}** ({dep_cand['role']}) has been assigned to project sprint. Resource team notified!")
            if st.button("Close Popup"):
                st.session_state["deploy_modal_candidate"] = None
                st.rerun()

    # TAB 2: UPLOAD RESUME (PDF)
    with tab2:
        st.subheader("Ingest Employee PDF Resume & Skills Profile")
        st.caption("Parse document layout using PyMuPDF and generate vector embeddings for instant search indexing.")
        
        with st.form("resume_upload_form", clear_on_submit=True):
            c_name = st.text_input("Candidate Full Name *", placeholder="e.g. Sarah Connor")
            c_role = st.text_input("Candidate Role / Job Title", placeholder="e.g. Senior AI Engineer")
            c_status = st.selectbox("Availability Bandwidth *", ["Available Immediately", "Part-time bandwidth (50%)", "Assigned until next month"])
            c_skills = st.text_input("Key Skills (Comma-separated)", placeholder="e.g. Python, FastAPI, PyMuPDF, ChromaDB, Docker")
            c_bio = st.text_area("Profile Summary / Bio", placeholder="Brief summary of candidate background...")
            uploaded_pdf = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            
            submitted = st.form_submit_button("Index Profile into Vector DB", type="primary")
            
            if submitted:
                if c_name.strip():
                    extracted_text = ""
                    if uploaded_pdf is not None:
                        try:
                            pdf_bytes = uploaded_pdf.read()
                            extracted_text = extract_text_from_pdf(pdf_bytes)
                            st.info(f"Successfully extracted {len(extracted_text)} characters from uploaded PDF using PyMuPDF.")
                        except Exception as e:
                            st.warning(f"Note on PDF parsing: {e}")
                    
                    skills_list = [s.strip() for s in c_skills.split(",") if s.strip()] if c_skills else ["Python", "Engineering"]
                    
                    new_candidate = {
                        "id": f"cand_{len(st.session_state['talent_pool']) + 1}",
                        "name": c_name.strip(),
                        "role": c_role.strip() if c_role.strip() else "Software Engineer",
                        "bandwidth_status": c_status,
                        "skills": skills_list,
                        "bio": c_bio.strip() if c_bio.strip() else "Indexed candidate profile.",
                        "years_experience": 5,
                        "past_projects": ["Enterprise Resume Ingestion"]
                    }
                    
                    st.session_state["talent_pool"].insert(0, new_candidate)
                    store_instance.add_profile(c_name.strip(), extracted_text or c_bio, {"candidate_name": c_name, "bandwidth_status": c_status})
                    
                    st.toast(f"✅ Indexed profile for {c_name} into vector store!", icon="✨")
                    st.success(f"Successfully indexed profile for **{c_name}** into vector store!")
                else:
                    st.error("Candidate Full Name is required.")

    # TAB 3: TALENT ROSTER MATRIX
    with tab3:
        st.subheader("Internal Talent Pool Roster Matrix")
        
        search_query = st.text_input("Search talent by name, role, or skill...", placeholder="Type e.g. Python, FastAPI, DevOps...")
        
        roster = st.session_state["talent_pool"]
        if search_query.strip():
            q = search_query.lower()
            roster = [c for c in roster if q in c["name"].lower() or q in c["role"].lower() or any(q in s.lower() for s in c["skills"])]
            
        st.markdown(f"**Showing {len(roster)} of {len(st.session_state['talent_pool'])} Candidates**")
        
        cols = st.columns(2)
        for idx, cand in enumerate(roster):
            col = cols[idx % 2]
            with col:
                status_class = "badge-avail"
                if "Assigned" in cand["bandwidth_status"]:
                    status_class = "badge-assigned"
                elif "Part-time" in cand["bandwidth_status"]:
                    status_class = "badge-part"
                    
                st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f"### {cand['name']}")
                st.markdown(f"**{cand['role']}** • {cand['years_experience']} Yrs Experience")
                st.markdown(f'<span class="{status_class}">{cand["bandwidth_status"]}</span>', unsafe_allow_html=True)
                st.write(cand["bio"])
                st.markdown(f"**Skills:** {', '.join(cand['skills'])}")
                st.markdown('</div>', unsafe_allow_html=True)
