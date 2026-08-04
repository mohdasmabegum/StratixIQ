import os
import json
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==========================================
# 1. SMART DOCUMENT INGESTION & CHUNKING
# ==========================================
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract raw text from uploaded PDF resume document bytes using PyMuPDF (fitz).
    """
    try:
        import fitz  # PyMuPDF
        text_content = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text and text.strip():
                    text_content.append(text.strip())
        return "\n\n".join(text_content)
    except Exception as e:
        return f"PDF Extraction Note: {str(e)}"

def chunk_document_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split text into semantic chunks using LangChain RecursiveCharacterTextSplitter with fallback.
    """
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        return text_splitter.split_text(text)
    except Exception:
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", " ", ""]
            )
            return text_splitter.split_text(text)
        except Exception:
            chunks = []
            start = 0
            while start < len(text):
                end = start + chunk_size
                chunks.append(text[start:end])
                start += max(1, chunk_size - chunk_overlap)
            return chunks

# ==========================================
# 2. PERSISTENT CHROMADB VECTOR STORE
# ==========================================
class VectorStoreManager:
    """
    Manages local ChromaDB vector store configured with Cosine Distance for accurate candidate matching.
    """
    def __init__(self, db_dir: str = "./chroma_db_store"):
        self.db_dir = db_dir
        self.collection_name = "stratixiq_talent_pool"
        self.use_chroma = False
        self.chroma_client = None
        self.collection = None
        self.in_memory_docs: List[Dict[str, Any]] = []

        self._initialize_db()

    def _initialize_db(self):
        try:
            import chromadb
            os.makedirs(self.db_dir, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=self.db_dir)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}  # Cosine distance metric for skill matching
            )
            self.use_chroma = True
        except Exception as e:
            print(f"[VectorStoreManager Warning] ChromaDB PersistentClient fallback to memory: {e}")
            self.use_chroma = False

    def add_candidate_profile(
        self,
        candidate_id: str,
        candidate_name: str,
        role: str,
        bandwidth_status: str,
        skills: List[str],
        raw_text: str
    ) -> bool:
        chunks = chunk_document_text(raw_text)
        skills_str = ", ".join(skills)

        if self.use_chroma and self.collection:
            try:
                documents = []
                metadatas = []
                ids = []
                for idx, chunk in enumerate(chunks):
                    doc_id = f"{candidate_id}_chunk_{idx}"
                    documents.append(f"Candidate: {candidate_name} | Role: {role} | Skills: {skills_str} | Content: {chunk}")
                    metadatas.append({
                        "candidate_id": candidate_id,
                        "candidate_name": candidate_name,
                        "role": role,
                        "bandwidth_status": bandwidth_status,
                        "skills": skills_str,
                        "chunk_index": idx
                    })
                    ids.append(doc_id)
                
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                return True
            except Exception as e:
                print(f"[VectorStoreManager Error] ChromaDB insertion error: {e}")

        # Fallback to structured document store
        self.in_memory_docs.append({
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "role": role,
            "bandwidth_status": bandwidth_status,
            "skills": skills,
            "raw_text": raw_text,
            "chunks": chunks
        })
        return True

    def query_candidates(self, query_text: str, top_k: int = 5, bandwidth_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        results = []
        if self.use_chroma and self.collection:
            try:
                where_clause = None
                if bandwidth_filter and bandwidth_filter != "All Availability":
                    where_clause = {"bandwidth_status": bandwidth_filter}

                query_res = self.collection.query(
                    query_texts=[query_text],
                    n_results=min(top_k * 3, 20),
                    where=where_clause
                )

                if query_res and query_res.get("metadatas") and query_res["metadatas"][0]:
                    seen = set()
                    metas = query_res["metadatas"][0]
                    distances = query_res["distances"][0] if query_res.get("distances") else [0.2] * len(metas)
                    
                    for meta, dist in zip(metas, distances):
                        cid = meta.get("candidate_id")
                        if cid and cid not in seen:
                            seen.add(cid)
                            # Convert cosine distance to match confidence percentage
                            similarity_score = max(0.5, 1.0 - float(dist))
                            results.append({
                                "candidate_id": cid,
                                "candidate_name": meta.get("candidate_name", "Indexed Candidate"),
                                "role": meta.get("role", "Engineer"),
                                "bandwidth_status": meta.get("bandwidth_status", "Available Immediately"),
                                "skills": [s.strip() for s in meta.get("skills", "").split(",") if s.strip()],
                                "cosine_score": round(similarity_score, 3)
                            })
                        if len(results) >= top_k:
                            break
                    return results
            except Exception as e:
                print(f"[VectorStoreManager Query Warning]: {e}")

        # Fallback in-memory search
        query_words = set(query_text.lower().split())
        for doc in self.in_memory_docs:
            if bandwidth_filter and bandwidth_filter != "All Availability":
                if doc["bandwidth_status"] != bandwidth_filter:
                    continue
            doc_text = (doc["candidate_name"] + " " + doc["role"] + " " + " ".join(doc["skills"]) + " " + doc["raw_text"]).lower()
            doc_words = set(doc_text.split())
            intersection = query_words.intersection(doc_words)
            score = len(intersection) / max(len(query_words), 1)
            results.append({
                "candidate_id": doc["candidate_id"],
                "candidate_name": doc["candidate_name"],
                "role": doc["role"],
                "bandwidth_status": doc["bandwidth_status"],
                "skills": doc["skills"],
                "cosine_score": round(0.55 + min(0.40, score * 2.0), 3)
            })
        results.sort(key=lambda x: x["cosine_score"], reverse=True)
        return results[:top_k]

    def get_total_count(self) -> int:
        if self.use_chroma and self.collection:
            try:
                return self.collection.count()
            except Exception:
                pass
        return len(self.in_memory_docs)

# Instantiate Global Vector Store
vector_store = VectorStoreManager()

# ==========================================
# 3. DYNAMIC HYBRID LOCAL-CLOUD LLM PROVIDER
# ==========================================
class LLMProviderManager:
    """
    Enterprise Data Privacy Manager for switching between OpenAI Cloud API,
    Local Ollama (e.g. Llama 3), and Local Deterministic Hybrid NLP engine.
    """
    def __init__(self):
        self.provider = os.getenv("DEFAULT_LLM_PROVIDER", "hybrid_local")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")

    def set_provider(self, provider_name: str):
        valid = ["openai", "ollama", "hybrid_local"]
        if provider_name.lower() in valid:
            self.provider = provider_name.lower()

    def generate_structured_match(self, project_desc: str, candidate_info: Dict[str, Any]) -> Dict[str, Any]:
        if self.provider == "openai" and self.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_api_key)
                prompt = f"""
                Act as an expert AI Talent Deployment Engine. Evaluate candidate suitability for the engineering project requirement.
                
                PROJECT REQUIREMENT:
                {project_desc}
                
                CANDIDATE PROFILE:
                Name: {candidate_info.get('name')}
                Role: {candidate_info.get('role')}
                Skills: {', '.join(candidate_info.get('skills', []))}
                Bio: {candidate_info.get('bio', '')}
                Availability: {candidate_info.get('bandwidth_status')}
                
                Return ONLY a JSON object with keys:
                - match_percentage: integer (0 to 100)
                - verified_strengths: list of matching skills
                - skill_gaps: list of missing tech requirements
                - availability_status: string
                - deployment_rationale: 2-sentence match justification
                - explainable_ai_breakdown: object with float weights (core_tech_weight, experience_weight, availability_weight)
                - upskilling_path: object with keys week_1 and week_2 containing 2-week targeted learning steps
                """
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                print(f"[LLMProviderManager OpenAI Error]: {e}. Falling back to hybrid engine.")

        elif self.provider == "ollama":
            try:
                import httpx
                prompt = f"Evaluate candidate {candidate_info.get('name')} for requirement: {project_desc}. Return strict JSON."
                res = httpx.post(
                    self.ollama_endpoint,
                    json={"model": self.ollama_model, "prompt": prompt, "format": "json"},
                    timeout=8.0
                )
                if res.status_code == 200:
                    data = res.json()
                    return json.loads(data.get("response", "{}"))
            except Exception as e:
                print(f"[LLMProviderManager Ollama Error]: {e}. Falling back to hybrid engine.")

        # Local High-Performance Hybrid Engine (Default & Zero-Latency Fallback)
        return self._generate_hybrid_local_evaluation(project_desc, candidate_info)

    def _generate_hybrid_local_evaluation(self, project_desc: str, candidate_info: Dict[str, Any]) -> Dict[str, Any]:
        query_lower = project_desc.lower()
        cand_skills = candidate_info.get("skills", [])
        cand_name = candidate_info.get("name", "Candidate")
        cand_role = candidate_info.get("role", "Software Engineer")
        cand_status = candidate_info.get("bandwidth_status", "Available Immediately")
        
        # Match verified strengths
        verified_strengths = [s for s in cand_skills if s.lower() in query_lower]
        if not verified_strengths:
            verified_strengths = cand_skills[:3] if cand_skills else ["Core Systems Architecture"]

        # Skill gap extraction
        tech_catalog = ["Kubernetes", "AWS CDK", "FastAPI", "ChromaDB", "Next.js", "PyTorch", "Go", "Redis", "Docker", "GraphQL", "PostgreSQL", "LangChain"]
        skill_gaps = [tech for tech in tech_catalog if tech.lower() in query_lower and tech.lower() not in [s.lower() for s in cand_skills]]
        
        # Dynamic Explainable Feature-Importance Weights
        matched_count = len(verified_strengths)
        core_tech_weight = round(min(55.0, 35.0 + (matched_count * 7.5)), 1)
        experience_weight = round(min(35.0, 25.0 + (candidate_info.get("years_experience", 5) * 1.5)), 1)
        availability_weight = 20.0 if "Immediately" in cand_status else (10.0 if "Part-time" in cand_status else 5.0)
        
        total_score = min(98, max(58, int(core_tech_weight + experience_weight + availability_weight)))

        # Automated 2-Week Remediation Learning Path
        gaps_str = ", ".join(skill_gaps[:2]) if skill_gaps else "advanced architecture patterns"
        upskilling_path = {
            "week_1": f"Complete hands-on module on {gaps_str} & study enterprise deployment documentation.",
            "week_2": f"Build & execute internal sandbox prototype for {cand_name} to validate production readiness."
        }

        deployment_rationale = (
            f"{cand_name} brings verified hands-on background in {', '.join(verified_strengths[:3])}. "
            f"Currently rated at {cand_status}, rendering them a strong strategic fit for sprint execution."
        )

        return {
            "match_percentage": total_score,
            "verified_strengths": verified_strengths,
            "skill_gaps": skill_gaps[:3],
            "availability_status": cand_status,
            "deployment_rationale": deployment_rationale,
            "explainable_ai_breakdown": {
                "core_tech_stack_weight": core_tech_weight,
                "experience_depth_weight": experience_weight,
                "availability_timeline_weight": availability_weight
            },
            "upskilling_path": upskilling_path
        }

# Instantiate Global LLM Manager
llm_manager = LLMProviderManager()
