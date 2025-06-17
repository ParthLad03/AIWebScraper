from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, HttpUrl
import asyncio
import uuid
import json
from pathlib import Path
import os
from typing import Dict, Optional
import uvicorn
from datetime import datetime

# Import enhanced scraper
from enhanced_scraper import EnhancedWebScraper

app = FastAPI(title="Enhanced Web Scraper API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for scraping jobs
scraping_jobs: Dict[str, Dict] = {}

# Initialize enhanced scraper
enhanced_scraper = EnhancedWebScraper()

class ScrapeRequest(BaseModel):
    url: HttpUrl
    max_pages: Optional[int] = 5
    custom_instructions: Optional[str] = None

class TestScrapeRequest(BaseModel):
    url: HttpUrl
    custom_instructions: Optional[str] = None

class ScrapeResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    result: Optional[Dict] = None
    error: Optional[str] = None

async def scrape_website_task(job_id: str, url: str, max_pages: int = 5, custom_instructions: str = None):
    """Background task to scrape website with enhanced features"""
    try:
        # Update job status
        scraping_jobs[job_id] = {
            "status": "scraping",
            "progress": 10,
            "message": "Initializing enhanced web scraper...",
            "result": None,
            "error": None,
            "started_at": datetime.now().isoformat()
        }
        
        # Update progress
        scraping_jobs[job_id].update({
            "progress": 30,
            "message": "Starting enhanced content extraction..."
        })
        
        # Scrape the website using enhanced scraper
        results = await enhanced_scraper.scrape_website_recursive(
            url, max_pages=max_pages, custom_instructions=custom_instructions
        )
        
        # Update progress
        scraping_jobs[job_id].update({
            "progress": 70,
            "message": "Processing and structuring content..."
        })
        
        # Process results
        if results and len(results) > 0:
            successful_results = [r for r in results if r.get('success', False)]
            
            if successful_results:
                # Create structured export
                structured_data = enhanced_scraper.create_structured_export(successful_results)
                
                # Combine all content for easy access
                combined_content = ""
                total_word_count = 0
                all_important_links = []
                
                for result in successful_results:
                    if result.get('cleaned_content'):
                        combined_content += f"\n\n--- Content from {result['url']} ---\n"
                        combined_content += result['cleaned_content']
                        total_word_count += result.get('word_count', 0)
                        
                        # Collect important links
                        links = result.get('links', {})
                        important_links = links.get('important', [])
                        all_important_links.extend(important_links)
                
                # Create final result with enhanced data
                final_result = {
                    "url": url,
                    "title": successful_results[0].get('title', 'Scraped Content'),
                    "description": f"Enhanced content scraped from {len(successful_results)} pages",
                    "cleanedContent": combined_content.strip(),
                    "wordCount": total_word_count,
                    "pagesScraped": len(successful_results),
                    "qualityScore": sum(r.get('quality_score', 0) for r in successful_results) / len(successful_results),
                    "importantLinks": all_important_links[:20],  # Top 20 important links
                    "structuredData": structured_data,
                    "customInstructionsApplied": any(r.get('custom_instructions_applied', False) for r in successful_results),
                    "allResults": successful_results,
                    "metadata": {
                        "scrapedAt": scraping_jobs[job_id].get("started_at"),
                        "totalPages": len(results),
                        "successfulPages": len(successful_results),
                        "failedPages": len(results) - len(successful_results),
                        "averageQualityScore": sum(r.get('quality_score', 0) for r in successful_results) / len(successful_results),
                        "extractionMethod": "enhanced_multi_strategy"
                    }
                }
                
                # Update job as completed
                scraping_jobs[job_id].update({
                    "status": "completed",
                    "progress": 100,
                    "message": f"Successfully scraped {len(successful_results)} pages with enhanced extraction",
                    "result": final_result
                })
            else:
                scraping_jobs[job_id].update({
                    "status": "error",
                    "progress": 0,
                    "message": "No content could be extracted from the website",
                    "error": "No successful scraping results"
                })
        else:
            scraping_jobs[job_id].update({
                "status": "error",
                "progress": 0,
                "message": "Failed to scrape website",
                "error": "No results returned from enhanced scraper"
            })
        
    except Exception as e:
        scraping_jobs[job_id].update({
            "status": "error",
            "progress": 0,
            "message": f"Enhanced scraping failed: {str(e)}",
            "error": str(e)
        })

async def test_scrape_task(job_id: str, url: str, custom_instructions: str = None):
    """Background task to test scrape a single page"""
    try:
        # Update job status
        scraping_jobs[job_id] = {
            "status": "scraping",
            "progress": 20,
            "message": "Testing single page extraction...",
            "result": None,
            "error": None,
            "started_at": datetime.now().isoformat()
        }
        
        # Update progress
        scraping_jobs[job_id].update({
            "progress": 50,
            "message": "Extracting and cleaning content..."
        })
        
        # Scrape single page
        result = await enhanced_scraper.scrape_single_page(url, custom_instructions)
        
        if result.get('success', False):
            # Create test result
            test_result = {
                "url": url,
                "title": result.get('title', ''),
                "description": result.get('description', ''),
                "cleanedContent": result.get('cleaned_content', ''),
                "wordCount": result.get('word_count', 0),
                "qualityScore": result.get('quality_score', 0),
                "extractionMethod": result.get('extraction_method', ''),
                "importantLinks": result.get('links', {}).get('important', [])[:10],
                "customInstructionsApplied": result.get('custom_instructions_applied', False),
                "cleaningSteps": result.get('cleaning_steps', []),
                "metadata": {
                    "scrapedAt": scraping_jobs[job_id].get("started_at"),
                    "isTestScrape": True,
                    "extractionMethod": result.get('extraction_method', '')
                }
            }
            
            scraping_jobs[job_id].update({
                "status": "completed",
                "progress": 100,
                "message": f"Test scrape completed successfully: {result.get('word_count', 0)} words extracted",
                "result": test_result
            })
        else:
            scraping_jobs[job_id].update({
                "status": "error",
                "progress": 0,
                "message": "Test scrape failed",
                "error": result.get('error', 'Unknown error')
            })
            
    except Exception as e:
        scraping_jobs[job_id].update({
            "status": "error",
            "progress": 0,
            "message": f"Test scrape failed: {str(e)}",
            "error": str(e)
        })

@app.post("/scrape", response_model=ScrapeResponse)
async def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Start an enhanced web scraping job"""
    job_id = str(uuid.uuid4())
    url = str(request.url)
    
    # Initialize job
    scraping_jobs[job_id] = {
        "status": "started",
        "progress": 0,
        "message": "Enhanced scraping job started",
        "result": None,
        "error": None,
        "started_at": datetime.now().isoformat()
    }
    
    # Start background task
    background_tasks.add_task(
        scrape_website_task, 
        job_id, 
        url, 
        request.max_pages, 
        request.custom_instructions
    )
    
    return ScrapeResponse(
        job_id=job_id,
        status="started",
        message="Enhanced scraping job started successfully"
    )

@app.post("/test-scrape", response_model=ScrapeResponse)
async def start_test_scrape(request: TestScrapeRequest, background_tasks: BackgroundTasks):
    """Start a test scrape of a single page"""
    job_id = str(uuid.uuid4())
    url = str(request.url)
    
    # Initialize job
    scraping_jobs[job_id] = {
        "status": "started",
        "progress": 0,
        "message": "Test scrape job started",
        "result": None,
        "error": None,
        "started_at": datetime.now().isoformat()
    }
    
    # Start background task
    background_tasks.add_task(
        test_scrape_task,
        job_id,
        url,
        request.custom_instructions
    )
    
    return ScrapeResponse(
        job_id=job_id,
        status="started",
        message="Test scrape job started successfully"
    )

@app.get("/scrape/{job_id}", response_model=JobStatus)
async def get_scrape_status(job_id: str):
    """Get the status of a scraping job"""
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = scraping_jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        result=job.get("result"),
        error=job.get("error")
    )

@app.get("/export/{job_id}/json")
async def export_json(job_id: str, pretty: bool = True):
    """Export job results as JSON"""
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = scraping_jobs[job_id]
    if job["status"] != "completed" or not job.get("result"):
        raise HTTPException(status_code=400, detail="Job not completed or no results available")
    
    json_data = enhanced_scraper.export_to_json(job["result"], pretty)
    
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=scrape_results_{job_id}.json"}
    )

@app.get("/export/{job_id}/csv")
async def export_csv(job_id: str):
    """Export job results as CSV"""
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = scraping_jobs[job_id]
    if job["status"] != "completed" or not job.get("result"):
        raise HTTPException(status_code=400, detail="Job not completed or no results available")
    
    csv_data = enhanced_scraper.export_to_csv(job["result"])
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scrape_results_{job_id}.csv"}
    )

@app.delete("/scrape/{job_id}")
async def delete_scrape_job(job_id: str):
    """Delete a scraping job"""
    if job_id not in scraping_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    del scraping_jobs[job_id]
    return {"message": "Job deleted successfully"}

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check if we can import required modules
        from content_extractor import ContentExtractor
        from content_cleaner import ContentCleaner
        from link_extractor import LinkExtractor
        
        # Check if Gemini API key is available
        gemini_available = bool(os.getenv('GOOGLE_GENERATIVE_AI_API_KEY'))
        
        # Check crawl4ai availability
        try:
            from crawl4ai import AsyncWebCrawler
            crawl4ai_available = True
        except ImportError:
            crawl4ai_available = False
        
        health_status = {
            "status": "healthy",
            "message": "Enhanced Web Scraper API is running",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "content_extractor": True,
                "content_cleaner": True,
                "link_extractor": True,
                "crawl4ai": crawl4ai_available,
                "gemini_api": gemini_available
            },
            "active_jobs": len(scraping_jobs),
            "version": "2.0.0"
        }
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/jobs")
async def list_jobs():
    """List all active jobs"""
    jobs_summary = []
    for job_id, job_data in scraping_jobs.items():
        jobs_summary.append({
            "job_id": job_id,
            "status": job_data["status"],
            "progress": job_data["progress"],
            "started_at": job_data.get("started_at"),
            "message": job_data["message"]
        })
    
    return {
        "total_jobs": len(jobs_summary),
        "jobs": jobs_summary
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
