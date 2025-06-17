"""
Advanced content extraction strategies
"""
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
import asyncio
from crawl4ai import AsyncWebCrawler

class ContentExtractor:
    """Multi-strategy content extraction system"""
    
    def __init__(self):
        self.content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '#content',
            '.main-content',
            '.page-content'
        ]
        
        self.noise_selectors = [
            'nav', 'header', 'footer', 'aside',
            '.sidebar', '.menu', '.navigation',
            '.ads', '.advertisement', '.banner',
            '.social', '.share', '.comments',
            '.related', '.recommended',
            'script', 'style', 'noscript'
        ]

    async def extract_content_multi_strategy(self, url: str, custom_instructions: str = None) -> Dict:
        """Extract content using multiple strategies with fallback"""
        
        strategies = [
            self._extract_with_semantic_html,
            self._extract_with_readability,
            self._extract_with_text_density,
            self._extract_with_raw_parsing
        ]
        
        crawler = None
        try:
            crawler = AsyncWebCrawler(
                headless=True,
                verbose=False,
                browser_type="chromium",
                magic=False,
                word_threshold=5,
                timeout=30000
            )
            
            await crawler.start()
            
            # Enhanced crawling with custom JavaScript
            result = await crawler.arun(
                url=url,
                bypass_cache=True,
                wait_for="networkidle",
                word_threshold=5,
                js_code=[self._get_content_extraction_js()]
            )
            
            if not result.success:
                return {"success": False, "error": result.error_message, "url": url}
            
            # Try each extraction strategy
            best_content = None
            best_score = 0
            extraction_method = "none"
            
            for i, strategy in enumerate(strategies):
                try:
                    content_data = await strategy(result, url)
                    if content_data and content_data.get('content'):
                        score = self._score_content_quality(content_data['content'])
                        if score > best_score:
                            best_content = content_data
                            best_score = score
                            extraction_method = f"strategy_{i+1}"
                except Exception as e:
                    print(f"Strategy {i+1} failed: {e}")
                    continue
            
            if not best_content:
                return {"success": False, "error": "No content could be extracted", "url": url}
            
            # Apply custom instructions if provided
            if custom_instructions:
                best_content = await self._apply_custom_instructions(
                    best_content, custom_instructions, url
                )
            
            # Add metadata
            best_content.update({
                "url": url,
                "extraction_method": extraction_method,
                "quality_score": best_score,
                "success": True
            })
            
            return best_content
            
        except Exception as e:
            print(f"Error in multi-strategy extraction: {e}")
            return {"success": False, "error": str(e), "url": url}
        
        finally:
            if crawler:
                try:
                    await crawler.close()
                except:
                    pass

    async def _extract_with_semantic_html(self, result, url: str) -> Dict:
        """Extract content using semantic HTML selectors"""
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Remove noise elements
        for selector in self.noise_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Find main content using semantic selectors
        main_content = ""
        content_source = "none"
        
        for selector in self.content_selectors:
            elements = soup.select(selector)
            if elements:
                main_content = elements[0].get_text(separator='\n', strip=True)
                content_source = selector
                break
        
        if not main_content:
            # Fallback to body content
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator='\n', strip=True)
                content_source = "body"
        
        # Extract metadata
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        
        return {
            "content": main_content,
            "title": title,
            "description": description,
            "content_source": content_source,
            "word_count": len(main_content.split()) if main_content else 0
        }

    async def _extract_with_readability(self, result, url: str) -> Dict:
        """Extract content using readability-style algorithm"""
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Score paragraphs based on text density and quality
        paragraphs = soup.find_all(['p', 'div', 'article', 'section'])
        scored_elements = []
        
        for element in paragraphs:
            text = element.get_text(strip=True)
            if len(text) < 25:  # Skip short elements
                continue
                
            score = self._calculate_element_score(element, text)
            if score > 0:
                scored_elements.append((element, score, text))
        
        # Sort by score and take top elements
        scored_elements.sort(key=lambda x: x[1], reverse=True)
        
        # Combine top-scoring elements
        main_content = ""
        for element, score, text in scored_elements[:10]:  # Top 10 elements
            if score > 5:  # Minimum quality threshold
                main_content += text + "\n\n"
        
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        
        return {
            "content": main_content.strip(),
            "title": title,
            "description": description,
            "content_source": "readability",
            "word_count": len(main_content.split()) if main_content else 0
        }

    async def _extract_with_text_density(self, result, url: str) -> Dict:
        """Extract content based on text density analysis"""
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Remove noise
        for selector in self.noise_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Find areas with highest text density
        text_blocks = []
        for element in soup.find_all(['div', 'section', 'article', 'main']):
            text = element.get_text(strip=True)
            if len(text) > 100:
                # Calculate text density (text length / HTML length)
                html_length = len(str(element))
                density = len(text) / html_length if html_length > 0 else 0
                text_blocks.append((text, density))
        
        # Sort by density and combine top blocks
        text_blocks.sort(key=lambda x: x[1], reverse=True)
        
        main_content = ""
        for text, density in text_blocks[:5]:  # Top 5 dense blocks
            if density > 0.1:  # Minimum density threshold
                main_content += text + "\n\n"
        
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        
        return {
            "content": main_content.strip(),
            "title": title,
            "description": description,
            "content_source": "text_density",
            "word_count": len(main_content.split()) if main_content else 0
        }

    async def _extract_with_raw_parsing(self, result, url: str) -> Dict:
        """Fallback: raw HTML parsing"""
        soup = BeautifulSoup(result.html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Get all text
        main_content = soup.get_text(separator='\n', strip=True)
        
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        
        return {
            "content": main_content,
            "title": title,
            "description": description,
            "content_source": "raw_parsing",
            "word_count": len(main_content.split()) if main_content else 0
        }

    def _calculate_element_score(self, element, text: str) -> int:
        """Calculate quality score for an HTML element"""
        score = 0
        
        # Length scoring
        word_count = len(text.split())
        if 25 <= word_count <= 500:
            score += 10
        elif word_count > 500:
            score += 5
        
        # Tag scoring
        tag_scores = {
            'article': 15, 'main': 15, 'section': 10,
            'div': 5, 'p': 8, 'h1': 12, 'h2': 10, 'h3': 8
        }
        score += tag_scores.get(element.name, 0)
        
        # Class/ID scoring
        class_names = ' '.join(element.get('class', []))
        id_name = element.get('id', '')
        
        positive_indicators = ['content', 'article', 'post', 'main', 'body']
        negative_indicators = ['nav', 'menu', 'sidebar', 'ad', 'comment', 'footer']
        
        for indicator in positive_indicators:
            if indicator in class_names.lower() or indicator in id_name.lower():
                score += 5
        
        for indicator in negative_indicators:
            if indicator in class_names.lower() or indicator in id_name.lower():
                score -= 10
        
        # Content quality indicators
        if re.search(r'\b(article|guide|tutorial|introduction)\b', text, re.I):
            score += 5
        
        return max(0, score)

    def _score_content_quality(self, text: str) -> int:
        """Score content quality"""
        if not text:
            return 0
        
        score = 0
        word_count = len(text.split())
        
        # Length scoring
        if 50 <= word_count <= 2000:
            score += 20
        elif word_count > 2000:
            score += 10
        elif word_count < 50:
            return 0
        
        # Sentence structure
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if 8 <= avg_sentence_length <= 30:
                score += 10
        
        # Content indicators
        quality_patterns = [
            r'\b(introduction|overview|summary|conclusion)\b',
            r'\b(first|second|third|finally)\b',
            r'\b(example|instance|case study)\b',
            r'\b(important|note|remember)\b'
        ]
        
        for pattern in quality_patterns:
            if re.search(pattern, text, re.I):
                score += 3
        
        return score

    def _extract_title(self, soup) -> str:
        """Extract page title"""
        # Try multiple title sources
        title_selectors = [
            'h1',
            'title',
            '.title',
            '.page-title',
            '.post-title',
            '.article-title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 5:
                    return title
        
        return "Untitled"

    def _extract_description(self, soup) -> str:
        """Extract page description"""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content']
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            text = first_p.get_text(strip=True)
            if len(text) > 20:
                return text[:200] + "..." if len(text) > 200 else text
        
        return ""

    def _get_content_extraction_js(self) -> str:
        """JavaScript code for enhanced content extraction"""
        return """
        // Enhanced content extraction
        function extractContentData() {
            const data = {
                title: document.title,
                headings: [],
                links: [],
                images: [],
                metadata: {}
            };
            
            // Extract headings
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            headings.forEach(h => {
                data.headings.push({
                    level: h.tagName,
                    text: h.textContent.trim(),
                    id: h.id || null
                });
            });
            
            // Extract important links
            const links = document.querySelectorAll('a[href]');
            links.forEach(link => {
                const href = link.getAttribute('href');
                const text = link.textContent.trim();
                if (href && text && text.length > 2) {
                    data.links.push({
                        href: href,
                        text: text,
                        isInternal: !href.startsWith('http') || href.includes(window.location.hostname)
                    });
                }
            });
            
            // Extract metadata
            const metaTags = document.querySelectorAll('meta');
            metaTags.forEach(meta => {
                const name = meta.getAttribute('name') || meta.getAttribute('property');
                const content = meta.getAttribute('content');
                if (name && content) {
                    data.metadata[name] = content;
                }
            });
            
            window.extractedContentData = data;
            return data;
        }
        
        extractContentData();
        """

    async def _apply_custom_instructions(self, content_data: Dict, instructions: str, url: str) -> Dict:
        """Apply custom extraction instructions using Gemini"""
        try:
            from google.generativeai import GenerativeModel
            import google.generativeai as genai
            import os
            
            # Configure Gemini
            api_key = os.getenv('GOOGLE_GENERATIVE_AI_API_KEY')
            if not api_key:
                print("Warning: No Gemini API key found, skipping custom instructions")
                return content_data
            
            genai.configure(api_key=api_key)
            model = GenerativeModel('gemini-2.0-flash-exp')
            
            prompt = f"""
            You are a content extraction specialist. I have scraped content from a webpage and need you to process it according to specific instructions.

            URL: {url}
            Original Content: {content_data.get('content', '')[:3000]}...

            User Instructions: {instructions}

            Please extract and structure the content according to the user's instructions. Return the result as clean, readable text focusing on the requested information.

            If the instructions ask for specific data points, structure them clearly.
            If no specific format is requested, clean and organize the content for better readability.
            """
            
            response = model.generate_content(prompt)
            
            if response and response.text:
                content_data['content'] = response.text
                content_data['custom_instructions_applied'] = True
                content_data['original_instructions'] = instructions
            
            return content_data
            
        except Exception as e:
            print(f"Error applying custom instructions: {e}")
            return content_data
