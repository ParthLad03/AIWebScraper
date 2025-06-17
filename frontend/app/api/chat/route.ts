import { streamText } from "ai"
import { google } from "@ai-sdk/google"

export const maxDuration = 30

export async function POST(req: Request) {
  try {
    const body = await req.json()
    const { messages, scrapedContent } = body

    console.log("Chat API called with:", {
      messagesCount: messages?.length || 0,
      hasScrapedContent: !!scrapedContent,
      scrapedContentLength: scrapedContent?.length || 0,
    })

    // Validate required data
    if (!messages || !Array.isArray(messages)) {
      console.error("Invalid messages format")
      return new Response(JSON.stringify({ error: "Invalid messages format" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      })
    }

    const systemPrompt = scrapedContent
      ? `You are a helpful AI assistant that can answer questions about the following scraped web content. Use this content to provide accurate and detailed responses.

SCRAPED CONTENT:
${scrapedContent}

Instructions:
- Answer questions based on the scraped content above
- If the question cannot be answered from the content, say so clearly
- Provide specific details and examples from the content when relevant
- Be concise but comprehensive in your responses`
      : `You are a helpful AI assistant. However, no web content has been provided for you to analyze. Please ask the user to scrape a website first before asking questions about its content.`

    console.log("System prompt created, length:", systemPrompt.length)

    // Check if API key is available
    if (!process.env.GOOGLE_GENERATIVE_AI_API_KEY) {
      console.error("Missing GOOGLE_GENERATIVE_AI_API_KEY")
      return new Response(JSON.stringify({ error: "AI service not configured" }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      })
    }

    const result = streamText({
      model: google("gemini-2.0-flash-exp"),
      system: systemPrompt,
      messages,
      temperature: 0.7,
      maxTokens: 1000,
    })

    console.log("Streaming response initiated successfully")
    return result.toDataStreamResponse()
  } catch (error) {
    console.error("Chat API error:", error)

    // Return a proper error response
    const errorMessage = error instanceof Error ? error.message : "Internal Server Error"
    return new Response(
      JSON.stringify({
        error: errorMessage,
        details: error instanceof Error ? error.stack : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      },
    )
  }
}
