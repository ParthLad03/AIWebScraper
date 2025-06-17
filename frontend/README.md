# Enhanced Web Scraper & AI Chat v2.0

A comprehensive web application that combines advanced web scraping with AI-powered chat functionality, featuring multi-strategy content extraction, intelligent cleaning, and structured data export.

## 🚀 New Features in v2.0

### Advanced Content Extraction
- **Multi-Strategy Extraction**: 4 different extraction methods with automatic fallback
- **Semantic HTML Analysis**: Prioritizes article, main, and content areas
- **Readability Algorithm**: Scores content quality and text density
- **Custom AI Instructions**: Use Gemini to apply specific extraction rules

### Intelligent Content Cleaning
- **Multi-Stage Pipeline**: 6-step cleaning process
- **Quality Scoring**: Automatic content quality assessment (0-100)
- **Structure Preservation**: Maintains headings and paragraph structure
- **Noise Removal**: Eliminates ads, navigation, and web artifacts

### Smart Link Discovery
- **Categorized Links**: Navigation, content, footer, external, social, download
- **Priority-Based Crawling**: Important links get crawled first
- **Link Quality Scoring**: Intelligent link prioritization
- **Important Links Extraction**: Automatically identifies key pages

### Enhanced Export Options
- **Structured JSON**: Organized data with metadata and analytics
- **CSV Export**: Tabular format with important links in dedicated columns
- **Multiple Formats**: Both pretty-printed and compact JSON

### Testing & Health Monitoring
- **Test Scrape**: Single-page testing before full crawl
- **Health Check API**: Monitor all system components
- **Real-time Progress**: Enhanced progress tracking with detailed messages

## 📋 Requirements

### Essential
- `GOOGLE_GENERATIVE_AI_API_KEY` - Google Gemini API key for AI features

### Optional
- `PYTHON_API_URL` - Python API URL (defaults to localhost:8000)

## 🛠️ Installation

### 1. Clone and Install Dependencies

\`\`\`bash
# Frontend (Next.js)
npm install

# Backend (Python)
cd python-scraper
pip install -r requirements.txt
\`\`\`

### 2. Environment Setup

Create `.env.local`:
\`\`\`env
GOOGLE_GENERATIVE_AI_API_KEY=your_gemini_api_key_here
PYTHON_API_URL=http://localhost:8000
\`\`\`

### 3. Get Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to your `.env.local` file

## 🚀 Running the Application

### Option 1: Run Both Services
\`\`\`bash
npm run dev-full
\`\`\`

### Option 2: Run Separately

**Terminal 1 - Python API:**
\`\`\`bash
cd python-scraper
python main.py
\`\`\`

**Terminal 2 - Next.js Frontend:**
\`\`\`bash
npm run dev
\`\`\`

### Option 3: Health Check
\`\`\`bash
npm run health-check
\`\`\`

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Python API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:3000/api/health

## 📊 API Endpoints

### Enhanced Scraping
- `POST /scrape` - Full website scraping with custom instructions
- `POST /test-scrape` - Single page test scraping
- `GET /scrape/{job_id}` - Get job status and results

### Export & Download
- `GET /export/{job_id}/json` - Download results as JSON
- `GET /export/{job_id}/csv` - Download results as CSV

### Monitoring
- `GET /health` - Comprehensive health check
- `GET /jobs` - List all active jobs

## 🎯 How to Use

### Basic Scraping
1. Enter any website URL
2. Click "Process All" to scrape multiple pages
3. Or click "Test 1 Page" to test single page extraction

### Custom Instructions
1. Add specific instructions in the text area
2. Examples:
   - "Extract only product names and prices"
   - "Focus on technical specifications and features"
   - "Summarize key points in bullet format"

### AI Chat
1. Once content is scraped, use the chat panel
2. Ask questions about the extracted content
3. Get AI-powered insights and summaries

### Export Data
1. Click JSON or CSV buttons to download
2. JSON includes full structured data with metadata
3. CSV provides tabular format with important links

## 🔧 Architecture

### Content Extraction Pipeline
\`\`\`
URL Input → Multi-Strategy Extraction → Content Cleaning → Link Discovery → Quality Scoring → Export
\`\`\`

### Extraction Strategies
1. **Semantic HTML** - Uses article, main, content selectors
2. **Readability** - Analyzes text density and paragraph quality
3. **Text Density** - Finds areas with highest content concentration
4. **Raw Parsing** - Fallback method for difficult sites

### Content Cleaning Stages
1. **Whitespace Normalization** - Clean spacing and line breaks
2. **Web Artifacts Removal** - Remove cookies, ads, navigation
3. **Navigation Filtering** - Remove menu and navigation elements
4. **Quality Filtering** - Keep only meaningful content lines
5. **Structure Improvement** - Enhance readability and formatting
6. **Final Cleanup** - Polish and normalize text

## 📈 Quality Metrics

### Content Quality Score (0-100)
- **Length**: Optimal word count (100-3000 words)
- **Structure**: Proper sentence and paragraph formation
- **Vocabulary**: Richness and diversity of language
- **Indicators**: Presence of quality content markers

### Link Categorization
- **Navigation**: High-priority site navigation links
- **Important**: Key pages (about, contact, services, etc.)
- **Content**: Links within main content areas
- **External**: Links to other domains
- **Social**: Social media platform links
- **Download**: File downloads and resources

## 🛡️ Best Practices

### Respectful Crawling
- 2-second delays between requests
- Respects robots.txt files
- Limits concurrent requests
- Monitors for rate limiting

### Error Handling
- Graceful fallbacks for failed extractions
- Detailed error reporting
- Automatic retry mechanisms
- Comprehensive logging

### Performance Optimization
- Async processing for all operations
- Background job processing
- Memory-efficient content handling
- Optimized link discovery algorithms

## 🔍 Troubleshooting

### Common Issues

1. **Python API not starting**
   \`\`\`bash
   cd python-scraper
   pip install -r requirements.txt
   python main.py
   \`\`\`

2. **Chat not working**
   - Verify `GOOGLE_GENERATIVE_AI_API_KEY` is set correctly
   - Check health endpoint: `curl http://localhost:3000/api/health`

3. **Poor content extraction**
   - Try test scrape first to see extraction quality
   - Use custom instructions for specific content types
   - Check if website blocks automated requests

4. **Export not working**
   - Ensure scraping job completed successfully
   - Check job status before attempting export

### Health Monitoring

Visit `/api/health` to check:
- Next.js API status
- Python API connectivity
- Environment variable configuration
- Component availability

## 📝 Development

### Adding New Extraction Strategies
1. Create new method in `ContentExtractor` class
2. Add to strategies list in `extract_content_multi_strategy`
3. Implement scoring mechanism

### Custom Content Cleaners
1. Add new cleaning method to `ContentCleaner` class
2. Include in `clean_content_pipeline`
3. Update cleaning steps tracking

### New Export Formats
1. Add method to `ExportUtils` class
2. Create new API endpoint in `main.py`
3. Add frontend download button

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

---

**Enhanced Web Scraper v2.0** - Intelligent content extraction meets AI-powered analysis
