from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
from utils import extract_text_from_pdf, store_instance

app = FastAPI(
    title="StratixIQ Talent Matching API",
    description="Agile Talent Deployment & Skill-Matching Engine API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CandidateMatchResult(BaseModel):
    candidate_name: str
    match_percentage: int = Field(..., ge=0, le=100, description="Match score from 0 to 100")
    verified_skills: List[str]
    skill_gaps: List[str]
    bandwidth_status: str = Field(..., description="Availability e.g., 'Available Immediately', 'Assigned until next month'")
    deployment_rationale: str

class MatchRequest(BaseModel):
    project_description: str
    top_k: Optional[int] = 5

@app.get("/")
def read_root():
    return {"status": "online", "service": "StratixIQ API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "vector_documents_count": len(store_instance.documents)}

@app.post("/upload-profile")
async def upload_profile(
    candidate_name: str = Form(...),
    bandwidth_status: str = Form("Available Immediately"),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    contents = await file.read()
    raw_text = extract_text_from_pdf(contents)
    
    metadata = {
        "candidate_name": candidate_name,
        "bandwidth_status": bandwidth_status
    }
    
    store_instance.add_profile(candidate_name, raw_text, metadata)
    
    return {
        "message": f"Successfully indexed profile for {candidate_name}",
        "extracted_character_count": len(raw_text),
        "status": "indexed"
    }

@app.post("/match-talent", response_model=List[CandidateMatchResult])
def match_talent(payload: MatchRequest):
    if not payload.project_description.strip():
        raise HTTPException(status_code=400, detail="Project description cannot be empty")
    
    results = store_instance.search(payload.project_description, top_k=payload.top_k)
    
    matches = []
    seen_candidates = set()
    
    for item in results:
        doc = item["doc"]
        c_name = doc["candidate_name"]
        if c_name in seen_candidates:
            continue
        seen_candidates.add(c_name)
        
        # Calculate dynamic mock score based on text similarity score
        score = min(98, max(65, int(item["score"] * 100) + 70))
        
        matches.append(CandidateMatchResult(
            candidate_name=c_name,
            match_percentage=score,
            verified_skills=["Python", "FastAPI", "Vector DB", "RAG"],
            skill_gaps=["Kubernetes"],
            bandwidth_status=doc["metadata"].get("bandwidth_status", "Available Immediately"),
            deployment_rationale=f"{c_name} exhibits strong alignment with project technical requirements and vector retrieval query."
        ))
        
    return matches

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
