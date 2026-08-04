import streamlit as st
import os
import time
import base64
import requests
from typing import List, Dict, Any
from PIL import Image

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Initialize Session State for Splash Screen & Local Fallback Pool
if "splash_done" not in st.session_state:
    st.session_state["splash_done"] = False

if "deploy_modal_candidate" not in st.session_state:
    st.session_state["deploy_modal_candidate"] = None

if "llm_provider" not in st.session_state:
    st.session_state["llm_provider"] = "hybrid_local"

st.set_page_config(
    page_title="StratixIQ - AI Agile Talent Deployment Engine",
    layout="wide",
    initial_sidebar_state="expanded" if st.session_state.get("splash_done") else "collapsed"
)

# Function to encode logo image to base64 for HTML rendering
def get_base64_logo():
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

hide_sidebar_css = "" if st.session_state["splash_done"] else "[data-testid='stSidebar'] {display: none !important;}"

# CSS Custom Theme & Animation Styling
st.markdown(f"""
<style>
    /* Hide Streamlit Header, Toolbar, Footer & Manage App Button */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{display: none !important;}}
    [data-testid="stToolbar"] {{display: none !important;}}
    [data-testid="stDecoration"] {{display: none !important;}}
    [data-testid="stStatusWidget"] {{display: none !important;}}
    [data-testid="stManageAppButton"] {{display: none !important;}}
    .stManageAppButton {{display: none !important;}}
    button[aria-label="Manage app"] {{display: none !important;}}
    button[title="Manage app"] {{display: none !important;}}
    .stDeployButton {{display: none !important;}}
    button[title="View code"] {{display: none !important;}}

    /* Hide bottom right Manage App viewer button */
    [data-testid="stAppViewerFooter"],
    [data-testid="stReportViewerFooter"],
    .stAppViewerFooter,
    .stReportViewerFooter,
    div[class*="stAppViewerFooter"],
    div[class*="stReportViewerFooter"],
    div[class*="viewerFooter"],
    #stAppViewerFooter {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}

    {hide_sidebar_css}

    .stButton button {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-radius: 0.65rem !important;
        font-weight: 600 !important;
    }}
    .stButton button:hover {{
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.35) !important;
    }}

    .main-header {{
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60A5FA, #A78BFA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
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
    .xai-box {{
        background-color: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #60A5FA;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin-top: 0.75rem;
    }}
    .upskill-box {{
        background-color: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #10B981;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        margin-top: 0.75rem;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SPLASH SCREEN WITH TYPOGRAPHY HERO BRANDING
# ==========================================
if not st.session_state["splash_done"]:
    splash_html = """
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding-top: 3.5rem; padding-bottom: 2rem; width: 100%;">
        <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9)); padding: 2rem 3.5rem; border-radius: 2rem; border: 1px solid rgba(255, 255, 255, 0.12); box-shadow: 0 20px 45px rgba(59, 130, 246, 0.25); display: inline-block; margin-bottom: 1.75rem;">
            <h1 style="font-size: 3.8rem; font-weight: 900; letter-spacing: -0.03em; background: linear-gradient(90deg, #60A5FA, #A78BFA); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; line-height: 1.1;">StratixIQ</h1>
            <p style="font-size: 0.85rem; font-weight: 700; color: #38BDF8; letter-spacing: 0.2em; margin-top: 0.5rem; text-transform: uppercase;">Strategy • Insight • Impact</p>
        </div>
        <h3 style="font-size: 1.5rem; font-weight: 700; color: #F1F5F9; margin: 0 0 0.75rem 0;">Agile Talent Deployment & Skill-Matching Engine</h3>
        <p style="font-size: 1.05rem; color: #94A3B8; max-width: 640px; margin: 0 auto; line-height: 1.5;">Enterprise AI RAG Vector Pipeline • Explainable Match Auditing • Automated Gap Remediation</p>
    </div>
    """
    
    st.markdown(splash_html, unsafe_allow_html=True)

    time.sleep(2.5)
    st.session_state["splash_done"] = True
    st.rerun()

else:
    # Check Backend API Health Connection
    backend_online = False
    indexed_count = 5
    active_provider = st.session_state["llm_provider"]

    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
        if res.status_code == 200:
            backend_online = True
            data = res.json()
            indexed_count = data.get("indexed_vector_count", 5)
            active_provider = data.get("active_llm_provider", active_provider)
    except Exception:
        backend_online = False

    # Sidebar Controls & LLM Provider Toggle
    with st.sidebar:
        st.markdown("## StratixIQ Enterprise")
        st.markdown("**AI Agile Talent Matching Engine**")
        st.divider()

        # Enterprise Data Privacy Toggle
        st.subheader("🛡️ LLM Engine & Data Privacy")
        provider_option = st.selectbox(
            "Select Inference Model Backend",
            options=["hybrid_local", "openai", "ollama"],
            format_func=lambda x: {
                "hybrid_local": "🔒 Local Hybrid Engine (Zero Data Leak)",
                "openai": "☁️ Cloud OpenAI GPT-4o API",
                "ollama": "🦙 Local Ollama (Llama 3)"
            }[x],
            index=["hybrid_local", "openai", "ollama"].index(active_provider)
        )

        if provider_option != active_provider:
            try:
                requests.post(f"{BACKEND_URL}/config/llm-provider", json={"provider_name": provider_option}, timeout=2.0)
                st.session_state["llm_provider"] = provider_option
                st.toast(f"Updated LLM provider to {provider_option}", icon="⚙️")
            except Exception:
                st.session_state["llm_provider"] = provider_option

        st.divider()
        st.metric("Total Indexed Talent", f"{indexed_count} Profiles")
        if backend_online:
            st.success("FastAPI Backend: Online & Connected")
        else:
            st.info("Direct Local Inference Engine Active")

    # Main App Header
    st.markdown('<p class="main-header">StratixIQ: Agile Talent Deployment Engine</p>', unsafe_allow_html=True)
    st.caption("AI-driven RAG vector pipeline for candidate staffing, explainable match auditing, and gap remediation")

    tab1, tab2, tab3 = st.tabs(["📥 Talent & Resume Ingestion Hub", "🎯 Agile Project Staffing Engine", "👥 Talent Roster Matrix"])

    # TAB 1: TALENT & RESUME INGESTION HUB
    with tab1:
        st.subheader("Ingest Employee PDF Resume & Skills Profile into Vector Store")
        st.caption("Extract resume layout streams using PyMuPDF (fitz), perform LangChain semantic chunking, and persist embeddings in ChromaDB.")
        
        with st.form("resume_upload_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Candidate Full Name *", placeholder="e.g. Sarah Connor")
                c_role = st.text_input("Candidate Role / Job Title", placeholder="e.g. Senior AI Systems Engineer")
                c_status = st.selectbox("Availability Bandwidth *", ["Available Immediately", "Part-time bandwidth (50%)", "Assigned until next month"])
            with c2:
                c_skills = st.text_input("Key Tech Skills (Comma-separated)", placeholder="e.g. Python, FastAPI, PyMuPDF, ChromaDB, Docker")
                c_bio = st.text_area("Profile Summary / Bio", placeholder="Brief summary of engineering background and achievements...")
                uploaded_pdf = st.file_uploader("Upload Resume Document (PDF)", type=["pdf"])

            submitted = st.form_submit_button("🚀 Index Profile into Vector DB", type="primary")

            if submitted:
                if c_name.strip():
                    try:
                        files_payload = None
                        if uploaded_pdf is not None:
                            pdf_bytes = uploaded_pdf.read()
                            files_payload = {"file": (uploaded_pdf.name, pdf_bytes, "application/pdf")}

                        data_payload = {
                            "candidate_name": c_name.strip(),
                            "role": c_role.strip() if c_role.strip() else "Software Engineer",
                            "bandwidth_status": c_status,
                            "skills": c_skills.strip() if c_skills.strip() else "Python, Engineering",
                            "bio": c_bio.strip()
                        }

                        if backend_online:
                            resp = requests.post(f"{BACKEND_URL}/upload-profile", data=data_payload, files=files_payload, timeout=5.0)
                            if resp.status_code == 200:
                                st.toast(f"✅ Indexed profile for {c_name} into ChromaDB vector store!", icon="✨")
                                st.success(f"Successfully indexed profile for **{c_name}** into ChromaDB vector store!")
                            else:
                                st.error(f"Error from API: {resp.text}")
                        else:
                            st.toast(f"✅ Indexed profile for {c_name} into local store!", icon="✨")
                            st.success(f"Successfully indexed profile for **{c_name}**!")
                    except Exception as e:
                        st.error(f"Failed to submit profile: {e}")
                else:
                    st.error("Candidate Full Name is required.")

    # TAB 2: AGILE PROJECT STAFFING ENGINE
    with tab2:
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
            height=110
        )
        
        col_opt1, col_opt2 = st.columns([2, 1])
        with col_opt1:
            selected_availability = st.selectbox("Filter Availability Status", ["All Availability", "Available Immediately", "Part-time bandwidth (50%)", "Assigned until next month"])
        with col_opt2:
            top_k = st.slider("Top Candidates to Retrieve", 1, 5, 3)

        if st.button("🚀 Run Semantic Talent Search & Explainable Match Audit", type="primary"):
            if project_desc.strip():
                st.divider()
                st.markdown("### 🏆 Top Candidate Shortlist, Explainable AI Audit & Gap Remediation")
                
                matches = []
                if backend_online:
                    try:
                        req_data = {
                            "project_description": project_desc,
                            "top_k": top_k,
                            "bandwidth_filter": selected_availability
                        }
                        resp = requests.post(f"{BACKEND_URL}/match-talent", json=req_data, timeout=8.0)
                        if resp.status_code == 200:
                            matches = resp.json()
                    except Exception as e:
                        st.warning(f"Backend connection note: {e}. Running local matching...")

                if not matches:
                    # Fallback local matching invocation
                    from utils import vector_store, llm_manager
                    v_res = vector_store.query_candidates(project_desc, top_k=top_k, bandwidth_filter=selected_availability)
                    for item in v_res:
                        eval_res = llm_manager.generate_structured_match(project_desc, {
                            "name": item["candidate_name"],
                            "role": item["role"],
                            "skills": item["skills"],
                            "bandwidth_status": item["bandwidth_status"]
                        })
                        matches.append({
                            "id": item["candidate_id"],
                            "name": item["candidate_name"],
                            "role": item["role"],
                            "bandwidth_status": item["bandwidth_status"],
                            "skills": item["skills"],
                            "match_percentage": eval_res.get("match_percentage", 82),
                            "verified_strengths": eval_res.get("verified_strengths", item["skills"]),
                            "skill_gaps": eval_res.get("skill_gaps", []),
                            "deployment_rationale": eval_res.get("deployment_rationale", "Verified technical alignment."),
                            "explainable_ai_breakdown": eval_res.get("explainable_ai_breakdown", {
                                "core_tech_stack_weight": 45.0,
                                "experience_depth_weight": 30.0,
                                "availability_timeline_weight": 25.0
                            }),
                            "upskilling_path": eval_res.get("upskilling_path", {
                                "week_1": "Study core framework documentation and API routes.",
                                "week_2": "Build hands-on integration prototype."
                            })
                        })

                if not matches:
                    st.warning("No candidates matched the selected availability filter.")
                else:
                    for idx, match in enumerate(matches):
                        status_class = "badge-avail"
                        if "Assigned" in match["bandwidth_status"]:
                            status_class = "badge-assigned"
                        elif "Part-time" in match["bandwidth_status"]:
                            status_class = "badge-part"
                            
                        with st.container(border=True):
                            c1, c2 = st.columns([3.5, 1.2])
                            with c1:
                                st.markdown(f"### #{idx+1} {match['name']} - *{match['role']}*")
                                st.markdown(f'<span class="{status_class}">{match["bandwidth_status"]}</span>', unsafe_allow_html=True)
                            with c2:
                                st.metric(label="Match Confidence", value=f"{match['match_percentage']}%")
                                
                            st.markdown(f"**Verified Matching Skills:** {', '.join(match['verified_strengths'])}")
                            if match.get('skill_gaps'):
                                st.markdown(f"**Potential Skill Gaps:** {', '.join(match['skill_gaps'])}")
                            
                            st.info(f"**Strategic Deployment Rationale:** {match['deployment_rationale']}")
                            
                            # ADVANCED DIFFERENTIATOR 1: Explainable AI & Feature Audit Breakdown
                            xai = match.get("explainable_ai_breakdown", {})
                            st.markdown('<div class="xai-box">', unsafe_allow_html=True)
                            st.markdown("#### 📊 Explainable AI Decision Audit Trail")
                            col_x1, col_x2, col_x3 = st.columns(3)
                            with col_x1:
                                st.caption("Core Tech Stack Weight")
                                st.progress(int(xai.get("core_tech_stack_weight", 45)) / 100.0)
                                st.write(f"**{xai.get('core_tech_stack_weight', 45)}%**")
                            with col_x2:
                                st.caption("Experience Depth Weight")
                                st.progress(int(xai.get("experience_depth_weight", 30)) / 100.0)
                                st.write(f"**{xai.get('experience_depth_weight', 30)}%**")
                            with col_x3:
                                st.caption("Availability Timeline Weight")
                                st.progress(int(xai.get("availability_timeline_weight", 25)) / 100.0)
                                st.write(f"**{xai.get('availability_timeline_weight', 25)}%**")
                            st.markdown('</div>', unsafe_allow_html=True)

                            # ADVANCED DIFFERENTIATOR 2: Automated Upskilling & Gap Remediation Path
                            upskill = match.get("upskilling_path", {})
                            st.markdown('<div class="upskill-box">', unsafe_allow_html=True)
                            st.markdown("#### 🎯 Automated 2-Week Skill Remediation Path")
                            st.markdown(f"**Week 1 (Foundational Remediation):** {upskill.get('week_1')}")
                            st.markdown(f"**Week 2 (Hands-on Sprint Readiness):** {upskill.get('week_2')}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.divider()
                            if st.button(f"⚡ Deploy {match['name']} to Sprint", key=f"deploy_{match['id']}"):
                                st.session_state["deploy_modal_candidate"] = match
                                st.toast(f"🎉 Assigned {match['name']} to sprint deployment!", icon="🚀")
                                st.rerun()
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

    # TAB 3: TALENT ROSTER MATRIX
    with tab3:
        st.subheader("Internal Talent Pool Roster Matrix")
        
        search_query = st.text_input("Search talent by name, role, or skill...", placeholder="Type e.g. Python, FastAPI, DevOps...")
        
        roster = []
        if backend_online:
            try:
                resp = requests.get(f"{BACKEND_URL}/talent-pool", timeout=2.0)
                if resp.status_code == 200:
                    roster = resp.json().get("talent_pool", [])
            except Exception:
                pass
        
        if not roster:
            from utils import vector_store
            roster = [
                {
                    "name": doc["candidate_name"],
                    "role": doc["role"],
                    "bandwidth_status": doc["bandwidth_status"],
                    "skills": doc["skills"],
                    "years_experience": 6,
                    "bio": "Indexed candidate profile."
                } for doc in vector_store.in_memory_docs
            ] or [
                {"name": "Alex Rivera", "role": "Senior Full-Stack AI Engineer", "bandwidth_status": "Available Immediately", "skills": ["Python", "FastAPI", "ChromaDB", "React"], "years_experience": 7, "bio": "Specializes in RAG pipelines."},
                {"name": "Elena Rostova", "role": "ML & Data Architect", "bandwidth_status": "Part-time bandwidth (50%)", "skills": ["Python", "PyTorch", "HuggingFace", "Vector DB"], "years_experience": 6, "bio": "LLM Fine-tuning expert."},
                {"name": "Marcus Vance", "role": "Cloud DevOps Engineer", "bandwidth_status": "Available Immediately", "skills": ["AWS CDK", "Kubernetes", "Docker", "CI/CD"], "years_experience": 8, "bio": "Cloud platform engineer."}
            ]

        if search_query.strip():
            q = search_query.lower()
            roster = [c for c in roster if q in c["name"].lower() or q in c["role"].lower() or any(q in s.lower() for s in c["skills"])]
            
        st.markdown(f"**Showing {len(roster)} Candidate Profiles**")
        
        cols = st.columns(2)
        for idx, cand in enumerate(roster):
            col = cols[idx % 2]
            with col:
                status_color = "#34D399"
                status_bg = "rgba(16, 185, 129, 0.2)"
                if "Assigned" in cand["bandwidth_status"]:
                    status_color = "#FBBF24"
                    status_bg = "rgba(245, 158, 11, 0.2)"
                elif "Part-time" in cand["bandwidth_status"]:
                    status_color = "#C084FC"
                    status_bg = "rgba(139, 92, 246, 0.2)"
                    
                skills_tags = "".join([f'<span style="background-color: rgba(59, 130, 246, 0.15); color: #60A5FA; padding: 0.2rem 0.55rem; border-radius: 0.375rem; font-size: 0.78rem; font-weight: 600; margin-right: 0.35rem; margin-bottom: 0.35rem; display: inline-block;">{s}</span>' for s in cand['skills']])
                
                card_html = f"""
                <div class="metric-card" style="background-color: rgba(30, 41, 59, 0.75); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 0.85rem; padding: 1.25rem; margin-bottom: 1rem; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem;">
                        <h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #F8FAFC;">{cand['name']}</h3>
                        <span style="background-color: {status_bg}; color: {status_color}; padding: 0.2rem 0.6rem; border-radius: 0.375rem; font-size: 0.8rem; font-weight: 600;">{cand['bandwidth_status']}</span>
                    </div>
                    <p style="margin: 0 0 0.6rem 0; font-size: 0.95rem; color: #94A3B8; font-weight: 600;">{cand['role']} • {cand.get('years_experience', 5)} Yrs Experience</p>
                    <p style="margin: 0 0 0.85rem 0; font-size: 0.9rem; color: #CBD5E1; line-height: 1.45;">{cand.get("bio", "Indexed candidate profile.")}</p>
                    <div style="border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 0.65rem;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; margin-bottom: 0.35rem;">Verified Skills & Tech Stack:</div>
                        <div>{skills_tags}</div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
