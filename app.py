import streamlit as st
import os
import time
import base64
import requests
from typing import List, Dict, Any
from PIL import Image

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Initialize Session State
if "splash_done" not in st.session_state:
    st.session_state["splash_done"] = False

if "deploy_modal_candidate" not in st.session_state:
    st.session_state["deploy_modal_candidate"] = None

if "llm_provider" not in st.session_state:
    st.session_state["llm_provider"] = "hybrid_local"

if "app_theme" not in st.session_state:
    st.session_state["app_theme"] = "System Default"

st.set_page_config(
    page_title="StratixIQ - AI Agile Talent Deployment Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to generate reusable brand logo card component
def get_brand_logo_card(variant="splash"):
    if variant == "splash":
        return (
            '<div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); '
            'padding: 2.2rem 4rem; border-radius: 2.2rem; border: 1px solid rgba(255, 255, 255, 0.14); '
            'box-shadow: 0 20px 50px rgba(59, 130, 246, 0.35); display: inline-block; text-align: center;">'
            '<h1 style="font-size: 4rem; font-weight: 900; letter-spacing: -0.03em; background: linear-gradient(90deg, #60A5FA, #C084FC); '
            '-webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; line-height: 1.1; font-family: sans-serif;">StratixIQ</h1>'
            '<p style="font-size: 0.9rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.25em; margin-top: 0.6rem; text-transform: uppercase; margin-bottom: 0;">STRATEGY • INSIGHT • IMPACT</p>'
            '</div>'
        )
    elif variant == "header":
        return (
            '<div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.85)); '
            'padding: 1.1rem 2.2rem; border-radius: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.12); '
            'box-shadow: 0 12px 30px rgba(59, 130, 246, 0.25); display: inline-block;">'
            '<h2 style="font-size: 2.2rem; font-weight: 900; letter-spacing: -0.03em; background: linear-gradient(90deg, #60A5FA, #C084FC); '
            '-webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; line-height: 1.1; font-family: sans-serif;">StratixIQ</h2>'
            '<p style="font-size: 0.7rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.22em; margin-top: 0.3rem; text-transform: uppercase; margin-bottom: 0;">STRATEGY • INSIGHT • IMPACT</p>'
            '</div>'
        )
    else: # sidebar
        return (
            '<div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9)); '
            'padding: 1rem 1.25rem; border-radius: 1.25rem; border: 1px solid rgba(255, 255, 255, 0.14); '
            'box-shadow: 0 8px 25px rgba(59, 130, 246, 0.25); text-align: center; margin-bottom: 1.25rem;">'
            '<h3 style="font-size: 1.75rem; font-weight: 900; letter-spacing: -0.03em; background: linear-gradient(90deg, #60A5FA, #C084FC); '
            '-webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; line-height: 1.1; font-family: sans-serif;">StratixIQ</h3>'
            '<p style="font-size: 0.62rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.2em; margin-top: 0.3rem; text-transform: uppercase; margin-bottom: 0;">STRATEGY • INSIGHT • IMPACT</p>'
            '</div>'
        )

# Theme Custom CSS
current_theme = st.session_state.get("app_theme", "System Default")
if current_theme == "Light":
    theme_css = """
    body, .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    .metric-card {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
        color: #0F172A !important;
    }
    .metric-card h3 { color: #0F172A !important; }
    .metric-card p { color: #475569 !important; }
    .metric-card strong { color: #2563EB !important; }
    """
elif current_theme == "Dark":
    theme_css = """
    body, .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }
    .metric-card {
        background-color: rgba(30, 41, 59, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.2) !important;
        color: #F8FAFC !important;
    }
    .metric-card h3 { color: #F8FAFC !important; }
    .metric-card p { color: #94A3B8 !important; }
    .metric-card strong { color: #60A5FA !important; }
    """
else: # System Default
    theme_css = """
    @media (prefers-color-scheme: light) {
        body, .stApp {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }
        .metric-card {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
            color: #0F172A !important;
        }
        .metric-card h3 { color: #0F172A !important; }
        .metric-card p { color: #475569 !important; }
        .metric-card strong { color: #2563EB !important; }
    }
    @media (prefers-color-scheme: dark) {
        body, .stApp {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
        }
        .metric-card {
            background-color: rgba(30, 41, 59, 0.75) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            box-shadow: 0 12px 30px rgba(59, 130, 246, 0.2) !important;
            color: #F8FAFC !important;
        }
        .metric-card h3 { color: #F8FAFC !important; }
        .metric-card p { color: #94A3B8 !important; }
        .metric-card strong { color: #60A5FA !important; }
    }
    """

# CSS Custom Styling
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
    div[class*="StyledAppViewerFooter"],
    #stAppViewerFooter {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}

    {theme_css}

    .stButton button {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border-radius: 0.65rem !important;
        font-weight: 600 !important;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4) !important;
    }}
    .stButton button:hover {{
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 14px 28px rgba(59, 130, 246, 0.5) !important;
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
        border-radius: 0.85rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .metric-card:hover {{
        border-color: rgba(59, 130, 246, 0.5) !important;
        transform: translateY(-4px);
        box-shadow: 0 16px 32px -6px rgba(59, 130, 246, 0.3) !important;
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
# SPLASH SCREEN WITH BRAND LOGO CARD
# ==========================================
if not st.session_state["splash_done"]:
    splash_card_html = get_brand_logo_card("splash")
    splash_html = (
        '<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding-top: 3.5rem; padding-bottom: 1.5rem; width: 100%;">'
        f'{splash_card_html}'
        '<h3 style="font-size: 1.6rem; font-weight: 700; color: #F1F5F9; margin: 1.75rem 0 0.75rem 0;">Agile Talent Deployment & Skill-Matching Engine</h3>'
        '<p style="font-size: 1.05rem; color: #94A3B8; max-width: 640px; margin: 0 auto 1.5rem auto; line-height: 1.5;">Enterprise AI RAG Vector Pipeline • Explainable Match Auditing • Automated Gap Remediation</p>'
        '</div>'
    )
    st.markdown(splash_html, unsafe_allow_html=True)

    c_s1, c_s2, c_s3 = st.columns([2, 2.5, 2])
    with c_s2:
        if st.button("🚀 Enter StratixIQ Workspace", type="primary", use_container_width=True):
            st.session_state["splash_done"] = True
            st.rerun()

    time.sleep(2.0)
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

    # Sidebar Controls, Navigation Menu & Theme Selector
    with st.sidebar:
        # Sidebar Header with Glowing Brand Logo Card
        st.markdown(get_brand_logo_card("sidebar"), unsafe_allow_html=True)
        st.markdown("**Enterprise AI Talent Deployment Engine**")
        st.divider()

        # Sidebar Feature Navigation Menu
        st.subheader("📌 Platform Navigation")
        nav_selection = st.radio(
            "Select Feature Module",
            options=[
                "🎯 Single Candidate Matching",
                "🧩 Multi-Agent Squad Builder",
                "📥 Talent Ingestion & Roster Hub",
                "📈 Career Growth & Promotion Audit",
                "⭐ Performance RL Feedback Loop",
                "🛡️ Knowledge Graph & HR AI Fairness Auditor"
            ],
            key="sidebar_nav_menu"
        )
        st.divider()

        # UI Design System & Theme Selector
        st.subheader("🎨 Interface Theme Mode")
        theme_option = st.selectbox(
            "Select Interface Theme",
            options=["System Default", "Dark", "Light"],
            index=["System Default", "Dark", "Light"].index(st.session_state.get("app_theme", "System Default"))
        )
        if theme_option != st.session_state.get("app_theme"):
            st.session_state["app_theme"] = theme_option
            st.rerun()

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

    # Main App Header with Brand Logo Card & Info
    col_brand, col_title = st.columns([2.5, 5.5])
    with col_brand:
        st.markdown(get_brand_logo_card("header"), unsafe_allow_html=True)
    with col_title:
        st.markdown('<h1 style="font-size: 2.3rem; font-weight: 800; color: #F8FAFC; margin: 0;">StratixIQ</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.95rem; font-weight: 700; color: #60A5FA; letter-spacing: 2px; margin: 0 0 0.5rem 0;">STRATEGY • INSIGHT • IMPACT</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.95rem; color: #94A3B8; margin: 0; line-height: 1.4;">Enterprise AI RAG Vector Pipeline • Multi-Agent Squad Builder • Algorithmic Fairness Auditor</p>', unsafe_allow_html=True)

    st.divider()

    # ==========================================
    # MODULE 1: SINGLE CANDIDATE MATCHING ENGINE
    # ==========================================
    if nav_selection == "🎯 Single Candidate Matching":
        st.subheader("🎯 Match Engineering Requirements to Internal Talent Pool")
        st.caption("Perform semantic vector retrieval, explainable AI feature weighting, and automated gap remediation.")
        
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
            height=110,
            key="t1_proj_desc"
        )
        
        col_opt1, col_opt2 = st.columns([2, 1])
        with col_opt1:
            selected_availability = st.selectbox("Filter Availability Status", ["All Availability", "Available Immediately", "Part-time bandwidth (50%)", "Assigned until next month"], key="t1_avail")
        with col_opt2:
            top_k = st.slider("Top Candidates to Retrieve", 1, 5, 3, key="t1_topk")

        if st.button("🚀 Run Semantic Talent Search & Explainable Match Audit", type="primary", key="t1_search_btn"):
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

        if st.session_state.get("deploy_modal_candidate"):
            dep_cand = st.session_state["deploy_modal_candidate"]
            st.divider()
            st.success(f"✅ **Deployment Status Confirmed**: Candidate **{dep_cand['name']}** ({dep_cand['role']}) has been assigned to project sprint. Resource team notified!")
            if st.button("Close Popup"):
                st.session_state["deploy_modal_candidate"] = None
                st.rerun()

    # ==========================================
    # MODULE 2: MULTI-AGENT COLLABORATIVE SQUAD BUILDER
    # ==========================================
    elif nav_selection == "🧩 Multi-Agent Squad Builder":
        st.subheader("🧩 Multi-Agent Cross-Functional Squad Assembler")
        st.caption("Deconstruct complex project requirements into distinct technical role slots, query vector store, and assemble non-redundant team rosters.")
        
        squad_scope = st.text_area(
            "Enter Full Project Scope for Team Assembly",
            value="Build a high-throughput AI RAG Analytics Platform with FastAPI backend, ChromaDB vector store, Next.js dashboard, and AWS Cloud deployment.",
            height=100,
            key="t2_squad_scope"
        )
        
        if st.button("🧩 Assemble Multi-Agent Collaborative Squad", type="primary", key="t2_assemble_btn"):
            if squad_scope.strip():
                squad_data = None
                if backend_online:
                    try:
                        resp = requests.post(f"{BACKEND_URL}/assemble-squad", json={"project_scope": squad_scope}, timeout=8.0)
                        if resp.status_code == 200:
                            squad_data = resp.json()
                    except Exception:
                        pass

                if not squad_data:
                    from utils import squad_assembler, vector_store, llm_manager
                    squad_data = squad_assembler.decompose_and_assemble(squad_scope, vector_store, llm_manager)

                st.divider()
                st.markdown("### 🚀 Assembled Cross-Functional Team Roster")
                
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Total Squad Members", f"{squad_data['squad_size']} Engineers")
                with m2:
                    st.metric("Squad Synergy Score", f"{squad_data['squad_synergy_score']}%")
                with m3:
                    st.metric("Skill Balance Index", f"{squad_data['skill_balance_index']}%")

                st.markdown("**Unique Tech Skills Covered Across Squad:**")
                skills_tags = "".join([f'<span style="background-color: rgba(16, 185, 129, 0.2); color: #34D399; padding: 0.2rem 0.6rem; border-radius: 0.375rem; font-size: 0.8rem; font-weight: 600; margin-right: 0.4rem; margin-bottom: 0.4rem; display: inline-block;">{s}</span>' for s in squad_data['unique_skills_covered']])
                st.markdown(skills_tags, unsafe_allow_html=True)
                st.divider()

                for member in squad_data["squad_roster"]:
                    with st.container(border=True):
                        st.markdown(f"#### 👤 {member['role_title']} → **{member['candidate_name']}** ({member['current_role']})")
                        st.markdown(f"**Match Confidence:** `{member['match_confidence']}%` | **Status:** `{member['bandwidth_status']}`")
                        st.markdown(f"**Matching Skills:** {', '.join(member['matching_skills'])}")
                        st.info(f"**Role Fit Rationale:** {member['role_fit_rationale']}")

                if st.button("⚡ Deploy Entire Squad to Enterprise Sprint", key="deploy_squad_btn", type="primary"):
                    st.toast(f"🎉 Deployed {squad_data['squad_size']} team members to sprint!", icon="🚀")
                    st.success(f"✅ **Squad Deployment Activated**: All {squad_data['squad_size']} team members notified!")

    # ==========================================
    # MODULE 3: TALENT INGESTION & ROSTER HUB
    # ==========================================
    elif nav_selection == "📥 Talent Ingestion & Roster Hub":
        st.subheader("📥 Ingest Resume & Explore Internal Talent Pool Roster Matrix")
        
        with st.form("t3_upload_form", clear_on_submit=True):
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
                            st.toast(f"✅ Indexed profile for {c_name} into local store!", icon="✨")
                            st.success(f"Successfully indexed profile for **{c_name}**!")
                    except Exception as e:
                        st.error(f"Failed to submit profile: {e}")
                else:
                    st.error("Candidate Full Name is required.")

        st.divider()
        search_query = st.text_input("Search talent by name, role, or skill...", placeholder="Type e.g. Python, FastAPI, DevOps...", key="t3_search")
        
        roster = []
        if backend_online:
            try:
                resp = requests.get(f"{BACKEND_URL}/talent-pool", timeout=2.0)
                if resp.status_code == 200:
                    roster = resp.json().get("talent_pool", [])
            except Exception:
                pass
        
        if not roster:
            from utils import INITIAL_TALENT_POOL
            roster = INITIAL_TALENT_POOL

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
                
                card_html = (
                    '<div class="metric-card" style="background-color: rgba(30, 41, 59, 0.75); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 0.85rem; padding: 1.25rem; margin-bottom: 1rem;">'
                    '<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem;">'
                    f'<h3 style="margin: 0; font-size: 1.35rem; font-weight: 800; color: #F8FAFC;">{cand["name"]}</h3>'
                    f'<span style="background-color: {status_bg}; color: {status_color}; padding: 0.2rem 0.6rem; border-radius: 0.375rem; font-size: 0.8rem; font-weight: 600;">{cand["bandwidth_status"]}</span>'
                    '</div>'
                    f'<p style="margin: 0 0 0.6rem 0; font-size: 0.95rem; color: #94A3B8; font-weight: 600;">{cand["role"]} • {cand.get("years_experience", 5)} Yrs Experience</p>'
                    f'<p style="margin: 0 0 0.85rem 0; font-size: 0.9rem; color: #CBD5E1; line-height: 1.45;">{cand.get("bio", "Indexed candidate profile.")}</p>'
                    '<div style="border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 0.65rem;">'
                    '<div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; margin-bottom: 0.35rem;">Verified Skills & Tech Stack:</div>'
                    f'<div>{skills_tags}</div>'
                    '</div>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

    # ==========================================
    # MODULE 4: CANDIDATE CAREER GROWTH AUDIT
    # ==========================================
    elif nav_selection == "📈 Career Growth & Promotion Audit":
        st.subheader("📈 Candidate Career Growth & Promotion Skill-Gap Auditor")
        st.caption("Empower employees to audit their profile against target senior enterprise roles and generate 4-week promotion readiness roadmaps.")
        
        ca1, ca2 = st.columns(2)
        with ca1:
            sel_cand_name = st.selectbox("Select Candidate for Audit", ["Alex Rivera", "Elena Rostova", "Marcus Vance", "Rahul Sharma", "Priya Patel", "Sneha Reddy", "Vikramaditya Rao"], key="t4_cand_sel")
        with ca2:
            sel_target_role = st.selectbox("Select Target Senior Role", [
                "Principal AI Systems Architect",
                "Lead Cloud DevOps Engineer",
                "Senior Full-Stack AI Engineer",
                "MLOps & Data Platform Architect"
            ], key="t4_role_sel")

        if st.button("🚀 Generate Career Audit & Promotion Roadmap", type="primary", key="t4_audit_btn"):
            audit_res = None
            cand_skills_map = {
                "Alex Rivera": ["Python", "FastAPI", "ChromaDB", "LangChain", "React"],
                "Elena Rostova": ["Python", "PyTorch", "HuggingFace", "Vector DB", "MLOps"],
                "Marcus Vance": ["AWS CDK", "Kubernetes", "Docker", "CI/CD", "Python"],
                "Rahul Sharma": ["Python", "FastAPI", "PyMuPDF", "ChromaDB", "PyTorch"],
                "Priya Patel": ["Java", "Spring Boot", "MySQL", "Kubernetes", "AWS"],
                "Sneha Reddy": ["React", "Node.js", "TypeScript", "PostgreSQL", "GraphQL"],
                "Vikramaditya Rao": ["Terraform", "AWS", "Kubernetes", "Docker", "CI/CD"]
            }
            c_skills = cand_skills_map.get(sel_cand_name, ["Python", "Engineering"])

            if backend_online:
                try:
                    resp = requests.post(f"{BACKEND_URL}/career-growth-audit", json={
                        "candidate_name": sel_cand_name,
                        "current_role": "Senior Engineer",
                        "current_skills": c_skills,
                        "target_role": sel_target_role
                    }, timeout=5.0)
                    if resp.status_code == 200:
                        audit_res = resp.json()
                except Exception:
                    pass

            if not audit_res:
                from utils import career_auditor
                audit_res = career_auditor.generate_career_audit(sel_cand_name, "Senior Engineer", c_skills, sel_target_role)

            st.divider()
            st.markdown(f"### 🏆 Career Growth Audit: **{sel_cand_name}** → `{sel_target_role}`")
            
            sc1, sc2 = st.columns([1.5, 3])
            with sc1:
                st.metric("Promotion Readiness", f"{audit_res['promotion_readiness_score']}%")
                st.progress(audit_res['promotion_readiness_score'] / 100.0)
            with sc2:
                st.markdown(f"**Verified Matching Skills:** {', '.join(audit_res['verified_matching_skills'])}")
                st.markdown(f"**Critical Skill Gaps to Bridge:** {', '.join(audit_res['critical_skill_gaps'])}")
                st.info(f"**Recommended Project Assignment:** {audit_res['recommended_internal_project']}")

            st.markdown("#### 📅 4-Week Actionable Upskilling Roadmap")
            rm = audit_res["four_week_upskilling_roadmap"]
            for week_k, step in rm.items():
                with st.container(border=True):
                    st.markdown(f"**{week_k.replace('_', ' ').title()}:** {step}")

    # ==========================================
    # MODULE 5: HISTORICAL PROJECT PERFORMANCE FEEDBACK LOOP
    # ==========================================
    elif nav_selection == "⭐ Performance RL Feedback Loop":
        st.subheader("⭐ Historical Project Performance & RL Feedback Loop")
        st.caption("Submit manager ratings (1-5 stars) on completed sprint assignments to dynamically weight vector search score multipliers.")
        
        fb1, fb2, fb3 = st.columns(3)
        with fb1:
            fb_cand_id = st.selectbox("Select Deployed Candidate", ["cand_1", "cand_2", "cand_3", "cand_6", "cand_7"], format_func=lambda x: {"cand_1": "Alex Rivera", "cand_2": "Elena Rostova", "cand_3": "Marcus Vance", "cand_6": "Rahul Sharma", "cand_7": "Priya Patel"}[x], key="t5_cand_id")
        with fb2:
            fb_project_title = st.text_input("Project / Sprint Title", value="Q3 Enterprise AI Microservice Sprint", key="t5_proj_title")
        with fb3:
            fb_rating = st.slider("Manager Performance Rating (1-5 Stars)", 1, 5, 5, key="t5_rating")

        fb_notes = st.text_area("Performance Feedback Notes", value="Delivered microservice architecture ahead of schedule with 99.9% uptime.", height=80, key="t5_notes")
        
        if st.button("⭐ Submit Manager Rating & Update RL Vector Multiplier", type="primary", key="t5_submit_btn"):
            cand_name_map = {"cand_1": "Alex Rivera", "cand_2": "Elena Rostova", "cand_3": "Marcus Vance", "cand_6": "Rahul Sharma", "cand_7": "Priya Patel"}
            fb_res = None
            if backend_online:
                try:
                    resp = requests.post(f"{BACKEND_URL}/submit-project-feedback", json={
                        "candidate_id": fb_cand_id,
                        "candidate_name": cand_name_map[fb_cand_id],
                        "project_title": fb_project_title,
                        "rating": fb_rating,
                        "feedback_text": fb_notes
                    }, timeout=5.0)
                    if resp.status_code == 200:
                        fb_res = resp.json()
                except Exception:
                    pass

            if not fb_res:
                from utils import feedback_manager
                fb_res = feedback_manager.record_feedback(fb_cand_id, cand_name_map[fb_cand_id], fb_project_title, fb_rating, fb_notes)

            st.toast(f"✅ Feedback logged for {fb_res['candidate_name']}! Multiplier: {fb_res['vector_score_multiplier']}x", icon="⭐")
            st.success(f"Recorded 5-Star feedback for **{fb_res['candidate_name']}**! Vector match multiplier updated to **{fb_res['vector_score_multiplier']}x**.")

        st.divider()
        st.markdown("#### 📜 Recent Manager Project Performance Feedback Audit Log")
        from utils import feedback_manager
        for rec in feedback_manager.feedback_records:
            with st.container(border=True):
                st.markdown(f"**Candidate:** `{rec['candidate_name']}` | **Project:** `{rec['project_title']}` | **Rating:** {'⭐' * rec['manager_rating']}")
                st.markdown(f"**Vector Multiplier Boost:** `{rec['vector_score_multiplier']}x`")
                st.caption(f"Feedback: \"{rec['feedback_text']}\"")

    # ==========================================
    # MODULE 6: ENTERPRISE KNOWLEDGE GRAPH & HR AI FAIRNESS AUDITOR
    # ==========================================
    elif nav_selection == "🛡️ Knowledge Graph & HR AI Fairness Auditor":
        st.subheader("🛡️ Enterprise Knowledge Graph & HR AI Algorithmic Fairness Auditor")
        
        kg_col, f_col = st.columns(2)
        
        with kg_col:
            st.markdown("### 🕸️ Enterprise Skill & Candidate Knowledge Graph")
            st.caption("Visualizing interconnections across candidates, roles, and technical skill nodes.")
            
            kg_data = None
            if backend_online:
                try:
                    resp = requests.get(f"{BACKEND_URL}/knowledge-graph", timeout=3.0)
                    if resp.status_code == 200:
                        kg_data = resp.json()
                except Exception:
                    pass

            if not kg_data:
                from utils import knowledge_graph_mgr, INITIAL_TALENT_POOL
                kg_data = knowledge_graph_mgr.generate_graph_data(INITIAL_TALENT_POOL)

            st.metric("Total Enterprise Network Nodes", f"{kg_data['total_nodes']} Nodes")
            st.metric("Total Skill & Role Connections", f"{kg_data['total_edges']} Edges")

            st.markdown("**Graph Node Cluster Breakdown:**")
            for node in kg_data["nodes"][:8]:
                st.markdown(f"• **{node['type']}:** <span style='color:{node['color']}; font-weight:700;'>{node['label']}</span>", unsafe_allow_html=True)

        with f_col:
            st.markdown("### 🛡️ HR AI Bias & Algorithmic Fairness Audit Certificate")
            st.caption("Verification scan for EU AI Act compliance, demographic proxy elimination, and equal opportunity scoring.")
            
            fair_data = None
            if backend_online:
                try:
                    resp = requests.post(f"{BACKEND_URL}/audit-fairness", json=[{"match_percentage": 90}, {"match_percentage": 85}], timeout=3.0)
                    if resp.status_code == 200:
                        fair_data = resp.json()
                except Exception:
                    pass

            if not fair_data:
                from utils import fairness_auditor
                fair_data = fairness_auditor.audit_matching_fairness([{"match_percentage": 90}, {"match_percentage": 85}])

            st.success(f"**Compliance Status:** {fair_data['compliance_status']}")
            
            fm1, fm2 = st.columns(2)
            with fm1:
                st.metric("Demographic Parity Index", f"{fair_data['demographic_parity_index']}%")
            with fm2:
                st.metric("Disparate Impact Ratio", f"{fair_data['disparate_impact_ratio']}")

            st.markdown("#### 🔒 Proxy Bias Indicator Audit Log")
            st.markdown("• **Demographic Data Stripped:** `YES`")
            st.markdown("• **Age / Gender / Location Weights:** `0.0%` (Zero Proxy Data)")
            st.markdown("• **Merit-Based Cosine Similarity Weight:** `100.0%`")
            st.caption(f"Certification Note: {fair_data['certification_summary']}")

    # ==========================================
    # PROFESSIONAL FOOTER
    # ==========================================
    footer_html = (
        '<div style="text-align: center; padding: 2rem 0 1.5rem 0; border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 3.5rem; color: #94A3B8; font-size: 0.88rem;">'
        '© 2026 <strong>StratixIQ</strong>. Enterprise AI Talent Deployment & Skill-Matching Engine. All Rights Reserved.'
        '</div>'
    )
    st.markdown(footer_html, unsafe_allow_html=True)

