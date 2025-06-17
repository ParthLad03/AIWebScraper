"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import {
  Globe,
  MessageSquare,
  Loader2,
  CheckCircle,
  AlertCircle,
  Send,
  Copy,
  FileText,
  Trash2,
  TestTube,
  Sparkles,
  Link,
  BarChart3,
  FileDown,
} from "lucide-react"
import { useChat } from "@ai-sdk/react"

interface ScrapedData {
  url: string
  title: string
  content: string
  wordCount: number
  qualityScore: number
  timestamp: string
  importantLinks: Array<{
    url: string
    text: string
    reason?: string
  }>
  metadata: {
    description?: string
    keywords?: string[]
    pagesScraped?: number
    averageQualityScore?: number
    extractionMethod?: string
  }
  isTestScrape?: boolean
  customInstructionsApplied?: boolean
}

interface ProcessingStatus {
  stage: "idle" | "scraping" | "cleaning" | "complete" | "error"
  progress: number
  message: string
}

export default function EnhancedWebScraperChat() {
  const [url, setUrl] = useState("")
  const [customInstructions, setCustomInstructions] = useState("")
  const [scrapedData, setScrapedData] = useState<ScrapedData | null>(null)
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>({
    stage: "idle",
    progress: 0,
    message: "",
  })
  const [jobId, setJobId] = useState<string | null>(null)
  const [isTestMode, setIsTestMode] = useState(false)

  const { messages, input, handleInputChange, handleSubmit, isLoading, error } = useChat({
    api: "/api/chat",
    body: {
      scrapedContent: scrapedData?.content || "",
    },
    onError: (error) => {
      console.error("Chat error:", error)
    },
  })

  const handleScrapeUrl = async (testMode = false) => {
    if (!url.trim()) return

    setIsTestMode(testMode)
    setProcessingStatus({
      stage: "scraping",
      progress: 10,
      message: testMode ? "Starting test scrape..." : "Starting enhanced web scraping job...",
    })

    try {
      const endpoint = testMode ? "/api/test-scrape" : "/api/scrape"
      const payload = testMode
        ? { url, customInstructions: customInstructions || null }
        : { url, maxPages: 5, customInstructions: customInstructions || null }

      // Start scraping job
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || "Failed to start scraping job")
      }

      const { job_id } = await response.json()
      setJobId(job_id)

      // Poll for job status
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await fetch(`/api/scrape/${job_id}`)
          if (!statusResponse.ok) {
            throw new Error("Failed to get job status")
          }

          const statusData = await statusResponse.json()

          setProcessingStatus({
            stage:
              statusData.status === "completed" ? "complete" : statusData.status === "error" ? "error" : "scraping",
            progress: statusData.progress,
            message: statusData.message,
          })

          if (statusData.status === "completed" && statusData.result) {
            const result = statusData.result

            setScrapedData({
              url: result.url,
              title: result.title,
              content: result.cleanedContent || "",
              wordCount: result.wordCount || 0,
              qualityScore: result.qualityScore || 0,
              timestamp: new Date().toISOString(),
              importantLinks: result.importantLinks || [],
              metadata: {
                description: result.description,
                pagesScraped: result.pagesScraped || 1,
                averageQualityScore: result.qualityScore,
                extractionMethod: result.metadata?.extractionMethod || "enhanced",
              },
              isTestScrape: testMode,
              customInstructionsApplied: result.customInstructionsApplied || false,
            })
            clearInterval(pollInterval)
          } else if (statusData.status === "error") {
            setProcessingStatus({
              stage: "error",
              progress: 0,
              message: statusData.error || "Scraping failed",
            })
            clearInterval(pollInterval)
          }
        } catch (error) {
          console.error("Polling error:", error)
          setProcessingStatus({
            stage: "error",
            progress: 0,
            message: "Failed to get scraping status",
          })
          clearInterval(pollInterval)
        }
      }, 2000)

      // Clear interval after 5 minutes
      setTimeout(() => clearInterval(pollInterval), 300000)
    } catch (error) {
      console.error("Scraping error:", error)
      setProcessingStatus({
        stage: "error",
        progress: 0,
        message: error instanceof Error ? error.message : "Failed to start scraping job",
      })
    }
  }

  const handleDownload = async (format: "json" | "csv") => {
    if (!jobId) return

    try {
      const response = await fetch(`/api/export/${jobId}/${format}`)
      if (!response.ok) {
        throw new Error("Failed to download file")
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `scraped-data-${new Date().toISOString().split("T")[0]}.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error("Download error:", error)
    }
  }

  const handleClearData = () => {
    setScrapedData(null)
    setProcessingStatus({
      stage: "idle",
      progress: 0,
      message: "",
    })
    setUrl("")
    setCustomInstructions("")
    setJobId(null)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900 flex items-center justify-center gap-2">
            <Sparkles className="h-8 w-8 text-blue-600" />
            Enhanced Web Scraper & AI Chat
          </h1>
          <p className="text-lg text-gray-600">
            Advanced web scraping with multi-strategy extraction, intelligent cleaning, and AI-powered chat
          </p>
        </div>

        {/* URL Input Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Enhanced Website Scraper
            </CardTitle>
            <CardDescription>
              Enter a URL to scrape with advanced content extraction and optional custom instructions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
                disabled={processingStatus.stage === "scraping"}
              />
              <Button
                onClick={() => handleScrapeUrl(false)}
                disabled={!url.trim() || processingStatus.stage === "scraping"}
                className="px-6"
              >
                {processingStatus.stage === "scraping" && !isTestMode ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : null}
                Process All
              </Button>
              <Button
                variant="outline"
                onClick={() => handleScrapeUrl(true)}
                disabled={!url.trim() || processingStatus.stage === "scraping"}
                className="px-6"
              >
                {processingStatus.stage === "scraping" && isTestMode ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <TestTube className="h-4 w-4 mr-2" />
                )}
                Test 1 Page
              </Button>
            </div>

            {/* Custom Instructions */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Custom Instructions (Optional)</label>
              <Textarea
                placeholder="e.g., 'Extract only product information and prices' or 'Focus on technical specifications'"
                value={customInstructions}
                onChange={(e) => setCustomInstructions(e.target.value)}
                className="min-h-[80px]"
                disabled={processingStatus.stage === "scraping"}
              />
              <p className="text-xs text-gray-500">
                Provide specific instructions for content extraction using AI. Leave empty for default extraction.
              </p>
            </div>

            {/* Processing Status */}
            {processingStatus.stage !== "idle" && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{processingStatus.message}</span>
                  <span className="text-gray-500">{processingStatus.progress}%</span>
                </div>
                <Progress value={processingStatus.progress} className="h-2" />
              </div>
            )}

            {/* Status Alerts */}
            {processingStatus.stage === "complete" && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  {scrapedData?.isTestScrape ? "Test scrape" : "Content"} successfully processed with enhanced
                  extraction!
                  {scrapedData?.customInstructionsApplied && " Custom instructions were applied."}
                </AlertDescription>
              </Alert>
            )}

            {processingStatus.stage === "error" && (
              <Alert className="border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">{processingStatus.message}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Main Content */}
        {scrapedData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Scraped Content Panel */}
            <Card className="h-fit">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Enhanced Content
                    {scrapedData.isTestScrape && (
                      <Badge variant="outline" className="ml-2">
                        Test
                      </Badge>
                    )}
                  </CardTitle>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleDownload("json")}>
                      <FileDown className="h-4 w-4 mr-1" />
                      JSON
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleDownload("csv")}>
                      <FileDown className="h-4 w-4 mr-1" />
                      CSV
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleClearData}>
                      <Trash2 className="h-4 w-4 mr-1" />
                      Clear
                    </Button>
                  </div>
                </div>
                <CardDescription>Enhanced extraction from {scrapedData.url}</CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="preview" className="w-full">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="preview">Preview</TabsTrigger>
                    <TabsTrigger value="metadata">Metadata</TabsTrigger>
                    <TabsTrigger value="links">Links</TabsTrigger>
                    <TabsTrigger value="analytics">Analytics</TabsTrigger>
                  </TabsList>

                  <TabsContent value="preview" className="space-y-4">
                    <div className="space-y-2">
                      <h3 className="font-semibold text-lg">{scrapedData.title}</h3>
                      <div className="flex gap-2 flex-wrap">
                        <Badge variant="secondary">{scrapedData.wordCount} words</Badge>
                        <Badge variant="outline">Quality: {scrapedData.qualityScore}/100</Badge>
                        <Badge variant="outline">{scrapedData.metadata.pagesScraped} pages</Badge>
                        {scrapedData.customInstructionsApplied && (
                          <Badge className="bg-purple-100 text-purple-800">Custom AI</Badge>
                        )}
                      </div>
                    </div>

                    <Separator />

                    <ScrollArea className="h-96 w-full rounded border p-4">
                      <div className="whitespace-pre-wrap text-sm text-gray-700 leading-relaxed">
                        {scrapedData.content || "No content available"}
                      </div>
                    </ScrollArea>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(scrapedData.content)}
                      className="w-full"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Copy Full Content
                    </Button>
                  </TabsContent>

                  <TabsContent value="metadata" className="space-y-4">
                    <div className="space-y-3">
                      <div>
                        <label className="text-sm font-medium text-gray-700">URL</label>
                        <p className="text-sm text-gray-600 break-all">{scrapedData.url}</p>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Title</label>
                        <p className="text-sm text-gray-600">{scrapedData.title}</p>
                      </div>

                      {scrapedData.metadata.description && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">Description</label>
                          <p className="text-sm text-gray-600">{scrapedData.metadata.description}</p>
                        </div>
                      )}

                      <div>
                        <label className="text-sm font-medium text-gray-700">Extraction Method</label>
                        <p className="text-sm text-gray-600">{scrapedData.metadata.extractionMethod}</p>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Custom Instructions Applied</label>
                        <p className="text-sm text-gray-600">{scrapedData.customInstructionsApplied ? "Yes" : "No"}</p>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Processed At</label>
                        <p className="text-sm text-gray-600">{new Date(scrapedData.timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="links" className="space-y-4">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Link className="h-4 w-4" />
                        <span className="font-medium">Important Links ({scrapedData.importantLinks.length})</span>
                      </div>

                      {scrapedData.importantLinks.length > 0 ? (
                        <ScrollArea className="h-64 w-full rounded border p-3">
                          <div className="space-y-2">
                            {scrapedData.importantLinks.map((link, index) => (
                              <div key={index} className="p-2 bg-gray-50 rounded text-sm">
                                <div className="font-medium text-blue-600">{link.text}</div>
                                <div className="text-gray-500 text-xs break-all">{link.url}</div>
                                {link.reason && <div className="text-gray-400 text-xs mt-1">Reason: {link.reason}</div>}
                              </div>
                            ))}
                          </div>
                        </ScrollArea>
                      ) : (
                        <p className="text-sm text-gray-500">No important links found</p>
                      )}
                    </div>
                  </TabsContent>

                  <TabsContent value="analytics" className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 bg-blue-50 rounded">
                        <div className="flex items-center gap-2">
                          <BarChart3 className="h-4 w-4 text-blue-600" />
                          <span className="text-sm font-medium">Quality Score</span>
                        </div>
                        <div className="text-2xl font-bold text-blue-600">{scrapedData.qualityScore}/100</div>
                      </div>

                      <div className="p-3 bg-green-50 rounded">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-green-600" />
                          <span className="text-sm font-medium">Word Count</span>
                        </div>
                        <div className="text-2xl font-bold text-green-600">{scrapedData.wordCount}</div>
                      </div>

                      <div className="p-3 bg-purple-50 rounded">
                        <div className="flex items-center gap-2">
                          <Globe className="h-4 w-4 text-purple-600" />
                          <span className="text-sm font-medium">Pages Scraped</span>
                        </div>
                        <div className="text-2xl font-bold text-purple-600">{scrapedData.metadata.pagesScraped}</div>
                      </div>

                      <div className="p-3 bg-orange-50 rounded">
                        <div className="flex items-center gap-2">
                          <Link className="h-4 w-4 text-orange-600" />
                          <span className="text-sm font-medium">Important Links</span>
                        </div>
                        <div className="text-2xl font-bold text-orange-600">{scrapedData.importantLinks.length}</div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            {/* Chat Panel */}
            <Card className="flex flex-col h-[600px]">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  AI Chat
                </CardTitle>
                <CardDescription>Ask questions about the scraped content</CardDescription>
              </CardHeader>

              <CardContent className="flex-1 flex flex-col">
                <ScrollArea className="flex-1 pr-4 mb-4">
                  <div className="space-y-4">
                    {messages.length === 0 ? (
                      <div className="text-center text-gray-500 py-8">
                        <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p>Start a conversation about the scraped content!</p>
                        <p className="text-sm mt-2">
                          Try asking: "What is this article about?" or "Summarize the main points"
                        </p>
                      </div>
                    ) : (
                      messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-lg px-4 py-2 ${
                              message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                            }`}
                          >
                            <div className="whitespace-pre-wrap">{message.content}</div>
                          </div>
                        </div>
                      ))
                    )}

                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-gray-100 rounded-lg px-4 py-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                      </div>
                    )}

                    {error && (
                      <div className="flex justify-center">
                        <Alert className="border-red-200 bg-red-50 max-w-md">
                          <AlertCircle className="h-4 w-4 text-red-600" />
                          <AlertDescription className="text-red-800">Chat error: {error.message}</AlertDescription>
                        </Alert>
                      </div>
                    )}
                  </div>
                </ScrollArea>

                <form onSubmit={handleSubmit} className="flex gap-2">
                  <Input
                    value={input}
                    onChange={handleInputChange}
                    placeholder="Ask about the scraped content..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button type="submit" disabled={isLoading || !input.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
