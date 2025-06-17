import { type NextRequest, NextResponse } from "next/server"

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000"

export async function GET(request: NextRequest, { params }: { params: { jobId: string } }) {
  try {
    const { jobId } = params

    // Get job status from Python API
    const response = await fetch(`${PYTHON_API_URL}/scrape/${jobId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json({ error: "Job not found" }, { status: 404 })
      }
      throw new Error("Failed to get job status")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Job status error:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to get job status" },
      { status: 500 },
    )
  }
}

export async function DELETE(request: NextRequest, { params }: { params: { jobId: string } }) {
  try {
    const { jobId } = params

    // Delete job from Python API
    const response = await fetch(`${PYTHON_API_URL}/scrape/${jobId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json({ error: "Job not found" }, { status: 404 })
      }
      throw new Error("Failed to delete job")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Job deletion error:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to delete job" },
      { status: 500 },
    )
  }
}
