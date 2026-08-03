import streamlit as st
import requests

st.set_page_config(
    page_title="StratixIQ - Agile Talent Deployment",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ StratixIQ: Agile Talent Deployment & Skill-Matching Engine")
st.caption("AI-driven vector search & RAG pipeline for instant candidate staffing")

tab1, tab2 = st.tabs(["📤 Upload Employee Profile", "🎯 Project Staffing Engine"])

with tab1:
    st.header("Upload Candidate Resume (PDF)")
    with st.form("upload_form"):
        candidate_name = st.text_input("Candidate Full Name", placeholder="e.g. Sarah Connor")
        bandwidth_status = st.selectbox("Current Bandwidth / Availability", [
            "Available Immediately",
            "Assigned until next month",
            "Part-time bandwidth (50%)"
        ])
        uploaded_file = st.file_uploader("Choose a PDF Resume", type=["pdf"])
        submit_button = st.form_submit_button("Index Profile into Vector DB")
        
        if submit_button:
            if candidate_name and uploaded_file:
                st.success(f"Indexed profile for {candidate_name} with status: '{bandwidth_status}'")
            else:
                st.error("Please provide candidate name and upload a PDF file.")

with tab2:
    st.header("Match Project Requirements to Talent Pool")
    project_desc = st.text_area(
        "Enter Technical Requirements / Project Scope",
        placeholder="Need a senior engineer with FastAPI, PostgreSQL, vector database experience, and LLM fine-tuning background...",
        height=150
    )
    
    if st.button("Run Semantic Talent Search"):
        if project_desc:
            st.markdown("### Top Candidate Shortlist & Skill-Gap Analysis")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Match Confidence", value="94%", delta="High Match")
                st.subheader("Alex Rivera")
                st.badge("Available Immediately")
                st.markdown("**Verified Skills:** Python, FastAPI, ChromaDB, OpenAI, LangChain")
                st.markdown("**Skill Gaps:** AWS CDK")
                st.info("**Deployment Rationale:** Alex has extensive hands-on experience building FastAPI microservices integrated with vector stores.")
            
            with col2:
                st.metric(label="Match Confidence", value="87%", delta="Moderate Match")
                st.subheader("Elena Rostova")
                st.badge("Part-time bandwidth")
                st.markdown("**Verified Skills:** Python, PyTorch, LangChain, PostgreSQL")
                st.markdown("**Skill Gaps:** FastAPI Endpoint optimization")
                st.info("**Deployment Rationale:** Elena brings strong ML foundation and RAG experience, available for immediate partial allocation.")
        else:
            st.warning("Please enter a project description to find candidate matches.")
