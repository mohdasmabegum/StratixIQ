export interface CandidateProfile {
  id: string;
  name: string;
  role: string;
  bandwidthStatus: "Available Immediately" | "Assigned until next month" | "Part-time bandwidth";
  skills: string[];
  bio: string;
  yearsExperience: number;
  pastProjects: string[];
}

export interface MatchResult {
  candidate: CandidateProfile;
  matchScore: number; // 0 - 100
  verifiedSkills: string[];
  skillGaps: string[];
  deploymentRationale: string;
}

export const INITIAL_TALENT_POOL: CandidateProfile[] = [
  {
    id: "cand_1",
    name: "Alex Rivera",
    role: "Senior AI & Full-Stack Engineer",
    bandwidthStatus: "Available Immediately",
    skills: ["Python", "FastAPI", "ChromaDB", "LangChain", "OpenAI", "React", "Next.js", "PostgreSQL", "Docker"],
    bio: "Specializes in building distributed RAG pipelines, FastAPI microservices, and vector search systems with high query throughput.",
    yearsExperience: 7,
    pastProjects: ["Enterprise Knowledge RAG Engine", "FastAPI Microservices Platform", "Real-Time AI Copilot"]
  },
  {
    id: "cand_2",
    name: "Elena Rostova",
    role: "Machine Learning & Data Architect",
    bandwidthStatus: "Part-time bandwidth",
    skills: ["Python", "PyTorch", "HuggingFace", "LangChain", "PostgreSQL", "MLOps", "Kubernetes", "Vector DB"],
    bio: "Passionate about fine-tuning open-source LLMs, embeddings optimization, and scalable vector indexing.",
    yearsExperience: 6,
    pastProjects: ["LLM Fine-Tuning Suite", "High-Scale Vector Store Indexing", "Predictive Analytics Engine"]
  },
  {
    id: "cand_3",
    name: "Marcus Vance",
    role: "Cloud DevOps & Platform Engineer",
    bandwidthStatus: "Available Immediately",
    skills: ["AWS CDK", "Terraform", "Kubernetes", "Docker", "Python", "FastAPI", "CI/CD", "Monitoring"],
    bio: "Focuses on cloud infrastructure automation, container orchestration, zero-downtime deployments, and API security.",
    yearsExperience: 8,
    pastProjects: ["AWS Infrastructure Automation", "Multi-Tenant Kubernetes Cluster", "CI/CD Pipeline Engine"]
  },
  {
    id: "cand_4",
    name: "Sophia Chen",
    role: "Lead UI/UX Systems Designer & Frontend Dev",
    bandwidthStatus: "Assigned until next month",
    skills: ["TypeScript", "React", "Next.js", "Tailwind CSS", "Framer Motion", "UI/UX Design Systems", "GraphQL"],
    bio: "Expert in crafting high-impact glassmorphic user interfaces, design systems, and responsive web applications.",
    yearsExperience: 5,
    pastProjects: ["Design System Refactor", "Enterprise Analytics Dashboard", "Responsive PWA"]
  },
  {
    id: "cand_5",
    name: "David Kim",
    role: "Backend & Database Engineer",
    bandwidthStatus: "Available Immediately",
    skills: ["Python", "Go", "PostgreSQL", "Redis", "FastAPI", "REST APIs", "gRPC", "Vector Search"],
    bio: "Specializes in database query optimization, Redis caching, low-latency microservice architectures, and data pipelines.",
    yearsExperience: 6,
    pastProjects: ["High-Throughput Data Ingestion", "Redis Vector Cache", "PostgreSQL Sharding System"]
  }
];

let activeTalentPool: CandidateProfile[] = [...INITIAL_TALENT_POOL];

export function getTalentPool(): CandidateProfile[] {
  return activeTalentPool;
}

export function addCandidateToPool(profile: Omit<CandidateProfile, "id">): CandidateProfile {
  const newCandidate: CandidateProfile = {
    ...profile,
    id: `cand_${Date.now()}`
  };
  activeTalentPool.unshift(newCandidate);
  return newCandidate;
}

export function matchTalentAgainstRequirement(projectDescription: str): MatchResult[] {
  const queryLower = projectDescription.toLowerCase();
  const words = queryLower.split(/\W+/).filter(w => w.length > 2);

  const results: MatchResult[] = activeTalentPool.map(candidate => {
    const candidateText = [
      candidate.role,
      candidate.bio,
      ...candidate.skills,
      ...candidate.pastProjects
    ].join(" ").toLowerCase();

    let matchedSkillCount = 0;
    const verifiedSkills: string[] = [];
    const skillGaps: string[] = [];

    candidate.skills.forEach(skill => {
      if (queryLower.includes(skill.toLowerCase())) {
        matchedSkillCount++;
        verifiedSkills.push(skill);
      }
    });

    // Extract potential required keywords that candidate might be missing
    const techKeywords = ["kubernetes", "aws cdk", "fastapi", "chromadb", "next.js", "pytorch", "go", "redis", "docker", "graphql"];
    techKeywords.forEach(keyword => {
      if (queryLower.includes(keyword) && !candidate.skills.map(s => s.toLowerCase()).includes(keyword)) {
        if (!skillGaps.includes(keyword.toUpperCase())) {
          skillGaps.push(keyword.toUpperCase());
        }
      }
    });

    let wordMatchCount = 0;
    words.forEach(w => {
      if (candidateText.includes(w)) wordMatchCount++;
    });

    // Score calculation algorithm
    const baseScore = Math.min(60, wordMatchCount * 5);
    const skillBonus = verifiedSkills.length * 12;
    const rawScore = 35 + baseScore + skillBonus;
    const matchScore = Math.min(99, Math.max(52, rawScore));

    const rationale = `${candidate.name} is a ${candidate.role} with verified expertise in ${
      verifiedSkills.length > 0 ? verifiedSkills.slice(0, 3).join(", ") : "core engineering domains"
    }. ${
      candidate.bandwidthStatus === "Available Immediately" 
        ? "Fully available for immediate agile sprint deployment." 
        : `Currently rated at ${candidate.bandwidthStatus.toLowerCase()}.`
    }`;

    return {
      candidate,
      matchScore,
      verifiedSkills: verifiedSkills.length > 0 ? verifiedSkills : candidate.skills.slice(0, 3),
      skillGaps: skillGaps.slice(0, 3),
      deploymentRationale: rationale
    };
  });

  return results.sort((a, b) => b.matchScore - a.matchScore);
}
