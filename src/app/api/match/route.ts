import { NextResponse } from "next/server";
import { matchTalentAgainstRequirement } from "@/lib/rag-engine";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { project_description } = body;

    if (!project_description || typeof project_description !== "string" || !project_description.trim()) {
      return NextResponse.json(
        { error: "Project description is required" },
        { status: 400 }
      );
    }

    const matches = matchTalentAgainstRequirement(project_description);

    return NextResponse.json({
      success: true,
      query: project_description,
      total_candidates_evaluated: matches.length,
      matches
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to process match query" },
      { status: 500 }
    );
  }
}
