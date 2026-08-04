from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uvicorn
import uuid

from utils import (
    extract_text_from_pdf, vector_store, llm_manager,
    squad_assembler, career_auditor, feedback_manager,
    knowledge_graph_mgr, fairness_auditor
)

app = FastAPI(
    title="StratixIQ Talent Deployment & Skill-Matching API",
    description="Asynchronous Enterprise AI RAG Engine API",
    version="2.0.0"
)

# Enable CORS for Next.js / Streamlit / Web Clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initial Talent Roster Database
INITIAL_TALENT_POOL: List[Dict[str, Any]] = [
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

# Seed initial candidates into ChromaDB vector store on launch
for cand in INITIAL_TALENT_POOL:
    vector_store.add_candidate_profile(
        candidate_id=cand["id"],
        candidate_name=cand["name"],
        role=cand["role"],
        bandwidth_status=cand["bandwidth_status"],
        skills=cand["skills"],
        raw_text=f"{cand['role']} - {cand['bio']}. Past Projects: {', '.join(cand['past_projects'])}"
    )

# ==========================================
# PYDANTIC V2 SCHEMAS
# ==========================================
class MatchRequest(BaseModel):
    project_description: str = Field(..., description="Engineering project requirements description")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Top K candidate matches to retrieve")
    bandwidth_filter: Optional[str] = Field("All Availability", description="Filter candidates by bandwidth status")

class ExplainableAIBreakdown(BaseModel):
    core_tech_stack_weight: float = Field(..., description="Weight attributed to matching skills")
    experience_depth_weight: float = Field(..., description="Weight attributed to experience level")
    availability_timeline_weight: float = Field(..., description="Weight attributed to availability status")

class UpskillingPath(BaseModel):
    week_1: str = Field(..., description="Targeted learning plan for week 1")
    week_2: str = Field(..., description="Targeted learning plan for week 2")

class CandidateMatchResponse(BaseModel):
    id: str
    name: str
    role: str
    bandwidth_status: str
    skills: List[str]
    match_percentage: int = Field(..., ge=0, le=100)
    verified_strengths: List[str]
    skill_gaps: List[str]
    deployment_rationale: str
    explainable_ai_breakdown: ExplainableAIBreakdown
    upskilling_path: UpskillingPath

class ConfigProviderRequest(BaseModel):
    provider_name: str = Field(..., description="LLM provider e.g. 'openai', 'ollama', 'hybrid_local'")

class UploadProfileResponse(BaseModel):
    success: bool
    message: str
    candidate_id: str
    extracted_character_count: int

class SquadRequest(BaseModel):
    project_scope: str = Field(..., description="High-level project scope description")

class CareerAuditRequest(BaseModel):
    candidate_name: str
    current_role: str
    current_skills: List[str]
    target_role: str

class FeedbackRequest(BaseModel):
    candidate_id: str
    candidate_name: str
    project_title: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: str

# ==========================================
# ASYNCHRONOUS API ROUTES
# ==========================================
@app.get("/")
async def read_root():
    return {
        "status": "online",
        "service": "StratixIQ Enterprise AI Talent Deployment Engine",
        "llm_provider": llm_manager.provider
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "indexed_vector_count": vector_store.get_total_count(),
        "active_llm_provider": llm_manager.provider,
        "chroma_db_active": vector_store.use_chroma
    }

@app.get("/talent-pool")
async def get_talent_pool():
    return {"talent_pool": INITIAL_TALENT_POOL}

@app.post("/config/llm-provider")
async def configure_llm_provider(payload: ConfigProviderRequest):
    llm_manager.set_provider(payload.provider_name)
    return {
        "message": f"Successfully updated LLM Provider to '{llm_manager.provider}'",
        "active_provider": llm_manager.provider
    }

@app.post("/upload-profile", response_model=UploadProfileResponse)
async def upload_candidate_profile(
    candidate_name: str = Form(...),
    role: str = Form("Software Engineer"),
    bandwidth_status: str = Form("Available Immediately"),
    skills: str = Form("Python, Engineering"),
    bio: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    try:
        extracted_text = bio
        if file is not None:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF resume files are supported")
            pdf_bytes = await file.read()
            parsed_pdf_text = extract_text_from_pdf(pdf_bytes)
            if parsed_pdf_text and not parsed_pdf_text.startswith("PDF Extraction Note"):
                extracted_text = f"{bio}\n\n[PDF RESUME CONTENT]\n{parsed_pdf_text}"

        cand_id = f"cand_{uuid.uuid4().hex[:8]}"
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]

        new_candidate = {
            "id": cand_id,
            "name": candidate_name.strip(),
            "role": role.strip(),
            "bandwidth_status": bandwidth_status,
            "skills": skills_list,
            "bio": bio.strip() if bio.strip() else "Indexed candidate profile.",
            "years_experience": 5,
            "past_projects": ["Enterprise Ingested Profile"]
        }

        INITIAL_TALENT_POOL.insert(0, new_candidate)

        # Index chunk embeddings into ChromaDB persistent vector store
        vector_store.add_candidate_profile(
            candidate_id=cand_id,
            candidate_name=candidate_name.strip(),
            role=role.strip(),
            bandwidth_status=bandwidth_status,
            skills=skills_list,
            raw_text=extracted_text or f"{role} - {bio}"
        )

        return UploadProfileResponse(
            success=True,
            message=f"Indexed candidate profile for {candidate_name} into ChromaDB vector store",
            candidate_id=cand_id,
            extracted_character_count=len(extracted_text)
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest profile: {str(e)}")

@app.post("/match-talent", response_model=List[CandidateMatchResponse])
async def match_talent_requirements(payload: MatchRequest):
    if not payload.project_description.strip():
        raise HTTPException(status_code=400, detail="Project requirement description cannot be empty")

    try:
        vector_results = vector_store.query_candidates(
            query_text=payload.project_description,
            top_k=payload.top_k,
            bandwidth_filter=payload.bandwidth_filter
        )

        matches = []
        for v_item in vector_results:
            cid = v_item["candidate_id"]
            cand_profile = next((c for c in INITIAL_TALENT_POOL if c["id"] == cid), None)
            if not cand_profile:
                cand_profile = {
                    "id": cid,
                    "name": v_item["candidate_name"],
                    "role": v_item["role"],
                    "bandwidth_status": v_item["bandwidth_status"],
                    "skills": v_item["skills"],
                    "bio": "Indexed vector candidate.",
                    "years_experience": 5,
                    "past_projects": ["Vector DB Index"]
                }

            llm_eval = llm_manager.generate_structured_match(
                project_desc=payload.project_description,
                candidate_info=cand_profile
            )

            explain_data = llm_eval.get("explainable_ai_breakdown", {})
            upskill_data = llm_eval.get("upskilling_path", {})

            # Apply RL feedback multiplier boost
            mult = feedback_manager.get_candidate_multiplier(cid)
            boosted_score = min(99, int(llm_eval.get("match_percentage", 80) * mult))

            matches.append(CandidateMatchResponse(
                id=cand_profile["id"],
                name=cand_profile["name"],
                role=cand_profile["role"],
                bandwidth_status=cand_profile["bandwidth_status"],
                skills=cand_profile["skills"],
                match_percentage=boosted_score,
                verified_strengths=llm_eval.get("verified_strengths", cand_profile["skills"][:3]),
                skill_gaps=llm_eval.get("skill_gaps", []),
                deployment_rationale=llm_eval.get("deployment_rationale", "Strong technical fit."),
                explainable_ai_breakdown=ExplainableAIBreakdown(
                    core_tech_stack_weight=explain_data.get("core_tech_stack_weight", 45.0),
                    experience_depth_weight=explain_data.get("experience_depth_weight", 30.0),
                    availability_timeline_weight=explain_data.get("availability_timeline_weight", 25.0)
                ),
                upskilling_path=UpskillingPath(
                    week_1=upskill_data.get("week_1", "Review core framework architecture & APIs."),
                    week_2=upskill_data.get("week_2", "Build sandbox integration project.")
                )
            ))

        matches.sort(key=lambda x: x.match_percentage, reverse=True)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Talent matching error: {str(e)}")

# ==========================================
# NEW ENDPOINTS FOR ADVANCED FEATURES
# ==========================================
@app.post("/assemble-squad")
async def assemble_collaborative_squad(payload: SquadRequest):
    if not payload.project_scope.strip():
        raise HTTPException(status_code=400, detail="Project scope cannot be empty")
    return squad_assembler.decompose_and_assemble(payload.project_scope, vector_store, llm_manager)

@app.post("/career-growth-audit")
async def audit_candidate_career_growth(payload: CareerAuditRequest):
    return career_auditor.generate_career_audit(
        candidate_name=payload.candidate_name,
        current_role=payload.current_role,
        current_skills=payload.current_skills,
        target_role=payload.target_role
    )

@app.post("/submit-project-feedback")
async def submit_project_feedback(payload: FeedbackRequest):
    return feedback_manager.record_feedback(
        candidate_id=payload.candidate_id,
        candidate_name=payload.candidate_name,
        project_title=payload.project_title,
        rating=payload.rating,
        feedback_text=payload.feedback_text
    )

@app.get("/knowledge-graph")
async def get_enterprise_knowledge_graph():
    return knowledge_graph_mgr.generate_graph_data(INITIAL_TALENT_POOL)

@app.post("/audit-fairness")
async def audit_algorithmic_fairness(payload: List[Dict[str, Any]]):
    return fairness_auditor.audit_matching_fairness(payload)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
