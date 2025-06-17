import { type NextRequest, NextResponse } from "next/server"

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    const { url, maxPages = 5 } = await request.json()

    if (!url) {
      return NextResponse.json({ error: "URL is required" }, { status: 400 })
    }

    // Validate URL format
    try {
      new URL(url)
    } catch {
      return NextResponse.json({ error: "Invalid URL format" }, { status: 400 })
    }

    // Start scraping job with Python API
    const response = await fetch(`${PYTHON_API_URL}/scrape`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: url,
        max_pages: maxPages,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || "Failed to start scraping job")
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error("Scraping error:", error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to scrape URL" },
      { status: 500 },
    )
  }
}
