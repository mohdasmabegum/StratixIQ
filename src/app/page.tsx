"use client";

import React, { useState, useEffect } from "react";
import { 
  Zap, 
  UploadCloud, 
  Users, 
  Search, 
  CheckCircle2, 
  AlertTriangle, 
  Sparkles, 
  BrainCircuit, 
  Briefcase, 
  Clock, 
  FileText,
  Send,
  Layers,
  ShieldCheck,
  ChevronRight
} from "lucide-react";
import { INITIAL_TALENT_POOL, CandidateProfile, MatchResult } from "@/lib/rag-engine";

export default function StratixIQDashboard() {
  const [activeTab, setActiveTab] = useState<"match" | "upload" | "roster">("match");
  const [talentPool, setTalentPool] = useState<CandidateProfile[]>(INITIAL_TALENT_POOL);
  
  // Matching Engine State
  const [projectDescription, setProjectDescription] = useState("");
  const [bandwidthFilter, setBandwidthFilter] = useState<string>("ALL");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<MatchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  // Upload Form State
  const [candidateName, setCandidateName] = useState("");
  const [candidateRole, setCandidateRole] = useState("");
  const [candidateBandwidth, setCandidateBandwidth] = useState<CandidateProfile["bandwidthStatus"]>("Available Immediately");
  const [candidateSkills, setCandidateSkills] = useState("");
  const [candidateBio, setCandidateBio] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Roster Search State
  const [rosterSearchQuery, setRosterSearchQuery] = useState("");

  const samplePrompts = [
    "Need a Senior Full-Stack Engineer with Python, FastAPI, ChromaDB vector store, and React for immediate sprint deployment.",
    "Looking for a Machine Learning Architect experienced in PyTorch, LangChain LLM fine-tuning, and vector database indexing.",
    "Require a Cloud DevOps Engineer with AWS CDK, Kubernetes, Docker, and CI/CD automation background."
  ];

  const handleRunMatch = async () => {
    if (!projectDescription.trim()) return;
    setIsSearching(true);
    setHasSearched(true);

    try {
      const res = await fetch("/api/match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ project_description: projectDescription })
      });
      const data = await res.json();
      if (data.matches) {
        setSearchResults(data.matches);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleUploadProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!candidateName.trim()) return;

    const formData = new FormData();
    formData.append("candidate_name", candidateName);
    formData.append("role", candidateRole || "Software Engineer");
    formData.append("bandwidth_status", candidateBandwidth);
    formData.append("skills", candidateSkills);
    formData.append("bio", candidateBio);

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (data.success && data.candidate) {
        setTalentPool(prev => [data.candidate, ...prev]);
        setUploadSuccess(true);
        setCandidateName("");
        setCandidateRole("");
        setCandidateSkills("");
        setCandidateBio("");
        setTimeout(() => setUploadSuccess(false), 4000);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const filteredMatches = searchResults.filter(match => {
    if (bandwidthFilter === "ALL") return true;
    return match.candidate.bandwidthStatus === bandwidthFilter;
  });

  const filteredRoster = talentPool.filter(candidate => {
    if (!rosterSearchQuery.trim()) return true;
    const q = rosterSearchQuery.toLowerCase();
    return (
      candidate.name.toLowerCase().includes(q) ||
      candidate.role.toLowerCase().includes(q) ||
      candidate.skills.some(s => s.toLowerCase().includes(q))
    );
  });

  return (
    <div className="min-h-screen flex flex-col max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Top Header */}
      <header className="glass-panel p-5 mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-blue-600/20 border border-blue-500/30 rounded-xl text-blue-400">
            <Zap className="w-7 h-7 text-blue-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-blue-400 bg-clip-text text-transparent">
                StratixIQ
              </h1>
              <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                v1.0 Enterprise
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Agile Talent Deployment & Skill-Matching Vector RAG Engine
            </p>
          </div>
        </div>

        {/* Live System Metrics */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div className="px-3 py-2 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center space-x-2">
            <Users className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-300">Indexed Talent:</span>
            <span className="font-semibold text-white">{talentPool.length} Profiles</span>
          </div>

          <div className="px-3 py-2 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            <span className="text-slate-300">Vector Store:</span>
            <span className="font-semibold text-emerald-400">Active</span>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="flex space-x-2 border-b border-slate-800 pb-4 mb-6 overflow-x-auto">
        <button
          onClick={() => setActiveTab("match")}
          className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all whitespace-nowrap ${
            activeTab === "match"
              ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <BrainCircuit className="w-4 h-4" />
          <span>Project Staffing Engine</span>
        </button>

        <button
          onClick={() => setActiveTab("upload")}
          className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all whitespace-nowrap ${
            activeTab === "upload"
              ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          <span>Ingest Candidate Resume</span>
        </button>

        <button
          onClick={() => setActiveTab("roster")}
          className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all whitespace-nowrap ${
            activeTab === "roster"
              ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Talent Pool Roster ({talentPool.length})</span>
        </button>
      </nav>

      {/* TAB 1: PROJECT STAFFING ENGINE */}
      {activeTab === "match" && (
        <div className="space-y-6">
          <div className="glass-panel p-6">
            <label className="block text-sm font-semibold text-slate-200 mb-2 flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-blue-400" />
                <span>Project Description & Skill Requirements</span>
              </span>
              <span className="text-xs text-slate-400">Natural Language RAG Query</span>
            </label>

            {/* Pre-loader Prompts */}
            <div className="flex flex-wrap gap-2 mb-3">
              <span className="text-xs text-slate-400 self-center">Sample Prompts:</span>
              {samplePrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => setProjectDescription(prompt)}
                  className="text-xs px-2.5 py-1 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                >
                  Prompt #{idx + 1}
                </button>
              ))}
            </div>

            <textarea
              rows={4}
              value={projectDescription}
              onChange={(e) => setProjectDescription(e.target.value)}
              placeholder="Paste engineering manager project requirements (e.g., 'Need a senior engineer with FastAPI, PostgreSQL, vector database experience, and LLM fine-tuning background...')"
              className="w-full p-4 rounded-xl bg-slate-900/90 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm transition"
            />

            <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              {/* Bandwidth Status Filter */}
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-400 font-medium">Availability Filter:</span>
                <select
                  value={bandwidthFilter}
                  onChange={(e) => setBandwidthFilter(e.target.value)}
                  className="bg-slate-900 border border-slate-700 text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none text-xs"
                >
                  <option value="ALL">All Availability</option>
                  <option value="Available Immediately">Available Immediately</option>
                  <option value="Part-time bandwidth">Part-time bandwidth</option>
                  <option value="Assigned until next month">Assigned until next month</option>
                </select>
              </div>

              <button
                onClick={handleRunMatch}
                disabled={isSearching || !projectDescription.trim()}
                className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-sm shadow-lg shadow-blue-500/25 disabled:opacity-50 transition"
              >
                {isSearching ? (
                  <>
                    <BrainCircuit className="w-4 h-4 animate-spin" />
                    <span>Evaluating Vector Embeddings...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    <span>Run Semantic Talent Search</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Search Results Display */}
          {hasSearched && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                  <span>Ranked Candidate Shortlist & Skill-Gap Analysis</span>
                </h2>
                <span className="text-xs text-slate-400">
                  {filteredMatches.length} Matches Found
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredMatches.map((res, index) => {
                  const candidate = res.candidate;
                  const isTopMatch = index === 0;

                  let badgeClass = "badge-available";
                  if (candidate.bandwidthStatus === "Assigned until next month") badgeClass = "badge-assigned";
                  if (candidate.bandwidthStatus === "Part-time bandwidth") badgeClass = "badge-part-time";

                  return (
                    <div 
                      key={candidate.id} 
                      className={`glass-card p-5 relative overflow-hidden flex flex-col justify-between ${
                        isTopMatch ? "ring-1 ring-blue-500/50" : ""
                      }`}
                    >
                      {isTopMatch && (
                        <div className="absolute top-0 right-0 bg-blue-600 text-white text-[10px] uppercase font-bold px-3 py-1 rounded-bl-lg shadow-md">
                          Top Match
                        </div>
                      )}

                      <div>
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                              <span>{candidate.name}</span>
                            </h3>
                            <p className="text-xs text-slate-400">{candidate.role} • {candidate.yearsExperience} yrs exp</p>
                          </div>
                          
                          {/* Score Gauge */}
                          <div className="flex flex-col items-end">
                            <span className="text-2xl font-extrabold text-blue-400 tracking-tight">
                              {res.matchScore}%
                            </span>
                            <span className="text-[10px] text-slate-400 font-medium uppercase">Match Score</span>
                          </div>
                        </div>

                        {/* Availability Status Badge */}
                        <div className="mb-4">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium ${badgeClass}`}>
                            <Clock className="w-3 h-3 mr-1.5" />
                            {candidate.bandwidthStatus}
                          </span>
                        </div>

                        {/* Verified Skills */}
                        <div className="mb-3">
                          <span className="text-xs font-semibold text-slate-300 block mb-1.5">Verified Matching Skills:</span>
                          <div className="flex flex-wrap gap-1.5">
                            {res.verifiedSkills.map((skill, i) => (
                              <span key={i} className="px-2 py-0.5 text-xs rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/50 font-medium">
                                ✓ {skill}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Skill Gaps */}
                        {res.skillGaps.length > 0 && (
                          <div className="mb-4">
                            <span className="text-xs font-semibold text-slate-300 block mb-1.5">Potential Skill Gaps:</span>
                            <div className="flex flex-wrap gap-1.5">
                              {res.skillGaps.map((gap, i) => (
                                <span key={i} className="px-2 py-0.5 text-xs rounded bg-amber-950/60 text-amber-300 border border-amber-800/50">
                                  ! {gap}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Rationale */}
                        <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 mb-4">
                          <span className="font-semibold text-slate-200 block mb-1">Strategic Deployment Rationale:</span>
                          {res.deploymentRationale}
                        </div>
                      </div>

                      <button
                        onClick={() => alert(`Assigned ${candidate.name} to project allocation queue!`)}
                        className="w-full py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium text-xs flex items-center justify-center space-x-1.5 transition"
                      >
                        <span>Deploy Candidate to Sprint</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: INGEST CANDIDATE RESUME */}
      {activeTab === "upload" && (
        <div className="max-w-2xl mx-auto w-full">
          <div className="glass-panel p-6">
            <h2 className="text-xl font-bold text-white mb-1 flex items-center space-x-2">
              <UploadCloud className="w-5 h-5 text-blue-400" />
              <span>Ingest Employee Resume & Profile</span>
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              Parse candidate PDF documents into chunked vector embeddings for immediate vector search retrieval.
            </p>

            {uploadSuccess && (
              <div className="p-4 mb-6 rounded-xl bg-emerald-950/80 border border-emerald-500/30 text-emerald-300 text-sm flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
                <span>Successfully indexed profile into ChromaDB vector store!</span>
              </div>
            )}

            <form onSubmit={handleUploadProfile} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Candidate Full Name *</label>
                <input
                  type="text"
                  required
                  value={candidateName}
                  onChange={(e) => setCandidateName(e.target.value)}
                  placeholder="e.g. Sarah Connor"
                  className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Role / Job Title</label>
                <input
                  type="text"
                  value={candidateRole}
                  onChange={(e) => setCandidateRole(e.target.value)}
                  placeholder="e.g. Senior AI Systems Engineer"
                  className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Current Availability Bandwidth *</label>
                <select
                  value={candidateBandwidth}
                  onChange={(e) => setCandidateBandwidth(e.target.value as any)}
                  className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 text-sm focus:outline-none focus:border-blue-500"
                >
                  <option value="Available Immediately">Available Immediately</option>
                  <option value="Part-time bandwidth">Part-time bandwidth (50%)</option>
                  <option value="Assigned until next month">Assigned until next month</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Key Technical Skills (Comma-separated)</label>
                <input
                  type="text"
                  value={candidateSkills}
                  onChange={(e) => setCandidateSkills(e.target.value)}
                  placeholder="e.g. Python, FastAPI, PyMuPDF, ChromaDB, Docker"
                  className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Profile Bio / Background</label>
                <textarea
                  rows={3}
                  value={candidateBio}
                  onChange={(e) => setCandidateBio(e.target.value)}
                  placeholder="Brief summary of candidate experience and major projects..."
                  className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* PDF File Dropzone */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Resume PDF Upload (Optional mock dropzone)</label>
                <div className="border-2 border-dashed border-slate-700 hover:border-blue-500/50 rounded-xl p-6 text-center cursor-pointer transition">
                  <FileText className="w-8 h-8 mx-auto text-slate-500 mb-2" />
                  <p className="text-xs text-slate-400 font-medium">Click to select or drag PDF file here</p>
                  <p className="text-[10px] text-slate-500 mt-1">Supports PDF layout parsing up to 10MB</p>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-lg shadow-blue-600/30 transition flex items-center justify-center space-x-2"
              >
                <Send className="w-4 h-4" />
                <span>Index Profile into Vector Database</span>
              </button>
            </form>
          </div>
        </div>
      )}

      {/* TAB 3: TALENT POOL ROSTER */}
      {activeTab === "roster" && (
        <div className="space-y-6">
          <div className="glass-panel p-4 flex items-center justify-between flex-wrap gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="text"
                value={rosterSearchQuery}
                onChange={(e) => setRosterSearchQuery(e.target.value)}
                placeholder="Search talent by name, role, or skill..."
                className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500"
              />
            </div>

            <span className="text-xs text-slate-400">
              Showing {filteredRoster.length} of {talentPool.length} Total Candidates
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredRoster.map((candidate) => {
              let badgeClass = "badge-available";
              if (candidate.bandwidthStatus === "Assigned until next month") badgeClass = "badge-assigned";
              if (candidate.bandwidthStatus === "Part-time bandwidth") badgeClass = "badge-part-time";

              return (
                <div key={candidate.id} className="glass-card p-5 flex flex-col justify-between">
                  <div>
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-bold text-white text-base">{candidate.name}</h3>
                        <p className="text-xs text-blue-400">{candidate.role}</p>
                      </div>
                      <span className="text-xs text-slate-400 font-medium">{candidate.yearsExperience} yrs exp</span>
                    </div>

                    <div className="mb-3">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium ${badgeClass}`}>
                        {candidate.bandwidthStatus}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 mb-3 line-clamp-2">{candidate.bio}</p>

                    <div className="flex flex-wrap gap-1 mb-3">
                      {candidate.skills.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 text-[10px] rounded bg-slate-800 text-slate-300 border border-slate-700">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="border-t border-slate-800 pt-3 text-[11px] text-slate-400">
                    <span className="font-semibold text-slate-300 block mb-1">Past High-Impact Projects:</span>
                    <ul className="list-disc list-inside space-y-0.5 text-slate-400">
                      {candidate.pastProjects.map((p, idx) => (
                        <li key={idx} className="truncate">{p}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-auto pt-8 pb-4 text-center text-xs text-slate-500 border-t border-slate-800/60 mt-12">
        StratixIQ AI Agile Staffing Engine • Enterprise RAG & Vector Matching Engine
      </footer>
    </div>
  );
}
