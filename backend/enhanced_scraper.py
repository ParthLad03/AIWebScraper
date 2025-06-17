"""
Enhanced web scraper with all improvements
"""
import asyncio
import uuid
from typing import Dict, List, Optional
from urllib.parse import urlparse
from pathlib import Path
import json

from content_extractor import ContentExtractor
from content_cleaner import ContentCleaner
from link_extractor import LinkExtractor
from export_utils import ExportUtils

class EnhancedWebScraper:
    """Enhanced web scraper with multi-strategy extraction and intelligent cleaning"""
    
    def __init__(self):
        self.content_extractor = ContentExtractor()
        self.content_cleaner = ContentCleaner()
        self.link_extractor = LinkExtractor()
        self.export_utils = ExportUtils()
        self.crawled_urls = set()
        self.max_pages = 5

    async def scrape_single_page(self, url: str, custom_instructions: str = None) -> Dict:
        """Scrape a single page with enhanced extraction"""
        try:
            print(f"🔍 Starting enhanced single-page scrape of: {url}")
            
            # Extract content using multi-strategy approach
            content_data = await self.content_extractor.extract_content_multi_strategy(
                url, custom_instructions
            )
            
            if not content_data.get('success', False):
                return content_data
            
            # Clean the extracted content
            cleaned_result = self.content_cleaner.clean_content_pipeline(
                content_data.get('content', '')
            )
            
            # Extract links from the page
            if 'html' in content_data:  # If we have HTML available
                links = self.link_extractor.extract_all_links(content_data['html'], url)
            else:
                links = {}
            
            # Combine all results
            result = {
                "url": url,
                "title": content_data.get('title', ''),
                "description": content_data.get('description', ''),
                "content": content_data.get("content", ''),
                "description": content_data.get('description', ''),
                "content": content_data.get('content', ''),
                "cleaned_content": cleaned_result['cleaned_content'],
                "word_count": cleaned_result['word_count'],
                "quality_score": cleaned_result['quality_score'],
                "extraction_method": content_data.get('extraction_method', ''),
                "links": links,
                "cleaning_steps": cleaned_result['cleaning_steps'],
                "custom_instructions_applied": content_data.get('custom_instructions_applied', False),
                "success": True,
                "scraped_at": asyncio.get_event_loop().time()
            }
            
            print(f"✅ Single page scrape completed: {result['word_count']} words, quality score: {result['quality_score']}")
            return result
            
        except Exception as e:
            print(f"❌ Error in single page scrape: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    async def scrape_website_recursive(self, base_url: str, max_pages: int = None, custom_instructions: str = None) -> List[Dict]:
        """Recursively scrape website with enhanced extraction"""
        if max_pages:
            self.max_pages = max_pages
        
        base_domain = urlparse(base_url).netloc
        self.crawled_urls.clear()
        
        print(f"🕸️ Starting enhanced recursive crawl of {base_url}")
        print(f"📊 Maximum pages to crawl: {self.max_pages}")
        
        try:
            # First, scrape the main page
            result = await self.scrape_single_page(base_url, custom_instructions)
            if not result.get('success'):
                return [result]
            
            results = [result]
            self.crawled_urls.add(base_url)
            
            # Get crawlable links from the main page
            links = result.get('links', {})
            crawlable_links = self.link_extractor.get_crawlable_links(links, self.max_pages - 1)
            
            print(f"🔗 Found {len(crawlable_links)} crawlable links")
            
            # Crawl discovered links
            crawl_count = 1
            for current_url in crawlable_links:
                if crawl_count >= self.max_pages:
                    print(f"🛑 Reached maximum page limit ({self.max_pages})")
                    break
                
                if current_url in self.crawled_urls:
                    continue
                
                # Check if URL is from same domain
                if urlparse(current_url).netloc != base_domain:
                    continue
                
                crawl_count += 1
                print(f"🔍 Crawling page {crawl_count}/{self.max_pages}: {current_url}")
                
                page_result = await self.scrape_single_page(current_url, custom_instructions)
                if page_result.get('success'):
                    results.append(page_result)
                    self.crawled_urls.add(current_url)
                    print(f"  ✅ Successfully crawled: {page_result.get('word_count', 0)} words")
                else:
                    print(f"  ❌ Failed to crawl: {page_result.get('error', 'Unknown error')}")
                
                # Polite delay between requests
                await asyncio.sleep(2)
            
            print(f"✅ Enhanced recursive crawl completed!")
            print(f"📊 Total pages successfully crawled: {len([r for r in results if r.get('success')])}")
            
            # Save results to JSON file
            timestamp = uuid.uuid4().hex[:8]
            output_dir = Path("crawl_results")
            output_dir.mkdir(exist_ok=True)
            
            output_file = output_dir / f"enhanced_crawl_{urlparse(base_url).netloc}_{timestamp}.json"
            structured_export = self.export_utils.create_structured_export(results)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(structured_export, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Enhanced crawl results saved to: {output_file}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error during enhanced recursive crawl: {e}")
            import traceback
            traceback.print_exc()
            return [{"success": False, "error": str(e), "url": base_url}]

    def export_to_json(self, data: Dict, pretty: bool = True) -> str:
        """Export data to JSON format"""
        return self.export_utils.to_json(data, pretty)

    def export_to_csv(self, data: Dict) -> str:
        """Export data to CSV format"""
        return self.export_utils.to_csv(data)

    def create_structured_export(self, data: Dict) -> Dict:
        """Create structured export"""
        return self.export_utils.create_structured_export(data)
