import { type NextRequest, NextResponse } from "next/server"

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000"

export async function GET(request: NextRequest, { params }: { params: { jobId: string; format: string } }) {
  try {
    const { jobId, format } = params

    if (!["json", "csv"].includes(format)) {
      return NextResponse.json({ error: "Invalid format. Use 'json' or 'csv'" }, { status: 400 })
    }

    // Get export from Python API
    const response = await fetch(`${PYTHON_API_URL}/export/${jobId}/${format}`, {
      method: "GET",
    })

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json({ error: "Job not found" }, { status: 404 })
      }
      throw new Error("Failed to export data")
    }

    const contentType = format === "json" ? "application/json" : "text/csv"
    const fileExtension = format === "json" ? "json" : "csv"

    const data = await response.text()

    return new Response(data, {
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": `attachment; filename=scrape_results_${jobId}.${fileExtension}`,
      },
    })
  } catch (error) {
    console.error("Export error:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to export data" },
      { status: 500 },
    )
  }
}
