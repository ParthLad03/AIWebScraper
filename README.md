# Enhanced Web Scraper & AI Chat v2.0

<div align="center">

![Web Scraper Logo](https://img.shields.io/badge/Web%20Scraper-v2.0-blue?style=for-the-badge&logo=spider&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15.1.3-black?style=for-the-badge&logo=next.js&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?style=for-the-badge&logo=fastapi&logoColor=white)
![AI Powered](https://img.shields.io/badge/AI%20Powered-Gemini-purple?style=for-the-badge&logo=google&logoColor=white)

**A comprehensive web application that combines advanced web scraping with AI-powered chat functionality**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [API Reference](#-api-reference) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🌟 Features

### 🚀 **Advanced Content Extraction**
- **Multi-Strategy Extraction**: 4 different extraction methods with intelligent fallback
- **Semantic HTML Analysis**: Prioritizes `<article>`, `<main>`, and content-specific selectors
- **Readability Algorithm**: Scores paragraphs based on text density and quality indicators
- **Text Density Analysis**: Identifies content-rich areas automatically
- **Custom AI Instructions**: Use Google Gemini to apply domain-specific extraction rules

### 🧹 **Intelligent Content Cleaning**
- **6-Stage Cleaning Pipeline**: Comprehensive content processing and normalization
- **Quality Scoring System**: Automatic content quality assessment (0-100 scale)
- **Structure Preservation**: Maintains headings, paragraphs, and logical flow
- **Noise Removal**: Eliminates ads, navigation menus, cookie banners, and web artifacts
- **Content Filtering**: Removes low-quality lines and metadata clutter

### 🔗 **Smart Link Discovery & Categorization**
- **Intelligent Link Classification**: Navigation, content, footer, external, social, download links
- **Priority-Based Crawling**: Important pages (About, Contact, Services) get crawled first
- **Link Quality Scoring**: Automatic prioritization based on context and importance
- **Important Links Extraction**: Identifies and extracts key pages for easy access

### 📊 **Enhanced Export & Analytics**
- **Structured JSON Export**: Organized data with comprehensive metadata and analytics
- **CSV Export**: Tabular format with important links in dedicated columns
- **Quality Metrics**: Content scoring, word counts, extraction method tracking
- **Crawl Statistics**: Success rates, page counts, domain analysis

### 🧪 **Testing & Monitoring**
- **Test Scrape Mode**: Single-page testing before full website crawling
- **Real-time Progress Tracking**: Detailed status updates during scraping process
- **Comprehensive Health Checks**: Monitor all system components and dependencies
- **Job Management**: Track, monitor, and manage multiple scraping jobs

### 🤖 **AI-Powered Chat Integration**
- **Context-Aware Conversations**: Chat about scraped content using Google Gemini
- **Custom Instruction Processing**: AI applies user-specific extraction requirements
- **Intelligent Summarization**: Get insights, summaries, and analysis of scraped data
- **Multi-turn Conversations**: Maintain context across multiple chat interactions

---

## 📋 Requirements

### **Essential Dependencies**
- **Node.js** 18.0+ and npm
- **Python** 3.8+ with pip
- **Google Gemini API Key** (for AI features)

### **Environment Variables**
\`\`\`env
# Required
GOOGLE_GENERATIVE_AI_API_KEY=your_gemini_api_key_here

# Optional
PYTHON_API_URL=http://localhost:8000  # Defaults to localhost:8000
\`\`\`

---

## 🛠️ Installation

### **1. Clone the Repository**
\`\`\`bash
git clone https://github.com/your-username/enhanced-web-scraper.git
cd enhanced-web-scraper
\`\`\`

### **2. Install Frontend Dependencies**
\`\`\`bash
npm install
\`\`\`

### **3. Install Backend Dependencies**
\`\`\`bash
cd python-scraper
pip install -r requirements.txt
cd ..
\`\`\`

### **4. Environment Setup**
Create a `.env.local` file in the root directory:
\`\`\`env
GOOGLE_GENERATIVE_AI_API_KEY=your_gemini_api_key_here
PYTHON_API_URL=http://localhost:8000
\`\`\`

### **5. Get Google Gemini API Key**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env.local` file

---

## 🚀 Running the Application

### **Option 1: Run Both Services Together (Recommended)**
\`\`\`bash
npm run dev-full
\`\`\`

### **Option 2: Run Services Separately**

**Terminal 1 - Python API Server:**
\`\`\`bash
cd python-scraper
python main.py
\`\`\`

**Terminal 2 - Next.js Frontend:**
\`\`\`bash
npm run dev
\`\`\`

### **Option 3: Health Check**
\`\`\`bash
npm run health-check
\`\`\`

### **Access Points**
- **Frontend Application**: http://localhost:3000
- **Python API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check Endpoint**: http://localhost:3000/api/health

---

## 🎯 Usage Guide

### **Basic Web Scraping**

1. **Enter URL**: Input any website URL in the main interface
2. **Choose Scraping Mode**:
   - **"Process All"**: Scrape multiple pages (up to 5 by default)
   - **"Test 1 Page"**: Test extraction on a single page first
3. **Monitor Progress**: Watch real-time progress updates and status messages
4. **Review Results**: Examine extracted content, quality scores, and important links

### **Custom AI Instructions**

Add specific instructions to tailor content extraction:

\`\`\`
Examples:
• "Extract only product names, prices, and descriptions"
• "Focus on technical specifications and system requirements"
• "Summarize key points in bullet format"
• "Extract contact information and business hours"
• "Find all mentioned dates, events, and deadlines"
\`\`\`

### **AI Chat Interaction**

Once content is scraped:
1. Use the chat panel to ask questions about the extracted content
2. Get AI-powered insights, summaries, and analysis
3. Ask follow-up questions for deeper understanding

**Example Chat Queries:**
- "What is this article about?"
- "Summarize the main points in 3 sentences"
- "What are the key benefits mentioned?"
- "Extract all the statistics and numbers"
- "What problems does this solve?"

### **Data Export**

Export scraped data in multiple formats:
- **JSON**: Complete structured data with metadata and analytics
- **CSV**: Tabular format perfect for spreadsheet analysis
- **Important Links**: Dedicated column/parameter for key page links

---

## 📚 API Reference

### **Scraping Endpoints**

#### `POST /scrape`
Start a comprehensive website scraping job.

**Request Body:**
\`\`\`json
{
  "url": "https://example.com",
  "max_pages": 5,
  "custom_instructions": "Extract product information only"
}
\`\`\`

**Response:**
\`\`\`json
{
  "job_id": "uuid-string",
  "status": "started",
  "message": "Enhanced scraping job started successfully"
}
\`\`\`

#### `POST /test-scrape`
Test scrape a single page.

**Request Body:**
\`\`\`json
{
  "url": "https://example.com",
  "custom_instructions": "Focus on main content only"
}
\`\`\`

#### `GET /scrape/{job_id}`
Get job status and results.

**Response:**
\`\`\`json
{
  "job_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "message": "Successfully scraped 3 pages",
  "result": {
    "url": "https://example.com",
    "title": "Page Title",
    "cleanedContent": "Extracted content...",
    "wordCount": 1250,
    "qualityScore": 85,
    "importantLinks": [...],
    "metadata": {...}
  }
}
\`\`\`

### **Export Endpoints**

#### `GET /export/{job_id}/json`
Download results as structured JSON.

#### `GET /export/{job_id}/csv`
Download results as CSV file.

### **Monitoring Endpoints**

#### `GET /health`
Comprehensive system health check.

**Response:**
\`\`\`json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "content_extractor": true,
    "content_cleaner": true,
    "link_extractor": true,
    "crawl4ai": true,
    "gemini_api": true
  },
  "active_jobs": 2,
  "version": "2.0.0"
}
\`\`\`

#### `GET /jobs`
List all active scraping jobs.

---

## 🏗️ Architecture

### **System Overview**
\`\`\`
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js UI   │────│   FastAPI Server │────│  Content Engine │
│   (Frontend)    │    │   (Orchestrator) │    │   (Processing)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
    ┌─────────┐              ┌─────────┐              ┌─────────┐
    │ Chat AI │              │ Job Mgmt│              │ Export  │
    │ (Gemini)│              │ (Redis) │              │ Utils   │
    └─────────┘              └─────────┘              └─────────┘
\`\`\`

### **Content Processing Pipeline**
\`\`\`
URL Input → Multi-Strategy Extraction → Content Cleaning → Link Discovery → Quality Scoring → Export
    ↓              ↓                        ↓                ↓               ↓            ↓
Strategy 1    Whitespace Clean      Navigation Links    Length Score    JSON Export   
Strategy 2    Artifact Removal      Content Links       Structure Score CSV Export    
Strategy 3    Navigation Filter     Important Links     Vocabulary Score            
Strategy 4    Quality Filter        External Links      Content Indicators          
\`\`\`

### **Extraction Strategies**

1. **Semantic HTML Strategy**
   - Targets `<article>`, `<main>`, `<section>` elements
   - Uses content-specific CSS selectors
   - Removes navigation and sidebar elements

2. **Readability Strategy**
   - Analyzes paragraph quality and text density
   - Scores elements based on content indicators
   - Combines top-scoring content blocks

3. **Text Density Strategy**
   - Calculates text-to-HTML ratios
   - Identifies content-rich areas
   - Filters based on density thresholds

4. **Raw Parsing Strategy**
   - Fallback method for difficult websites
   - Basic HTML tag removal and text extraction
   - Minimal processing for maximum coverage

### **Content Cleaning Stages**

1. **Whitespace Normalization**: Clean spacing and line breaks
2. **Web Artifacts Removal**: Remove cookies, ads, navigation elements
3. **Navigation Filtering**: Filter menu and navigation text
4. **Quality Filtering**: Keep only meaningful content lines
5. **Structure Improvement**: Enhance readability and formatting
6. **Final Cleanup**: Polish and normalize final text

### **Link Classification System**

- **Navigation Links**: Site navigation, menus, breadcrumbs
- **Important Links**: About, Contact, Services, Documentation
- **Content Links**: Links within main content areas
- **External Links**: Links to other domains
- **Social Links**: Social media platform links
- **Download Links**: Files, documents, resources

---

## 📊 Quality Metrics & Scoring

### **Content Quality Score (0-100)**

| Factor | Weight | Description |
|--------|--------|-------------|
| **Length** | 30% | Optimal word count (100-3000 words) |
| **Structure** | 25% | Proper sentences and paragraphs |
| **Vocabulary** | 20% | Language richness and diversity |
| **Indicators** | 15% | Quality content markers present |
| **Readability** | 10% | Sentence length and complexity |

### **Link Priority Scoring**

| Link Type | Base Score | Bonus Factors |
|-----------|------------|---------------|
| Navigation | 10 | Important keywords (+3), Proper length (+5) |
| Content | 5 | Context relevance (+3), Description quality (+2) |
| Footer | 3 | Contact/About pages (+5) |

### **Extraction Success Metrics**

- **Word Count**: Total extracted words
- **Quality Score**: Content quality assessment
- **Link Count**: Important links discovered
- **Page Success Rate**: Successful vs. failed page extractions
- **Processing Time**: Time taken for extraction and cleaning

---

## 🛡️ Best Practices & Limitations

### **Respectful Web Scraping**
- ✅ 2-second delays between requests
- ✅ Respects `robots.txt` files
- ✅ Limits concurrent requests
- ✅ Monitors for rate limiting
- ✅ User-agent identification

### **Error Handling**
- ✅ Graceful fallbacks for failed extractions
- ✅ Detailed error reporting and logging
- ✅ Automatic retry mechanisms
- ✅ Timeout protection (60 seconds per page)

### **Performance Optimization**
- ✅ Async processing for all operations
- ✅ Background job processing
- ✅ Memory-efficient content handling
- ✅ Optimized link discovery algorithms

### **Known Limitations**
- ⚠️ JavaScript-heavy SPAs may have limited content extraction
- ⚠️ Sites with aggressive bot protection may block requests
- ⚠️ Very large pages (>10MB) may timeout
- ⚠️ Custom instructions require Gemini API key

---

## 🔧 Configuration & Customization

### **Scraping Configuration**
```python
# In enhanced_scraper.py
self.max_pages = 5  # Maximum pages to crawl
timeout = 60000     # Page load timeout (ms)
word_threshold = 5  # Minimum words per content block
