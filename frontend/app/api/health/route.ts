import { NextResponse } from "next/server"

const PYTHON_API_URL = process.env.PYTHON_API_URL || "http://localhost:8000"

export async function GET() {
  try {
    // Check Python API health
    const pythonHealthResponse = await fetch(`${PYTHON_API_URL}/health`, {
      method: "GET",
    })

    let pythonHealth = null
    if (pythonHealthResponse.ok) {
      pythonHealth = await pythonHealthResponse.json()
    }

    // Check environment variables
    const hasGeminiKey = !!process.env.GOOGLE_GENERATIVE_AI_API_KEY
    const hasPythonUrl = !!process.env.PYTHON_API_URL

    const healthStatus = {
      status: pythonHealth ? "healthy" : "degraded",
      timestamp: new Date().toISOString(),
      services: {
        nextjs: {
          status: "healthy",
          message: "Next.js API is running",
        },
        python_api: {
          status: pythonHealth ? "healthy" : "unhealthy",
          message: pythonHealth ? "Python API is running" : "Python API is not accessible",
          details: pythonHealth,
        },
      },
      environment: {
        gemini_api_key: hasGeminiKey ? "configured" : "missing",
        python_api_url: hasPythonUrl ? "configured" : "using_default",
      },
      version: "2.0.0",
    }

    return NextResponse.json(healthStatus)
  } catch (error) {
    return NextResponse.json(
      {
        status: "unhealthy",
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : "Health check failed",
      },
      { status: 500 },
    )
  }
}
