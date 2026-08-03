# StratixIQ: AI-Driven Agile Talent Deployment & Skill-Matching Engine

![StratixIQ](https://img.shields.io/badge/StratixIQ-Enterprise%20AI-blue?style=for-the-badge)
![Vercel Ready](https://img.shields.io/badge/Vercel-Deployed-black?style=for-the-badge&logo=vercel)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=nextdotjs)
![Python](https://img.shields.io/badge/Python-FastAPI%20%7C%20Streamlit-3776AB?style=for-the-badge&logo=python)

**StratixIQ** is an enterprise-grade AI talent matching engine. Engineering managers input project requirements in natural language and retrieve a ranked candidate shortlist with match confidence scores (0–100%), verified skills, skill gap analysis, strategic deployment rationales, and real-time availability bandwidth badges.

---

## 🌟 Key Features

1. **Document Ingestion & Resume Parsing**:
   - Ingest candidate PDF resumes using layout extraction (`PyMuPDF`/`fitz`).
   - Split documents into semantic text chunks using `RecursiveCharacterTextSplitter`.

2. **RAG Vector Search & Matching Engine**:
   - High-dimensional vector space indexing.
   - Natural language project requirement matching via similarity search.

3. **Structured Scoring & Metrics**:
   - **Match Confidence** (0–100%).
   - **Verified Skills** (matching candidate skills).
   - **Skill Gap Analysis** (missing tech requirements).
   - **Deployment Rationale** (2-sentence strategic justification).

4. **Agile Bandwidth & Availability Status Badges**:
   - Track availability in real time: *Available Immediately*, *Assigned until next month*, *Part-time bandwidth*.

5. **Multi-Tab Dashboard (Web & Mobile)**:
   - **Tab 1**: Project Staffing Engine & RAG Candidate Shortlist.
   - **Tab 2**: Resume PDF Dropzone & Profile Ingestion.
   - **Tab 3**: Talent Pool Roster & Skill Matrix.

---

## 🚀 Dual Architecture & Tech Stack

### 1. Next.js 14 Full-Stack Production App (Vercel-Ready)
- **Framework**: Next.js 14 (App Router, TypeScript, React 18).
- **Styling**: Tailwind CSS + Custom Dark Glassmorphism CSS design system.
- **Serverless API Routes**: `/api/match` and `/api/upload`.
- **Deployment Target**: Vercel (Web & Mobile PWA ready).

### 2. Python RAG Engine (FastAPI + Streamlit + ChromaDB)
- **Backend API**: FastAPI (`backend.py`) with `/upload-profile` and `/match-talent` routes.
- **Frontend App**: Streamlit (`app.py`) multi-tab interactive app.
- **Vector DB**: ChromaDB local vector store.
- **Dependencies**: Listed in `requirements.txt`.

---

## ⚡ Deployment to Vercel (Web & Mobile App)

### Quick Vercel Deployment

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit of StratixIQ"
   git remote add origin https://github.com/mohdasmabegum/StratixIQ.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy on Vercel**:
   - Connect your GitHub account to [Vercel](https://vercel.com).
   - Import the repository `mohdasmabegum/StratixIQ`.
   - Vercel automatically detects Next.js framework configuration.
   - Click **Deploy**. Your app will be live with a production Vercel URL accessible on both Desktop and Mobile browsers!

---

## 💻 Local Running Guide

### Running Next.js Web App
```bash
npm install
npm run dev
# Open http://localhost:3000
```

### Running Python Streamlit / FastAPI
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI Backend (Terminal 1)
python backend.py

# Run Streamlit Frontend (Terminal 2)
streamlit run app.py
```

---

## 🔗 Repository Link
GitHub Repository: [https://github.com/mohdasmabegum/StratixIQ](https://github.com/mohdasmabegum/StratixIQ)
