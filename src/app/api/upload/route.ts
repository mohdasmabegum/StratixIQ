import { NextResponse } from "next/server";
import { addCandidateToPool } from "@/lib/rag-engine";

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const name = formData.get("candidate_name") as string;
    const role = formData.get("role") as string || "Software Engineer";
    const bandwidthStatus = (formData.get("bandwidth_status") as any) || "Available Immediately";
    const bio = formData.get("bio") as string || "Experienced technical professional.";
    const skillsString = formData.get("skills") as string || "Python, React, Data Analysis";

    if (!name || !name.trim()) {
      return NextResponse.json(
        { error: "Candidate name is required" },
        { status: 400 }
      );
    }

    const skills = skillsString.split(",").map(s => s.trim()).filter(Boolean);

    const newCandidate = addCandidateToPool({
      name,
      role,
      bandwidthStatus,
      bio,
      skills,
      yearsExperience: 5,
      pastProjects: ["Enterprise Profile Ingestion"]
    });

    return NextResponse.json({
      success: true,
      message: `Successfully indexed profile for ${name}`,
      candidate: newCandidate
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to process candidate upload" },
      { status: 500 }
    );
  }
}
