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
    },
    {
        "id": "cand_6",
        "name": "Rahul Sharma",
        "role": "Senior AI Systems Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Python", "FastAPI", "PyMuPDF", "ChromaDB", "Docker", "PyTorch", "LangChain"],
        "bio": "3 years building enterprise RAG retrieval systems, vector store indexing pipelines, and high-throughput microservices.",
        "years_experience": 3,
        "past_projects": ["Enterprise RAG Retrieval System", "Vector Store Indexing Pipeline", "High-Throughput Microservice"]
    },
    {
        "id": "cand_7",
        "name": "Priya Patel",
        "role": "Lead Backend Developer",
        "bandwidth_status": "Assigned until next month",
        "skills": ["Java", "Spring Boot", "MySQL", "REST APIs", "Microservices", "Kubernetes", "AWS"],
        "bio": "5 years scaling high-traffic financial transaction systems and performing deep relational database performance tuning.",
        "years_experience": 5,
        "past_projects": ["Financial Transaction Processing Engine", "Database Performance Tuning", "Spring Boot Microservices"]
    },
    {
        "id": "cand_8",
        "name": "Amit Kumar",
        "role": "Data Scientist & ML Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Python", "Pandas", "Scikit-Learn", "TensorFlow", "SQL", "Tableau", "Naive Bayes"],
        "bio": "2 years engineering predictive analytics dashboards, classification models, and data pipeline ETL workflows.",
        "years_experience": 2,
        "past_projects": ["Predictive Analytics Dashboard", "Customer Classification Engine", "ETL Data Pipeline"]
    },
    {
        "id": "cand_9",
        "name": "Sneha Reddy",
        "role": "Full-Stack Web Architect",
        "bandwidth_status": "Part-time bandwidth (50%)",
        "skills": ["React", "Node.js", "TypeScript", "PostgreSQL", "TailwindCSS", "Express", "GraphQL"],
        "bio": "4 years building responsive SaaS dashboards, modern component libraries, and scalable asynchronous Node servers.",
        "years_experience": 4,
        "past_projects": ["SaaS Analytics Dashboard", "Asynchronous Node Server", "Design Component Library"]
    },
    {
        "id": "cand_10",
        "name": "Vikramaditya Rao",
        "role": "DevOps & Cloud Infrastructure Lead",
        "bandwidth_status": "Available Immediately",
        "skills": ["Terraform", "AWS", "Kubernetes", "Docker", "CI/CD Pipelines", "Prometheus", "Grafana"],
        "bio": "6 years designing multi-region cloud infrastructure, container orchestration, and zero-downtime deployment pipelines.",
        "years_experience": 6,
        "past_projects": ["Multi-Region Cloud Infrastructure", "Container Orchestration Engine", "Zero-Downtime CI/CD Pipeline"]
    },
    {
        "id": "cand_11",
        "name": "Ananya Deshmukh",
        "role": "Conversational AI & NLP Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Python", "Hugging Face Transformers", "BERT", "Spacy", "LangChain", "OpenAI API", "FastAPI"],
        "bio": "3 years fine-tuning open-source LLMs, building semantic search agents, and handling intent-classification models.",
        "years_experience": 3,
        "past_projects": ["Open-Source LLM Fine-Tuning", "Semantic Search Agent", "Intent Classification Pipeline"]
    },
    {
        "id": "cand_12",
        "name": "Karthik Nambiar",
        "role": "Cyber Security & Compliance Engineer",
        "bandwidth_status": "Assigned until next month",
        "skills": ["Penetration Testing", "OAuth2", "JWT", "Network Security", "Python", "Bash", "SOC 2 Compliance"],
        "bio": "4 years auditing enterprise infrastructure, enforcing data privacy regulations, and securing cloud access points.",
        "years_experience": 4,
        "past_projects": ["Enterprise Infrastructure Security Audit", "Cloud Access Hardening", "SOC 2 Compliance Pipeline"]
    },
    {
        "id": "cand_13",
        "name": "Divya Iyer",
        "role": "Big Data & ETL Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Apache Spark", "PySpark", "Hadoop", "Kafka", "Snowflake", "Airflow", "SQL"],
        "bio": "5 years building petabyte-scale data lakes, streaming real-time pipelines, and optimizing cloud data warehouse tables.",
        "years_experience": 5,
        "past_projects": ["Petabyte-Scale Data Lake", "Real-Time Kafka Streaming", "Snowflake Data Warehouse Optimization"]
    },
    {
        "id": "cand_14",
        "name": "Mohammed Zaid",
        "role": "Frontend UI/UX Developer",
        "bandwidth_status": "Part-time bandwidth (50%)",
        "skills": ["Vue.js", "JavaScript", "HTML5", "CSS3", "Figma to Code", "TailwindCSS", "Webpack"],
        "bio": "3 years converting complex enterprise design mockups into highly optimized, accessible, and fast web applications.",
        "years_experience": 3,
        "past_projects": ["Enterprise Web Application UI", "Figma Design System Conversion", "Frontend Bundle Optimization"]
    },
    {
        "id": "cand_15",
        "name": "Meera Namboodiri",
        "role": "Mobile Application Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Flutter", "Dart", "Firebase", "REST API Integration", "iOS", "Android", "Git"],
        "bio": "3 years developing cross-platform mobile apps with seamless offline caching and real-time state synchronization.",
        "years_experience": 3,
        "past_projects": ["Cross-Platform Mobile App", "Offline-First Data Sync", "Real-Time Firebase Integration"]
    },
    {
        "id": "cand_16",
        "name": "Arjun Menon",
        "role": "Distributed Systems Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Go", "gRPC", "Docker", "Kubernetes", "Redis", "Apache Kafka", "Distributed Locking"],
        "bio": "4 years engineering low-latency microservices communication layers and high-concurrency background job workers.",
        "years_experience": 4,
        "past_projects": ["Low-Latency gRPC Microservices", "High-Concurrency Background Worker", "Distributed Cache System"]
    },
    {
        "id": "cand_17",
        "name": "Neha Kulkarni",
        "role": "QA Automation & Reliability Engineer",
        "bandwidth_status": "Assigned until next month",
        "skills": ["Python", "PyTest", "Selenium", "Playwright", "CI/CD Testing", "Postman", "JMeter"],
        "bio": "4 years building robust end-to-end automated test suites and performance load-testing frameworks for release pipelines.",
        "years_experience": 4,
        "past_projects": ["Automated E2E Test Suite", "CI/CD Regression Framework", "Performance Load Testing Pipeline"]
    },
    {
        "id": "cand_18",
        "name": "Rohan Srivastav",
        "role": "Database Reliability Engineer (DBA)",
        "bandwidth_status": "Available Immediately",
        "skills": ["PostgreSQL", "MongoDB", "Redis", "Query Optimization", "Indexing", "Sharding", "Backup Strategies"],
        "bio": "5 years managing massive relational and NoSQL database clusters, ensuring high availability and zero data loss.",
        "years_experience": 5,
        "past_projects": ["PostgreSQL High-Availability Cluster", "MongoDB Sharding & Scaling", "NoSQL Query Optimization"]
    },
    {
        "id": "cand_19",
        "name": "Swathi Varma",
        "role": "Computer Vision Engineer",
        "bandwidth_status": "Part-time bandwidth (50%)",
        "skills": ["OpenCV", "PyTorch", "YOLOv8", "Image Processing", "C++", "Python", "ONNX Runtime"],
        "bio": "3 years building real-time object detection models and edge-device computer vision inference pipelines.",
        "years_experience": 3,
        "past_projects": ["Real-Time Object Detection Model", "Edge-Device Vision Inference Pipeline", "PyTorch Image Processing"]
    },
    {
        "id": "cand_20",
        "name": "Manish Gupta",
        "role": "Enterprise Solutions Architect",
        "bandwidth_status": "Assigned until next month",
        "skills": ["System Design", "Enterprise Integration", "AWS", "Microservices", "TOGAF", "Python", "Java"],
        "bio": "8 years bridging business requirements with resilient, fault-tolerant cloud architecture blueprints for global clients.",
        "years_experience": 8,
        "past_projects": ["Enterprise Integration Blueprint", "Fault-Tolerant AWS Microservices", "Global Enterprise Architecture"]
    },
    {
        "id": "cand_21",
        "name": "Tanya Sen",
        "role": "Generative AI Application Developer",
        "bandwidth_status": "Available Immediately",
        "skills": ["LlamaIndex", "LangChain", "Python", "ChromaDB", "Pinecone", "Streamlit", "Prompt Engineering"],
        "bio": "2 years prototyping custom enterprise chatbots, internal knowledge-base search engines, and multi-agent workflows.",
        "years_experience": 2,
        "past_projects": ["Enterprise Chatbot Prototype", "Internal Knowledge Search Engine", "Multi-Agent Workflow Engine"]
    },
    {
        "id": "cand_22",
        "name": "Aditya Verma",
        "role": "Embedded Linux & IoT Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["C", "C++", "Embedded Linux", "FreeRTOS", "MQTT", "ARM Cortex", "Python"],
        "bio": "4 years writing low-level firmware and connecting smart edge devices to cloud telemetry dashboards.",
        "years_experience": 4,
        "past_projects": ["Embedded Linux Firmware", "Smart Edge IoT Telemetry", "FreeRTOS Kernel Customization"]
    },
    {
        "id": "cand_23",
        "name": "Pooja Hegde",
        "role": "Business Intelligence Analyst",
        "bandwidth_status": "Part-time bandwidth (50%)",
        "skills": ["PowerBI", "Tableau", "Advanced SQL", "Excel", "Python (Pandas)", "Data Storytelling"],
        "bio": "3 years turning raw corporate operational metrics into executive-level interactive dashboards and revenue growth insights.",
        "years_experience": 3,
        "past_projects": ["Executive PowerBI Dashboard", "Revenue Growth Analytics", "Corporate Operational Insights"]
    },
    {
        "id": "cand_24",
        "name": "Nikhil Choudhary",
        "role": "Blockchain & Smart Contract Developer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Solidity", "Hardhat", "Ethers.js", "Rust", "Web3.js", "Node.js", "Cryptography"],
        "bio": "3 years developing secure decentralized finance (DeFi) protocols and auditing smart contract vulnerability vectors.",
        "years_experience": 3,
        "past_projects": ["DeFi Protocol Smart Contracts", "Smart Contract Vulnerability Audit", "Web3 Integration Layer"]
    },
    {
        "id": "cand_25",
        "name": "Kavya Sridhar",
        "role": "Product Operations & Data Specialist",
        "bandwidth_status": "Available Immediately",
        "skills": ["Python", "Jira API", "Confluence Automation", "Agile/Scrum Metrics", "Mixpanel", "SQL"],
        "bio": "3 years streamlining engineering delivery tracking, release velocity reporting, and cross-functional team roadmaps.",
        "years_experience": 3,
        "past_projects": ["Jira Automation & Delivery Metrics", "Release Velocity Dashboard", "Agile Roadmap Analytics"]
    },
    {
        "id": "cand_26",
        "name": "Siddharth Rao",
        "role": "Backend API Developer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Node.js", "Express", "MongoDB", "TypeScript", "Jest", "Docker", "Redis"],
        "bio": "3 years designing secure RESTful API layers and third-party webhooks for high-growth SaaS applications.",
        "years_experience": 3,
        "past_projects": ["RESTful SaaS API Layer", "Webhooks Integration Microservice", "Node.js Express Backend"]
    },
    {
        "id": "cand_27",
        "name": "Lavanya Ramesh",
        "role": "Machine Learning Operations (MLOps) Engineer",
        "bandwidth_status": "Assigned until next month",
        "skills": ["MLflow", "Kubeflow", "Docker", "Python", "AWS SageMaker", "GitHub Actions", "Prometheus"],
        "bio": "4 years automating model training loops, model registry management, and production monitoring.",
        "years_experience": 4,
        "past_projects": ["Kubeflow Automated Model Training", "AWS SageMaker Deployment Pipeline", "Model Monitoring System"]
    },
    {
        "id": "cand_28",
        "name": "Tarun Bachan",
        "role": "Systems Performance Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["C++", "Linux Kernel", "Performance Profiling", "Memory Management", "Valgrind", "Python"],
        "bio": "5 years profiling CPU bottlenecks, optimizing low-level memory usage, and writing high-frequency trading tools.",
        "years_experience": 5,
        "past_projects": ["Low-Level C++ Memory Optimization", "CPU Bottleneck Profiler", "High-Frequency Trading System"]
    },
    {
        "id": "cand_29",
        "name": "Ritu Chakraborty",
        "role": "UI Component Library Developer",
        "bandwidth_status": "Part-time bandwidth (50%)",
        "skills": ["React", "Storybook", "CSS Modules", "TypeScript", "Jest", "Accessibility (a11y)"],
        "bio": "3 years crafting design systems and accessible component libraries used across multi-brand enterprise portals.",
        "years_experience": 3,
        "past_projects": ["Multi-Brand Design System", "Storybook UI Component Library", "Accessible Web Components"]
    },
    {
        "id": "cand_30",
        "name": "Abhinav Sharma",
        "role": "Cloud Security Architect",
        "bandwidth_status": "Available Immediately",
        "skills": ["IAM Policies", "AWS Security Hub", "HashiCorp Vault", "Kubernetes Security", "Python"],
        "bio": "6 years hardening enterprise cloud perimeters, auditing access keys, and enforcing zero-trust networking.",
        "years_experience": 6,
        "past_projects": ["Zero-Trust Cloud Architecture", "AWS IAM Security Hardening", "HashiCorp Vault Integration"]
    },
    {
        "id": "cand_31",
        "name": "Deepika Padukone",
        "role": "Data Governance & Compliance Analyst",
        "bandwidth_status": "Assigned until next month",
        "skills": ["GDPR", "Data Lineage", "Collibra", "SQL", "Python", "Metadata Management", "Risk Assessment"],
        "bio": "4 years managing enterprise data governance frameworks, security classifications, and data catalog pipelines.",
        "years_experience": 4,
        "past_projects": ["GDPR Compliance Framework", "Enterprise Data Lineage Catalog", "Collibra Metadata Pipeline"]
    },
    {
        "id": "cand_32",
        "name": "Varun Tej",
        "role": "Game & Interactive Simulation Engineer",
        "bandwidth_status": "Part-time bandwidth (50%)",
        "skills": ["C#", "Unity Engine", "Shader Programming", "3D Mathematics", "Performance Optimization"],
        "bio": "4 years developing interactive training simulations and real-time visualization applications.",
        "years_experience": 4,
        "past_projects": ["Interactive 3D Training Simulation", "Unity Performance Optimization", "Custom Shader System"]
    },
    {
        "id": "cand_33",
        "name": "Shreya Ghoshal",
        "role": "Technical Content & Documentation Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Markdown", "OpenAPI/Swagger", "Python Scripting for Docs", "Git", "Sphinx", "Technical Writing"],
        "bio": "3 years writing developer guides, SDK reference manuals, and automated API documentation portals.",
        "years_experience": 3,
        "past_projects": ["Developer SDK Documentation Portal", "OpenAPI Specification Suite", "Automated Docs Generator"]
    },
    {
        "id": "cand_34",
        "name": "Kiran Kumar Reddy",
        "role": "Network Automation Engineer",
        "bandwidth_status": "Available Immediately",
        "skills": ["Python", "Netmiko", "Ansible", "Cisco IOS", "BGP/OSPF", "Linux Shell Scripting"],
        "bio": "4 years automating software-defined networking configurations, routers, and data center switch fabrics.",
        "years_experience": 4,
        "past_projects": ["Software-Defined Network Automation", "Ansible Router Configuration Engine", "Data Center Switch Fabric Automation"]
    },
    {
        "id": "cand_35",
        "name": "Zoya Akhtar",
        "role": "Creative Technologist & Prototyper",
        "bandwidth_status": "Part-time bandwidth (50%)",
        "skills": ["Python", "Streamlit", "Three.js", "JavaScript", "Rapid Prototyping", "API Integration"],
        "bio": "3 years rapidly spinning up functional proof-of-concept demos and internal interactive tools for product validation.",
        "years_experience": 3,
        "past_projects": ["Interactive Product Prototype", "Three.js 3D Web Visualizer", "Streamlit Internal Tooling"]
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
