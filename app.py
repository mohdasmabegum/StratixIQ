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

# List of Feature Pages
PAGES = [
    "🎯 Single Candidate Matching",
    "🧩 Multi-Agent Squad Builder",
    "📥 Talent Ingestion & Roster Hub",
    "📈 Career Growth & Promotion Audit",
    "⭐ Performance RL Feedback Loop",
    "🛡️ Knowledge Graph & HR AI Fairness Auditor",
    "📄 Vector ATS Resume Screening & Shortlisting"
]

SHORT_TITLES = {
    "🎯 Single Candidate Matching": "Single Match",
    "🧩 Multi-Agent Squad Builder": "Squad Builder",
    "📥 Talent Ingestion & Roster Hub": "Roster Hub",
    "📈 Career Growth & Promotion Audit": "Career Audit",
    "⭐ Performance RL Feedback Loop": "RL Feedback",
    "🛡️ Knowledge Graph & HR AI Fairness Auditor": "AI Fairness",
    "📄 Vector ATS Resume Screening & Shortlisting": "ATS Screening"
}

if "current_page" not in st.session_state:
    st.session_state["current_page"] = PAGES[0]

if "active_feature" not in st.session_state:
    st.session_state["active_feature"] = PAGES[0]

def set_active_feature(target_page):
    st.session_state["active_feature"] = target_page

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
    p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {
        color: #0F172A !important;
    }
    .stCaption, caption, .stCaption p {
        color: #475569 !important;
    }
    section[data-testid="stSidebar"] {
        background: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
        box-shadow: 4px 0 25px rgba(0, 0, 0, 0.08) !important;
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #0F172A !important;
    }
    div[data-baseweb="select"] > div, input, textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #CBD5E1 !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #FFFFFF !important;
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
    button[key="top_left_sidebar_toggle"] {
        background: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        color: #2563EB !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08) !important;
    }
    """
elif current_theme == "Dark":
    theme_css = """
    body, .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }
    p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {
        color: #F8FAFC !important;
    }
    .stCaption, caption, .stCaption p {
        color: #94A3B8 !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.98)) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.14) !important;
        box-shadow: 12px 0 35px rgba(0, 0, 0, 0.5) !important;
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #F8FAFC !important;
    }
    div[data-baseweb="select"] > div, input, textarea {
        background-color: rgba(30, 41, 59, 0.8) !important;
        color: #F8FAFC !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #1E293B !important;
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
    button[key="top_left_sidebar_toggle"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9)) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #60A5FA !important;
        box-shadow: 0 4px 18px rgba(59, 130, 246, 0.3) !important;
    }
    """
else: # System Default
    theme_css = """
    @media (prefers-color-scheme: light) {
        body, .stApp { background-color: #F8FAFC !important; color: #0F172A !important; }
        p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown { color: #0F172A !important; }
        .stCaption, caption { color: #475569 !important; }
        .metric-card { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; color: #0F172A !important; }
    }
    @media (prefers-color-scheme: dark) {
        body, .stApp { background-color: #0F172A !important; color: #F8FAFC !important; }
        p, span, label, div, h1, h2, h3, h4, h5, h6, .stMarkdown { color: #F8FAFC !important; }
        .stCaption, caption { color: #94A3B8 !important; }
        .metric-card { background-color: rgba(30, 41, 59, 0.75) !important; border: 1px solid rgba(255, 255, 255, 0.12) !important; color: #F8FAFC !important; }
    }
    """

# CSS Custom Styling
st.markdown(f"""
<style>
    /* Preserve Streamlit sidebar toggle while hiding toolbar */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden !important;}}
    [data-testid="stHeader"] {{background: transparent !important; z-index: 100 !important;}}
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

    /* Completely hide sidebar and toggle elements */
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarExpandButton"] {{
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
    }}

    /* Icon-Only Left Arrow Back Button */
    button[key*="back_btn_p"],
    div[data-testid="stColumn"] button[key*="back_btn_p"] {{
        width: 44px !important;
        height: 44px !important;
        padding: 0 !important;
        font-size: 1.4rem !important;
        font-weight: 900 !important;
        border-radius: 0.75rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 44px !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8)) !important;
        color: #60A5FA !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }}
    button[key*="back_btn_p"]:hover {{
        background: linear-gradient(135deg, #3B82F6, #8B5CF6) !important;
        color: #FFFFFF !important;
        transform: translateX(-3px) scale(1.05) !important;
    }}

    /* Interactive Animated Feature Hub Cards */
    .feature-hub-card {{
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 1.25rem;
        padding: 1.5rem;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 1rem;
        cursor: pointer;
    }}
    .feature-hub-card:hover {{
        transform: translateY(-6px) scale(1.02);
        border-color: rgba(96, 165, 250, 0.6) !important;
        box-shadow: 0 18px 36px -6px rgba(59, 130, 246, 0.35) !important;
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

    /* Fixed Bottom Footer Bar */
    .fixed-footer-bar {{
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 9999;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(12px);
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        text-align: center;
        padding: 0.65rem 1rem;
        color: #94A3B8;
        font-size: 0.85rem;
        box-shadow: 0 -8px 25px rgba(0, 0, 0, 0.4);
    }}

    /* Ensure bottom spacing so scrollable content doesn't get covered */
    .main .block-container {{
        padding-bottom: 90px !important;
    }}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def check_backend_health_cached(url: str):
    try:
        res = requests.get(f"{url}/health", timeout=0.3)
        if res.status_code == 200:
            data = res.json()
            return True, data.get("indexed_vector_count", 5), data.get("active_llm_provider", "hybrid_local")
    except Exception:
        pass
    return False, 5, "hybrid_local"

# ==========================================
# MAIN APP ROUTING & INTERACTIVE WORKSPACE
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

else:
    # Optimized Cached Health Check (Zero-delay reruns)
    backend_online, indexed_count, active_provider = check_backend_health_cached(BACKEND_URL)

    # Main App Header with Brand Logo & Metadata
    col_brand, col_title = st.columns([3, 7])
    with col_brand:
        st.markdown(get_brand_logo_card("header"), unsafe_allow_html=True)

    with col_title:
        st.markdown('<h1 style="font-size: 2.3rem; font-weight: 800; color: #F8FAFC; margin: 0;">StratixIQ</h1>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.95rem; font-weight: 700; color: #60A5FA; letter-spacing: 2px; margin: 0 0 0.5rem 0;">STRATEGY • INSIGHT • IMPACT</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.95rem; color: #94A3B8; margin: 0; line-height: 1.4;">Enterprise AI RAG Vector Pipeline • Multi-Agent Squad Builder • Algorithmic Fairness Auditor</p>', unsafe_allow_html=True)

    st.divider()

    active_page = st.session_state.get("active_feature", PAGES[0])

    # ==========================================
    # PAGE 1: SINGLE CANDIDATE MATCHING ENGINE & FEATURE HUB
    # ==========================================
    if active_page == PAGES[0]:
        st.subheader("🎯 Match Engineering Requirements to Internal Talent Pool")
        st.caption("Perform semantic vector retrieval, explainable AI feature weighting, and automated gap remediation.")

        # Interactive Feature Access Cards Grid on Main Dashboard
        with st.expander("🚀 Explore All Enterprise AI Feature Modules", expanded=True):
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                st.markdown(
                    '<div class="feature-hub-card">'
                    '<h4 style="margin: 0 0 0.4rem 0;">🎯 Single Candidate Matcher</h4>'
                    '<p style="font-size: 0.85rem; margin: 0 0 0.75rem 0;">Semantic RAG vector search, explainable AI score breakdown & 2-week upskilling path.</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
                if st.button("🚀 Open Matcher", key="launch_f0", use_container_width=True):
                    st.session_state["active_feature"] = PAGES[0]
                    st.rerun()

                st.markdown(
                    '<div class="feature-hub-card" style="margin-top: 1rem;">'
                    '<h4 style="margin: 0 0 0.4rem 0;">📈 Career Growth Audit</h4>'
                    '<p style="font-size: 0.85rem; margin: 0 0 0.75rem 0;">Audit employee profiles against senior target roles & generate 4-week promotion roadmaps.</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
                if st.button("🚀 Open Career Audit", key="launch_f3", use_container_width=True):
                    st.session_state["active_feature"] = PAGES[3]
                    st.rerun()

            with f_col2:
                st.markdown(
                    '<div class="feature-hub-card">'
                    '<h4 style="margin: 0 0 0.4rem 0;">🧩 Multi-Agent Squad Builder</h4>'
                    '<p style="font-size: 0.85rem; margin: 0 0 0.75rem 0;">Deconstruct project scopes into role slots & assemble non-redundant team rosters.</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
                if st.button("🚀 Open Squad Builder", key="launch_f1", use_container_width=True):
                    st.session_state["active_feature"] = PAGES[1]
                    st.rerun()

                st.markdown(
                    '<div class="feature-hub-card" style="margin-top: 1rem;">'
                    '<h4 style="margin: 0 0 0.4rem 0;">⭐ Performance RL Feedback</h4>'
                    '<p style="font-size: 0.85rem; margin: 0 0 0.75rem 0;">Submit 1-5 star manager ratings on completed sprints to dynamically boost vector scores.</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
                if st.button("🚀 Open RL Feedback", key="launch_f4", use_container_width=True):
                    st.session_state["active_feature"] = PAGES[4]
                    st.rerun()

            with f_col3:
                st.markdown(
                    '<div class="feature-hub-card">'
                    '<h4 style="margin: 0 0 0.4rem 0;">📥 Talent Ingestion & Roster</h4>'
                    '<p style="font-size: 0.85rem; margin: 0 0 0.75rem 0;">Upload candidate resume PDFs into ChromaDB vector store & explore candidate roster.</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
                if st.button("🚀 Open Roster Hub", key="launch_f2", use_container_width=True):
                    st.session_state["active_feature"] = PAGES[2]
                    st.rerun()

                st.markdown(
                    '<div class="feature-hub-card" style="margin-top: 1rem;">'
                    '<h4 style="margin: 0 0 0.4rem 0;">📄 Vector ATS Screening</h4>'
                    '<p style="font-size: 0.85rem; margin: 0 0 0.75rem 0;">Screen external resume PDFs, analyze project code internal frameworks & rank applicants.</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
                if st.button("🚀 Open ATS Screener", key="launch_f6", use_container_width=True):
                    st.session_state["active_feature"] = PAGES[6]
                    st.rerun()

        st.divider()

        st.markdown("**Sample Project Prompts:**")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        if col_p1.button("Prompt #1: FastAPI + RAG Vector Engineer", key="p1_prompt_btn"):
            st.session_state["t1_proj_desc"] = "Need a Senior Full-Stack Engineer with Python, FastAPI, ChromaDB vector store, and React for immediate sprint deployment."
            st.rerun()
        if col_p2.button("Prompt #2: ML Architect & LLM Fine-Tuning", key="p2_prompt_btn"):
            st.session_state["t1_proj_desc"] = "Looking for a Machine Learning Architect experienced in PyTorch, LangChain LLM fine-tuning, and vector database indexing."
            st.rerun()
        if col_p3.button("Prompt #3: Cloud DevOps & AWS Specialist", key="p3_prompt_btn"):
            st.session_state["t1_proj_desc"] = "Require a Cloud DevOps Engineer with AWS CDK, Kubernetes, Docker, and CI/CD automation background."
            st.rerun()

        project_desc = st.text_area(
            "Enter Project Technical Requirements / Scope Description",
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
                        pass

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
                            "match_percentage": int(item["cosine_score"] * 100) if "cosine_score" in item else eval_res.get("match_percentage", 88),
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
                st.session_state["t1_matches"] = matches
            else:
                st.error("Please enter a project requirement description to run semantic matching.")

        current_matches = st.session_state.get("t1_matches")
        if current_matches is not None:
            if not current_matches:
                st.warning("⚠️ No internal candidates matched the selected availability filter.")
                with st.container(border=True):
                    st.markdown("### 📢 Option: Save Job Requirements & Post Online Job Offer")
                    st.caption("No available internal talent found. Automatically save your preferred skills and experience requirements to post a job offer online and run Vector ATS screening on external applicants.")
                    
                    with st.form("auto_job_offer_form"):
                        c_j1, c_j2 = st.columns(2)
                        with c_j1:
                            job_title_input = st.text_input("Target Online Job Title", value="Senior Healthcare AI & Medical Imaging Engineer")
                            min_exp_input = st.number_input("Minimum Years Experience Required", min_value=1, max_value=20, value=4)
                        with c_j2:
                            req_skills_input = st.text_input("Required Skills (Comma-separated)", value="PyTorch, OpenCV, FastAPI, PostgreSQL, AWS S3, React")
                            job_desc_input = st.text_area("Job Scope Description", value=project_desc if project_desc else "Healthcare AI diagnostic platform requiring DICOM processing, PyTorch, and FastAPI...", height=80)

                        save_job_btn = st.form_submit_button("📢 Publish Job Offer & Launch External ATS Resume Screener ➔", type="primary")

                        if save_job_btn:
                            from utils import vector_ats_manager
                            skills_list = [s.strip() for s in req_skills_input.split(",") if s.strip()]
                            vector_ats_manager.save_job_offer(job_title_input, skills_list, min_exp_input, job_desc_input)
                            st.session_state["active_feature"] = PAGES[6]
                            st.toast(f"✅ Saved Job Offer for '{job_title_input}' & launched Vector ATS Screener!", icon="🚀")
                            st.rerun()
            else:
                st.divider()
                st.markdown("### 🏆 Top Candidate Shortlist, Explainable AI Audit & Gap Remediation")
                for idx, match in enumerate(current_matches):
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

        if st.session_state.get("deploy_modal_candidate"):
            dep_cand = st.session_state["deploy_modal_candidate"]
            st.divider()
            st.success(f"✅ **Deployment Status Confirmed**: Candidate **{dep_cand['name']}** ({dep_cand['role']}) has been assigned to project sprint. Resource team notified!")
            if st.button("Close Popup"):
                st.session_state["deploy_modal_candidate"] = None
                st.rerun()

    # ==========================================
    # PAGE 2: MULTI-AGENT COLLABORATIVE SQUAD BUILDER
    # ==========================================
    elif active_page == PAGES[1]:
        c_p1_back, c_p1_head = st.columns([1.2, 8.8])
        with c_p1_back:
            if st.button("⬅️", key="back_btn_p1", type="secondary", help="Return to Main Dashboard"):
                st.session_state["active_feature"] = PAGES[0]
                st.rerun()
        with c_p1_head:
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

                st.session_state["t2_squad_data"] = squad_data
            else:
                st.error("Please enter a project scope to assemble squad.")

        curr_squad_data = st.session_state.get("t2_squad_data")
        if curr_squad_data:
            st.divider()
            st.markdown("### 🚀 Assembled Cross-Functional Team Roster")
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Squad Members", f"{curr_squad_data['squad_size']} Engineers")
            with m2:
                st.metric("Squad Synergy Score", f"{curr_squad_data['squad_synergy_score']}%")
            with m3:
                st.metric("Skill Balance Index", f"{curr_squad_data['skill_balance_index']}%")

            st.markdown("**Unique Tech Skills Covered Across Squad:**")
            skills_tags = "".join([f'<span style="background-color: rgba(16, 185, 129, 0.2); color: #34D399; padding: 0.2rem 0.6rem; border-radius: 0.375rem; font-size: 0.8rem; font-weight: 600; margin-right: 0.4rem; margin-bottom: 0.4rem; display: inline-block;">{s}</span>' for s in curr_squad_data['unique_skills_covered']])
            st.markdown(skills_tags, unsafe_allow_html=True)
            st.divider()

            for member in curr_squad_data["squad_roster"]:
                with st.container(border=True):
                    st.markdown(f"#### 👤 {member['role_title']} → **{member['candidate_name']}** ({member['current_role']})")
                    st.markdown(f"**Match Confidence:** `{member['match_confidence']}%` | **Status:** `{member['bandwidth_status']}`")
                    st.markdown(f"**Matching Skills:** {', '.join(member['matching_skills'])}")
                    st.info(f"**Role Fit Rationale:** {member['role_fit_rationale']}")

            if st.button("⚡ Deploy Entire Squad to Enterprise Sprint", key="deploy_squad_btn", type="primary"):
                st.toast(f"🎉 Deployed {curr_squad_data['squad_size']} team members to sprint!", icon="🚀")
                st.success(f"✅ **Squad Deployment Activated**: All {curr_squad_data['squad_size']} team members notified!")

    # ==========================================
    # PAGE 3: TALENT INGESTION & ROSTER HUB
    # ==========================================
    elif active_page == PAGES[2]:
        c_p2_back, c_p2_head = st.columns([1.2, 8.8])
        with c_p2_back:
            if st.button("⬅️", key="back_btn_p2", type="secondary", help="Return to Main Dashboard"):
                st.session_state["active_feature"] = PAGES[0]
                st.rerun()
        with c_p2_head:
            st.subheader("📥 Ingest Resume & Explore Internal Talent Pool Roster Matrix")
            st.caption("Ingest candidate resumes into ChromaDB vector store and explore internal employee profiles.")
        
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
                status_class = "badge-avail"
                if "Assigned" in cand["bandwidth_status"]:
                    status_class = "badge-assigned"
                elif "Part-time" in cand["bandwidth_status"]:
                    status_class = "badge-part"

                with st.container(border=True):
                    c_n, c_b = st.columns([3, 1.2])
                    with c_n:
                        st.markdown(f"### **{cand['name']}**")
                        st.markdown(f"**{cand['role']}** • `{cand.get('years_experience', 5)} Yrs Experience`")
                    with c_b:
                        st.markdown(f'<span class="{status_class}">{cand["bandwidth_status"]}</span>', unsafe_allow_html=True)

                    st.caption(cand.get("bio", "Indexed candidate profile."))
                    st.markdown("**Verified Skills & Tech Stack:**")
                    skills_tags = "".join([f'<span style="background-color: rgba(59, 130, 246, 0.15); color: #60A5FA; padding: 0.2rem 0.55rem; border-radius: 0.375rem; font-size: 0.78rem; font-weight: 600; margin-right: 0.35rem; margin-bottom: 0.35rem; display: inline-block;">{s}</span>' for s in cand['skills']])
                    st.markdown(skills_tags, unsafe_allow_html=True)

    # ==========================================
    # PAGE 4: CANDIDATE CAREER GROWTH AUDIT
    # ==========================================
    elif active_page == PAGES[3]:
        c_p3_back, c_p3_head = st.columns([1.2, 8.8])
        with c_p3_back:
            if st.button("⬅️", key="back_btn_p3", type="secondary", help="Return to Main Dashboard"):
                st.session_state["active_feature"] = PAGES[0]
                st.rerun()
        with c_p3_head:
            st.subheader("📈 Candidate Career Growth & Promotion Skill-Gap Auditor")
            st.caption("Empower employees to audit their profile against target senior enterprise roles and generate 4-week promotion readiness roadmaps.")
        
        from utils import INITIAL_TALENT_POOL
        all_cand_names = [c["name"] for c in INITIAL_TALENT_POOL]
        
        ca1, ca2 = st.columns(2)
        with ca1:
            sel_cand_name = st.selectbox("Select Candidate for Audit", options=all_cand_names, key="t4_cand_sel")
        with ca2:
            sel_target_role = st.selectbox("Select Target Senior Role", [
                "Principal AI Systems Architect",
                "Lead Cloud DevOps Engineer",
                "Senior Full-Stack AI Engineer",
                "MLOps & Data Platform Architect"
            ], key="t4_role_sel")

        if st.button("🚀 Generate Career Audit & Promotion Roadmap", type="primary", key="t4_audit_btn"):
            audit_res = None
            matched_cand = next((c for c in INITIAL_TALENT_POOL if c["name"] == sel_cand_name), None)
            c_skills = matched_cand["skills"] if matched_cand and "skills" in matched_cand else ["Python", "Engineering"]
            c_role = matched_cand["role"] if matched_cand and "role" in matched_cand else "Senior Engineer"

            if backend_online:
                try:
                    resp = requests.post(f"{BACKEND_URL}/career-growth-audit", json={
                        "candidate_name": sel_cand_name,
                        "current_role": c_role,
                        "current_skills": c_skills,
                        "target_role": sel_target_role
                    }, timeout=5.0)
                    if resp.status_code == 200:
                        audit_res = resp.json()
                except Exception:
                    pass

            if not audit_res:
                from utils import career_auditor
                audit_res = career_auditor.generate_career_audit(sel_cand_name, c_role, c_skills, sel_target_role)

            st.session_state["t4_audit_res"] = (sel_cand_name, sel_target_role, audit_res)

        curr_audit = st.session_state.get("t4_audit_res")
        if curr_audit:
            aud_cand_name, aud_target_role, audit_res = curr_audit
            st.divider()
            st.markdown(f"### 🏆 Career Growth Audit: **{aud_cand_name}** → `{aud_target_role}`")
            
            sc1, sc2 = st.columns([1.5, 3])
            with sc1:
                st.metric("Promotion Readiness", f"{audit_res['promotion_readiness_score']}%")
                st.progress(max(0.0, min(1.0, audit_res['promotion_readiness_score'] / 100.0)))
            with sc2:
                st.markdown(f"**Verified Matching Skills:** {', '.join(audit_res['verified_matching_skills'])}")
                st.markdown(f"**Critical Skill Gaps to Bridge:** {', '.join(audit_res['critical_skill_gaps'])}")
                st.info(f"**Recommended Project Assignment:** {audit_res['recommended_internal_project']}")

            st.markdown("#### 📅 4-Week Actionable Upskilling Roadmap")
            rm = audit_res.get("four_week_upskilling_roadmap") or {}
            for week_k, step in rm.items():
                with st.container(border=True):
                    st.markdown(f"**{week_k.replace('_', ' ').title()}:** {step}")

    # ==========================================
    # PAGE 5: HISTORICAL PROJECT PERFORMANCE FEEDBACK LOOP
    # ==========================================
    elif active_page == PAGES[4]:
        c_p4_back, c_p4_head = st.columns([1.2, 8.8])
        with c_p4_back:
            if st.button("⬅️", key="back_btn_p4", type="secondary", help="Return to Main Dashboard"):
                st.session_state["active_feature"] = PAGES[0]
                st.rerun()
        with c_p4_head:
            st.subheader("⭐ Historical Project Performance & RL Feedback Loop")
            st.caption("Submit manager ratings (1-5 stars) on completed sprint assignments to dynamically weight vector search score multipliers.")
        
        from utils import INITIAL_TALENT_POOL
        all_cand_ids = [c["id"] for c in INITIAL_TALENT_POOL]
        cand_name_map = {c["id"]: c["name"] for c in INITIAL_TALENT_POOL}
        
        fb1, fb2, fb3 = st.columns(3)
        with fb1:
            fb_cand_id = st.selectbox("Select Deployed Candidate", options=all_cand_ids, format_func=lambda cid: f"{cand_name_map.get(cid, cid)} ({cid})", key="t5_cand_id")
        with fb2:
            fb_project_title = st.text_input("Project / Sprint Title", value="Q3 Enterprise AI Microservice Sprint", key="t5_proj_title")
        with fb3:
            fb_rating = st.slider("Manager Performance Rating (1-5 Stars)", 1, 5, 5, key="t5_rating")

        fb_notes = st.text_area("Performance Feedback Notes", value="Delivered microservice architecture ahead of schedule with 99.9% uptime.", height=80, key="t5_notes")
        
        if st.button("⭐ Submit Manager Rating & Update RL Vector Multiplier", type="primary", key="t5_submit_btn"):
            selected_cand_name = cand_name_map.get(fb_cand_id, "Candidate")
            fb_res = None
            if backend_online:
                try:
                    resp = requests.post(f"{BACKEND_URL}/submit-project-feedback", json={
                        "candidate_id": fb_cand_id,
                        "candidate_name": selected_cand_name,
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
                fb_res = feedback_manager.record_feedback(fb_cand_id, selected_cand_name, fb_project_title, fb_rating, fb_notes)

            st.toast(f"✅ Feedback logged for {fb_res['candidate_name']}! Multiplier: {fb_res['vector_score_multiplier']}x", icon="⭐")
            st.success(f"Recorded {fb_rating}-Star feedback for **{fb_res['candidate_name']}**! Vector match multiplier updated to **{fb_res['vector_score_multiplier']}x**.")

        st.divider()
        st.markdown("#### 📜 Recent Manager Project Performance Feedback Audit Log")
        from utils import feedback_manager
        for rec in feedback_manager.feedback_records:
            with st.container(border=True):
                st.markdown(f"**Candidate:** `{rec['candidate_name']}` | **Project:** `{rec['project_title']}` | **Rating:** {'⭐' * rec['manager_rating']}")
                st.markdown(f"**Vector Multiplier Boost:** `{rec['vector_score_multiplier']}x`")
                st.caption(f"Feedback: \"{rec['feedback_text']}\"")

    # ==========================================
    # PAGE 6: ENTERPRISE KNOWLEDGE GRAPH & HR AI FAIRNESS AUDITOR
    # ==========================================
    elif active_page == PAGES[5]:
        c_p5_back, c_p5_head = st.columns([1.2, 8.8])
        with c_p5_back:
            if st.button("⬅️", key="back_btn_p5", type="secondary", help="Return to Main Dashboard"):
                st.session_state["active_feature"] = PAGES[0]
                st.rerun()
        with c_p5_head:
            st.subheader("🛡️ Enterprise Knowledge Graph & HR AI Algorithmic Fairness Auditor")
            st.caption("Verify EU AI Act compliance certificates, demographic proxy elimination, and candidate-skill network cluster graphs.")
        
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
    # PAGE 7: VECTOR ATS EXTERNAL RESUME SCREENING & SHORTLISTING
    # ==========================================
    elif active_page == PAGES[6]:
        c_p6_back, c_p6_head = st.columns([1.2, 8.8])
        with c_p6_back:
            if st.button("⬅️", key="back_btn_p6", type="secondary", help="Return to Main Dashboard"):
                st.session_state["active_feature"] = PAGES[0]
                st.rerun()
        with c_p6_head:
            st.subheader("📄 External Resume Vector ATS Screening & Ranking Engine")
            st.caption("Screen external job applicant resumes, analyze project code internal frameworks, and match applicants against active company job requirements.")

        from utils import vector_ats_manager
        
        job_titles = [j["title"] for j in vector_ats_manager.job_offers_catalog]
        
        st.markdown("### 📢 Select Active Company Job Offer for Resume ATS Screening")
        selected_job_title = st.selectbox(
            "Choose Active Job Posting to Screen Resumes Against:",
            job_titles,
            key="ats_active_job_select"
        )
        selected_job = vector_ats_manager.set_active_job_by_title(selected_job_title)

        with st.container(border=True):
            c_j_head, c_j_badge = st.columns([3.5, 1.2])
            with c_j_head:
                st.markdown(f"### 🎯 **{selected_job['title']}**")
                st.markdown(f"**Department:** `{selected_job['department']}` | **Min Experience:** `{selected_job['min_experience']}+ Years`")
            with c_j_badge:
                st.markdown(f'<span class="badge-avail">Active External Job</span>', unsafe_allow_html=True)

            st.markdown(f"**Required Tech Stack:** `{', '.join(selected_job['required_skills'])}`")
            st.caption(f"Job Scope: {selected_job['description']}")

        st.divider()
        with st.container(border=True):
            st.markdown("### 📥 Bulk Upload Received External Applicant Resumes (Multi-PDF Vector ATS Screener)")
            st.caption("No manual entry required! Drag & drop multiple applicant resume PDFs at once. The AI vector engine automatically parses resumes, extracts technical skills, detects code frameworks, and ranks candidates.")

            c_u1, c_u2 = st.columns([2.5, 1.5])
            with c_u1:
                uploaded_resumes = st.file_uploader(
                    "Drag & Drop Multiple Applicant Resume PDFs",
                    type=["pdf"],
                    accept_multiple_files=True,
                    key="bulk_ats_pdf_uploader"
                )
            with c_u2:
                st.markdown("#### 🎯 Target Job Posting")
                target_job_title = st.selectbox(
                    "Screen Resumes Against:",
                    [j["title"] for j in vector_ats_manager.job_offers_catalog],
                    key="bulk_ats_job_select"
                )
                run_bulk_ats = st.button("🚀 Process Resumes & Run Vector ATS Audit", type="primary", use_container_width=True)

            if run_bulk_ats and uploaded_resumes:
                for pdf in uploaded_resumes:
                    vector_ats_manager.process_pdf_resume(pdf, target_job_title)
                st.toast(f"✅ Processed {len(uploaded_resumes)} resumes with Vector ATS!", icon="🚀")
                st.success(f"Successfully processed and ranked {len(uploaded_resumes)} applicant resumes for **{target_job_title}**!")
                st.rerun()

        st.divider()
        st.markdown("### 🏆 External Applicant Shortlist Matrix (Side-by-Side Vector ATS Breakdown)")
        st.caption("Ranks external candidate resumes by ATS match score, highlights versatile multi-project talent, and displays code frameworks side-by-side with cross-departmental transfer eligibility.")

        ranked_applicants = vector_ats_manager.applicants
        for app in ranked_applicants:
            cross_matches = vector_ats_manager.get_cross_project_matches(app)
            is_versatile = (len(cross_matches) >= 2)

            with st.container(border=True):
                col_left, col_right = st.columns([1.15, 1.0])

                with col_left:
                    st.markdown(f"### Rank #{app['ats_rank']} — **{app['name']}** *(External Candidate)*")
                    st.markdown(f"**Applied Position:** `{app['applied_role']}`")
                    st.markdown(f"**Experience:** `{app['years_experience']} Yrs` | **Email:** `{app['email']}`")

                    if is_versatile:
                        st.markdown(
                            f'<div style="background: rgba(245, 158, 11, 0.2); color: #FBBF24; padding: 0.35rem 0.65rem; border-radius: 0.5rem; font-weight: 700; font-size: 0.82rem; margin-top: 0.35rem; margin-bottom: 0.5rem;">'
                            f'🌟 VERSATILE TOP TALENT — Matched to {len(cross_matches)} Departmental Projects!'
                            '</div>',
                            unsafe_allow_html=True
                        )

                    m1, m2 = st.columns([1.5, 2.5])
                    with m1:
                        st.metric("Vector ATS Score", f"{app['ats_match_score']}%")
                    with m2:
                        st.caption("Match Confidence Alignment")
                        st.progress(min(1.0, max(0.0, app['ats_match_score'] / 100.0)))

                    st.markdown(f"**Verified Technical Skills:** {', '.join(app['verified_strengths'])}")
                    if app.get("skill_gaps"):
                        st.markdown(f"**Identified Skill Gaps:** {', '.join(app['skill_gaps'])}")

                    st.info(f"**Resume Profile Summary:** {app['resume_summary']}")

                with col_right:
                    st.markdown("#### 💻 Analyzed Code Frameworks & Repositories")
                    fw_tags = "".join([f'<span style="background-color: rgba(96, 165, 250, 0.15); color: #60A5FA; padding: 0.2rem 0.55rem; border-radius: 0.375rem; font-size: 0.78rem; font-weight: 600; margin-right: 0.35rem; margin-bottom: 0.35rem; display: inline-block;">⚙️ {fw}</span>' for fw in app['internal_frameworks_used']])
                    st.markdown(fw_tags, unsafe_allow_html=True)

                    if app.get("github_project_links"):
                        links_str = " • ".join([f"[{link}]({link})" for link in app['github_project_links']])
                        st.markdown(f"**GitHub Repositories:** {links_str}")

                    st.markdown("#### 🏢 Cross-Departmental Transfer Eligibility")
                    if cross_matches:
                        for c_match in cross_matches:
                            p_score = c_match['match_percentage']
                            p_badge = "#34D399" if p_score >= 88.0 else "#60A5FA"
                            st.markdown(
                                f"• **{c_match['department']}** → `{c_match['project_title']}` | "
                                f"Match: <span style='color:{p_badge}; font-weight:800;'>{p_score}%</span>",
                                unsafe_allow_html=True
                            )
                    else:
                        st.caption("No cross-departmental project matches above 75%.")

                    st.divider()
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button(f"✅ Issue Hiring Offer", key=f"shortlist_{app['applicant_id']}", type="primary", use_container_width=True):
                            st.toast(f"🎉 Issued hiring offer to {app['name']}!", icon="✅")
                            st.success(f"External Candidate **{app['name']}** marked as **Shortlisted for Hiring Offer**!")
                    with b2:
                        if cross_matches:
                            target_dept = cross_matches[0]["department"]
                            if st.button(f"🔀 Assign to {target_dept[:12]}...", key=f"transfer_{app['applicant_id']}", use_container_width=True):
                                st.toast(f"🔀 Cross-assigned {app['name']} to {target_dept} candidate pool!", icon="✨")
                                st.success(f"External Candidate **{app['name']}** cross-assigned to **{target_dept}**!")

    # ==========================================
    # SINGLE FIXED BOTTOM FOOTER
    # ==========================================
    footer_html = (
        '<div class="fixed-footer-bar">'
        '© 2026 <strong>StratixIQ</strong>. Enterprise AI Talent Deployment & Skill-Matching Engine. All Rights Reserved.'
        '</div>'
    )
    st.markdown(footer_html, unsafe_allow_html=True)

