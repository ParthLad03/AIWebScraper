import getpass
import os
import dotenv
import bs4
# Remove unused LangChain imports that require LangSmith
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_chroma import Chroma
# from langchain import hub
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langgraph.graph import START, StateGraph
# from typing_extensions import List, TypedDict

import uuid
import json
from pathlib import Path
import re
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy, LLMConfig
from urllib.parse import urlparse, urljoin
from pydantic import BaseModel, Field 
from typing import Optional, Dict
import datetime

# Update the schema definitions
class MetadataModel(BaseModel):
    title: Optional[str]
    description: Optional[str]
    keywords: Optional[str]

class WebContentSchema(BaseModel):
    main_content: str = Field(default="")
    navigation: str = Field(default="")
    sidebar: str = Field(default="")
    metadata: Dict = Field(default_factory=dict)
    technical_content: str = Field(default="")
    structured_data: str = Field(default="")
    additional_content: str = Field(default="")

    class Config:
        arbitrary_types_allowed = True

class WebContentScraper:
    """Advanced web scraper using crawl4ai for comprehensive content extraction"""
    
    def __init__(self):
        self.crawler = None
        self.max_pages = 5  # Default max pages to crawl
        self.crawled_urls = set()
        self.domain_links = {}
    
    def _normalize_url(self, href, base_url):
        """Normalize and convert relative URLs to absolute URLs"""
        try:
            if not href:
                return None
            
            # Handle relative URLs
            if not urlparse(href).netloc:
                href = urljoin(base_url, href)
            
            # Clean up the URL
            parsed = urlparse(href)
            # Remove fragment but keep query parameters
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                normalized += f"?{parsed.query}"
            
            # Remove trailing slashes for consistency
            if normalized.endswith('/') and len(normalized) > 1:
                normalized = normalized.rstrip('/')
            
            return normalized
        except Exception:
            return None

    async def initialize_crawler(self):
        """Initialize the crawler with updated settings"""
        if self.crawler is None:
            try:
                self.crawler = AsyncWebCrawler(
                    headless=True,
                    verbose=True,
                    browser_type="chromium",
                    magic=False,
                    word_threshold=10,
                    image_description_min_word_threshold=5,
                    follow_links=True,  # Enable following links
                    max_depth=3,        # Set crawling depth
                    respect_robots_txt=True,
                    timeout=60000       # Increase timeout to 60 seconds
                )
                await self.crawler.start()
                print("✅ Crawler initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing crawler: {e}")
                raise e
    
    def _clean_content(self, content):
        """Clean extracted content with better preservation of meaningful text"""
        if not content:
            return ""
        
        print(f"🧹 Cleaning content (original length: {len(content)} chars)")
        
        # First, let's preserve the content structure better
        # Remove excessive whitespace but keep paragraph breaks
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove specific web artifacts but be more conservative
        patterns_to_remove = [
            r'Cookie\s+Policy.*?Accept',
            r'Privacy\s+Policy.*?Accept', 
            r'This website uses cookies.*?Accept',
            r'Skip to main content',
            r'Skip to navigation',
            r'Loading\.\.\.',
            r'Please enable JavaScript',
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove markdown-style links but keep the text
        content = re.sub(r'\[([^\]]+)\]$$[^)]+$$', r'\1', content)
        
        # Remove empty lines and excessive spacing
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Keep lines that have meaningful content (more than just punctuation/symbols)
            if len(line) > 3 and re.search(r'[a-zA-Z]', line):
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines).strip()
        print(f"🧹 Cleaned content (final length: {len(result)} chars, words: {len(result.split())})")
        
        return result

    async def scrape_url(self, url):
        crawler = None
        try:
            # Create a new crawler instance for each URL to avoid state issues
            crawler = AsyncWebCrawler(
                headless=True,
                verbose=True,
                browser_type="chromium",
                magic=False,
                word_threshold=5,  # Lower threshold to capture more content
                image_description_min_word_threshold=5,
                follow_links=True,
                max_depth=3,
                respect_robots_txt=True,
                timeout=60000
            )
            
            await crawler.start()
            
            print(f"🌐 Crawling: {url}")
            
            # Enhanced crawling with JavaScript execution and navigation extraction
            result = await crawler.arun(
                url=url,
                bypass_cache=True,
                wait_for="networkidle",
                word_threshold=5,
                # Add JavaScript to extract navigation links
                js_code=[
                    """
                    // Extract navigation links from common navigation selectors
                    function extractNavigationLinks() {
                        const navSelectors = [
                            'nav', 'navigation', '.nav', '.navbar', '.navigation', '.menu',
                            '.main-nav', '.primary-nav', '.site-nav', '.top-nav', '.header-nav',
                            '[role="navigation"]', '.nav-menu', '.menu-bar', '.nav-bar',
                            'header nav', 'header .nav', 'header .menu', '.header-menu',
                            '.site-header nav', '.site-header .nav', '.site-header .menu'
                        ];
                        
                        const navLinks = [];
                        
                        navSelectors.forEach(selector => {
                            try {
                                const elements = document.querySelectorAll(selector);
                                elements.forEach(element => {
                                    const links = element.querySelectorAll('a[href]');
                                    links.forEach(link => {
                                        const href = link.getAttribute('href');
                                        const text = link.textContent?.trim() || '';
                                        if (href && text && text.length > 2) {
                                            navLinks.push({
                                                href: href,
                                                text: text,
                                                selector: selector,
                                                source: 'navigation'
                                            });
                                        }
                                    });
                                });
                            } catch (e) {
                                console.log('Error with selector:', selector, e);
                            }
                        });
                        
                        // Also look for footer links (often contain important pages)
                        const footerSelectors = ['footer', '.footer', '.site-footer', '#footer'];
                        footerSelectors.forEach(selector => {
                            try {
                                const elements = document.querySelectorAll(selector);
                                elements.forEach(element => {
                                    const links = element.querySelectorAll('a[href]');
                                    links.forEach(link => {
                                        const href = link.getAttribute('href');
                                        const text = link.textContent?.trim() || '';
                                        if (href && text && text.length > 2 && text.length < 50) {
                                            navLinks.push({
                                                href: href,
                                                text: text,
                                                selector: selector,
                                                source: 'footer'
                                            });
                                        }
                                    });
                                });
                            } catch (e) {
                                console.log('Error with footer selector:', selector, e);
                            }
                        });
                        
                        // Store in window for retrieval
                        window.extractedNavLinks = navLinks;
                        return navLinks;
                    }
                    
                    // Execute the extraction
                    extractNavigationLinks();
                    """
                ]
            )
            
            if result.success:
                print(f"✅ Crawl successful for {url}")
                
                # Extract structured content
                extracted_data = {}
                if result.extracted_content:
                    try:
                        extracted_data = json.loads(result.extracted_content) if isinstance(result.extracted_content, str) else result.extracted_content
                    except json.JSONDecodeError:
                        extracted_data = {"main_content": str(result.extracted_content)}
                
                # Get navigation links from JavaScript execution
                nav_links = []
                if hasattr(result, 'js_execution_results') and result.js_execution_results:
                    for js_result in result.js_execution_results:
                        if isinstance(js_result, list):
                            nav_links.extend(js_result)
                
                print(f"📄 Found {len(nav_links)} navigation links")
                
                # Get the best content source
                content_sources = []
                
                # Priority: markdown > cleaned_html > extracted_content > html
                if hasattr(result, 'markdown') and result.markdown:
                    content_sources.append(('markdown', result.markdown))
                    print(f"📝 Markdown content: {len(result.markdown)} chars")
                
                if hasattr(result, 'cleaned_html') and result.cleaned_html:
                    content_sources.append(('cleaned_html', result.cleaned_html))
                    print(f"🧹 Cleaned HTML: {len(result.cleaned_html)} chars")
                
                if extracted_data.get('main_content'):
                    content_sources.append(('extracted_main', extracted_data['main_content']))
                    print(f"📊 Extracted main: {len(extracted_data['main_content'])} chars")
                
                # Use the first available content source
                main_content = ""
                content_type = "none"
                
                for source_type, content in content_sources:
                    if content and len(content.strip()) > 100:
                        main_content = content
                        content_type = source_type
                        print(f"✅ Using {source_type} as main content source")
                        break
                
                if not main_content and hasattr(result, 'html') and result.html:
                    # Fallback to parsing HTML directly
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(result.html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                        script.decompose()
                    
                    main_content = soup.get_text()
                    content_type = "parsed_html"
                    print(f"🔄 Fallback to parsed HTML: {len(main_content)} chars")
                
                # Extract title and metadata
                title = extracted_data.get('metadata', {}).get('title', '') or result.metadata.get('title', '') or "Untitled"
                description = extracted_data.get('metadata', {}).get('description', '') or result.metadata.get('description', '') or ""
                
                # Clean the content
                cleaned_content = self._clean_content(main_content)
                
                if not cleaned_content or len(cleaned_content.strip()) < 50:
                    print(f"⚠️ Warning: Very little content extracted from {url}")
                    # Try to extract at least some content
                    if main_content:
                        # More aggressive extraction - just remove HTML tags and clean minimally
                        from bs4 import BeautifulSoup
                        if '<' in main_content:
                            soup = BeautifulSoup(main_content, 'html.parser')
                            cleaned_content = soup.get_text()
                        else:
                            cleaned_content = main_content
                        
                        # Minimal cleaning
                        cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
                        print(f"🔄 Fallback cleaning resulted in {len(cleaned_content)} chars")
                
                # Enhanced links structure including navigation links
                enhanced_links = dict(result.links) if result.links else {}
                if nav_links:
                    enhanced_links['navigation'] = nav_links
                
                # Calculate word count
                word_count = len(cleaned_content.split()) if cleaned_content else 0
                
                # Save structured JSON
                structured_data = {
                    "url": url,
                    "title": title,
                    "description": description,
                    "extracted_data": extracted_data,
                    "raw_markdown": result.markdown if hasattr(result, 'markdown') else "",
                    "metadata": dict(result.metadata) if result.metadata else {},
                    "links": enhanced_links,
                    "navigation_links": nav_links,
                    "media": result.media if hasattr(result, 'media') else [],
                    "cleaned_content": cleaned_content,
                    "word_count": word_count,
                    "content_type": content_type,
                    "success": True
                }
                
                print(f"✅ Successfully processed {url}: {word_count} words extracted")
                return structured_data
            else:
                print(f"❌ Failed to crawl {url}: {result.error_message}")
                return {"success": False, "error": result.error_message, "url": url}
                
        except Exception as e:
            print(f"❌ Error crawling {url}: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e), "url": url}
        
        finally:
            # Always try to close the crawler
            if crawler:
                try:
                    if hasattr(crawler, 'close'):
                        await crawler.close()
                    elif hasattr(crawler, 'stop'):
                        await crawler.stop()
                    elif hasattr(crawler, '__aexit__'):
                        await crawler.__aexit__(None, None, None)
                    print("✅ Crawler closed successfully")
                except Exception as e:
                    print(f"Warning: Error closing crawler: {e}")
    
    async def scrape_multiple_urls(self, urls):
        """Scrape multiple URLs"""
        if isinstance(urls, str):
            urls = [urls]
        
        print(f"🚀 Starting comprehensive crawling of {len(urls)} URLs...")
        
        results = []
        for url in urls:
            result = await self.scrape_url(url)
            results.append(result)
        
        return results
    
    async def close(self):
        """Close the crawler"""
        if self.crawler:
            try:
                if hasattr(self.crawler, 'close'):
                    await self.crawler.close()
                elif hasattr(self.crawler, 'stop'):
                    await self.crawler.stop()
                elif hasattr(self.crawler, '__aexit__'):
                    await self.crawler.__aexit__(None, None, None)
                else:
                    self.crawler = None
            except Exception as e:
                print(f"Warning: Error closing crawler: {e}")
                self.crawler = None

    async def scrape_website_recursive(self, base_url, max_pages=None):
        """Recursively scrape all pages from a website with enhanced navigation-aware link discovery"""
        if max_pages:
            self.max_pages = max_pages
        
        base_domain = urlparse(base_url).netloc
        self.crawled_urls.clear()
        self.domain_links[base_domain] = set()

        print(f"🕸️ Starting navigation-aware recursive crawl of {base_url}")
        print(f"📊 Maximum pages to crawl: {self.max_pages}")

        try:
            # First, crawl the main page
            result = await self.scrape_url(base_url)
            if not result.get('success'):
                return [result]

            results = [result]
            self.crawled_urls.add(base_url)

            # Enhanced link extraction with navigation priority
            navigation_links = set()
            regular_links = set()
            
            print(f"🔍 Analyzing links found on {base_url}...")
            
            # Process navigation links first (higher priority)
            if 'navigation_links' in result and result['navigation_links']:
                print(f"🧭 Found {len(result['navigation_links'])} navigation links")
                for nav_link in result['navigation_links']:
                    if isinstance(nav_link, dict):
                        href = nav_link.get('href', '')
                        text = nav_link.get('text', '')
                        source = nav_link.get('source', 'navigation')
                        
                        if self._is_valid_crawlable_url(href, base_domain, base_url):
                            full_url = self._normalize_url(href, base_url)
                            if full_url and full_url not in self.crawled_urls:
                                navigation_links.add(full_url)
                                print(f"  🧭 Navigation link: {text} → {full_url}")
            
            # Process regular links
            if 'links' in result and result['links']:
                for link_type, link_list in result['links'].items():
                    if link_type != 'navigation' and isinstance(link_list, list):
                        for link in link_list:
                            href = ""
                            if isinstance(link, dict):
                                href = link.get('href', '')
                            elif isinstance(link, str):
                                href = link
                            
                            if href and self._is_valid_crawlable_url(href, base_domain, base_url):
                                full_url = self._normalize_url(href, base_url)
                                if full_url and full_url not in self.crawled_urls and full_url not in navigation_links:
                                    regular_links.add(full_url)
                
                print(f"🔗 Found {len(regular_links)} additional crawlable links")
            
            # Combine all links, prioritizing navigation links
            all_links_to_crawl = list(navigation_links) + list(regular_links)
            
            print(f"📊 Link Summary:")
            print(f"  🧭 Navigation links: {len(navigation_links)}")
            print(f"  🔗 Regular links: {len(regular_links)}")
            print(f"  🎯 Total unique links to crawl: {len(all_links_to_crawl)}")

            # Crawl discovered links
            crawl_count = 1
            for current_url in all_links_to_crawl:
                if crawl_count >= self.max_pages:
                    print(f"🛑 Reached maximum page limit ({self.max_pages})")
                    break
                if current_url in self.crawled_urls:
                    continue

                crawl_count += 1
                link_source = "🧭 NAV" if current_url in navigation_links else "🔗 REG"
                print(f"🔍 Crawling page {crawl_count}/{self.max_pages} [{link_source}]: {current_url}")
                
                result = await self.scrape_url(current_url)
                if result.get('success'):
                    results.append(result)
                    self.crawled_urls.add(current_url)
                    print(f"  ✅ Successfully crawled: {result.get('word_count', 0)} words")
                else:
                    print(f"  ❌ Failed to crawl: {result.get('error', 'Unknown error')}")

                await asyncio.sleep(2)  # Polite delay between requests

            print(f"✅ Navigation-aware recursive crawl completed!")
            print(f"📊 Total pages successfully crawled: {len([r for r in results if r.get('success')])}")

            # Save results to JSON file
            timestamp = uuid.uuid4().hex[:8]
            output_dir = Path("crawl_results")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"crawl_{urlparse(base_url).netloc}_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Crawl results saved to: {output_file}")
            
            return results

        except Exception as e:
            print(f"❌ Error during recursive crawl: {e}")
            import traceback
            traceback.print_exc()
            return [{"success": False, "error": str(e), "url": base_url}]
        
    def _is_valid_crawlable_url(self, href, base_domain, current_url):
        """Check if a URL is valid and crawlable"""
        if not href or not isinstance(href, str):
            return False
        
        # Skip non-HTTP protocols
        if href.startswith(('mailto:', 'tel:', 'javascript:', 'data:', 'ftp:', 'file:')):
            return False
        
        # Skip fragments and empty links
        if href.startswith('#') or href.strip() == '':
            return False
        
        # Skip common file extensions that aren't web pages
        skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', 
                          '.css', '.js', '.xml', '.txt', '.zip', '.doc', '.docx', 
                          '.xls', '.xlsx', '.ppt', '.pptx', '.mp4', '.mp3', '.avi',
                          '.woff', '.woff2', '.ttf', '.eot', '.json', '.rss'}
        
        parsed_href = urlparse(href.lower())
        if any(parsed_href.path.endswith(ext) for ext in skip_extensions):
            return False
        
        try:
            parsed = urlparse(href)
            
            # Handle relative URLs
            if not parsed.netloc:
                href = urljoin(current_url, href)
                parsed = urlparse(href)
            
            # Only crawl URLs from the same domain
            if parsed.netloc and parsed.netloc != base_domain:
                return False
            
            # Ensure it's an HTTP/HTTPS URL
            if parsed.scheme not in ['http', 'https']:
                return False
            
            return True
            
        except Exception:
            return False
