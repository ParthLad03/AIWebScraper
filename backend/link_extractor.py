"""
Intelligent link discovery and extraction
"""
import re
from typing import Dict, List, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class LinkExtractor:
    """Intelligent link discovery and categorization"""
    
    def __init__(self):
        self.navigation_selectors = [
            'nav a', 'navigation a', '.nav a', '.navbar a',
            '.navigation a', '.menu a', '.main-nav a',
            '.primary-nav a', '.site-nav a', '.top-nav a',
            '.header-nav a', '[role="navigation"] a',
            '.nav-menu a', '.menu-bar a', '.nav-bar a',
            'header nav a', 'header .nav a', 'header .menu a',
            '.header-menu a', '.site-header nav a',
            '.site-header .nav a', '.site-header .menu a'
        ]
        
        self.content_selectors = [
            'article a', 'main a', '.content a',
            '.post-content a', '.entry-content a',
            '.article-content a', '#content a',
            '.main-content a', '.page-content a'
        ]
        
        self.footer_selectors = [
            'footer a', '.footer a', '.site-footer a',
            '#footer a', '.page-footer a'
        ]

    def extract_all_links(self, html: str, base_url: str) -> Dict:
        """Extract and categorize all links from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        links = {
            'navigation': self._extract_navigation_links(soup, base_url),
            'content': self._extract_content_links(soup, base_url),
            'footer': self._extract_footer_links(soup, base_url),
            'external': self._extract_external_links(soup, base_url),
            'important': self._extract_important_links(soup, base_url),
            'social': self._extract_social_links(soup, base_url),
            'download': self._extract_download_links(soup, base_url)
        }
        
        # Add summary statistics
        links['summary'] = {
            'total_links': sum(len(category) for category in links.values() if isinstance(category, list)),
            'internal_links': len(links['navigation']) + len(links['content']) + len(links['footer']),
            'external_links': len(links['external']),
            'important_links': len(links['important'])
        }
        
        return links

    def _extract_navigation_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract navigation links with high priority"""
        nav_links = []
        processed_urls = set()
        
        for selector in self.navigation_selectors:
            for link in soup.select(selector):
                href = link.get('href')
                if not href:
                    continue
                
                full_url = self._normalize_url(href, base_url)
                if not full_url or full_url in processed_urls:
                    continue
                
                text = link.get_text(strip=True)
                if not text or len(text) > 100:  # Skip very long link texts
                    continue
                
                # Check if it's a valid navigation link
                if self._is_valid_navigation_link(text, href):
                    nav_links.append({
                        'url': full_url,
                        'text': text,
                        'selector': selector,
                        'priority': self._calculate_link_priority(text, href, 'navigation')
                    })
                    processed_urls.add(full_url)
        
        # Sort by priority
        nav_links.sort(key=lambda x: x['priority'], reverse=True)
        return nav_links

    def _extract_content_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract links from main content areas"""
        content_links = []
        processed_urls = set()
        
        for selector in self.content_selectors:
            for link in soup.select(selector):
                href = link.get('href')
                if not href:
                    continue
                
                full_url = self._normalize_url(href, base_url)
                if not full_url or full_url in processed_urls:
                    continue
                
                text = link.get_text(strip=True)
                if not text:
                    continue
                
                content_links.append({
                    'url': full_url,
                    'text': text,
                    'selector': selector,
                    'priority': self._calculate_link_priority(text, href, 'content')
                })
                processed_urls.add(full_url)
        
        # Sort by priority
        content_links.sort(key=lambda x: x['priority'], reverse=True)
        return content_links

    def _extract_footer_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract footer links"""
        footer_links = []
        processed_urls = set()
        
        for selector in self.footer_selectors:
            for link in soup.select(selector):
                href = link.get('href')
                if not href:
                    continue
                
                full_url = self._normalize_url(href, base_url)
                if not full_url or full_url in processed_urls:
                    continue
                
                text = link.get_text(strip=True)
                if not text or len(text) > 50:  # Footer links should be concise
                    continue
                
                footer_links.append({
                    'url': full_url,
                    'text': text,
                    'selector': selector,
                    'priority': self._calculate_link_priority(text, href, 'footer')
                })
                processed_urls.add(full_url)
        
        return footer_links

    def _extract_external_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract external links"""
        base_domain = urlparse(base_url).netloc
        external_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            parsed_href = urlparse(href)
            
            # Check if it's external
            if parsed_href.netloc and parsed_href.netloc != base_domain:
                text = link.get_text(strip=True)
                if text:
                    external_links.append({
                        'url': href,
                        'text': text,
                        'domain': parsed_href.netloc,
                        'type': self._classify_external_link(href, text)
                    })
        
        return external_links

    def _extract_important_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract links that are likely important based on context"""
        important_keywords = [
            'about', 'contact', 'services', 'products', 'pricing',
            'documentation', 'docs', 'api', 'guide', 'tutorial',
            'help', 'support', 'faq', 'download', 'get started',
            'sign up', 'register', 'login', 'dashboard'
        ]
        
        important_links = []
        processed_urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True).lower()
            
            # Check if link text contains important keywords
            is_important = any(keyword in text for keyword in important_keywords)
            
            # Check if link has important classes or IDs
            classes = ' '.join(link.get('class', [])).lower()
            link_id = link.get('id', '').lower()
            is_important = is_important or any(keyword in classes or keyword in link_id 
                                            for keyword in important_keywords)
            
            if is_important:
                full_url = self._normalize_url(href, base_url)
                if full_url and full_url not in processed_urls:
                    important_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True),
                        'reason': 'keyword_match',
                        'keywords_found': [kw for kw in important_keywords if kw in text]
                    })
                    processed_urls.add(full_url)
        
        return important_links

    def _extract_social_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract social media links"""
        social_domains = [
            'facebook.com', 'twitter.com', 'x.com', 'linkedin.com',
            'instagram.com', 'youtube.com', 'tiktok.com', 'pinterest.com',
            'snapchat.com', 'reddit.com', 'github.com', 'gitlab.com'
        ]
        
        social_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            parsed_href = urlparse(href)
            
            if any(domain in parsed_href.netloc for domain in social_domains):
                social_links.append({
                    'url': href,
                    'text': link.get_text(strip=True),
                    'platform': self._identify_social_platform(parsed_href.netloc)
                })
        
        return social_links

    def _extract_download_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract download links"""
        download_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.tar', '.gz', '.exe', '.dmg', '.pkg',
            '.mp3', '.mp4', '.avi', '.mov', '.wav', '.jpg', '.png', '.gif'
        ]
        
        download_links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True).lower()
            
            # Check if URL ends with download extension
            is_download = any(href.lower().endswith(ext) for ext in download_extensions)
            
            # Check if link text suggests download
            download_keywords = ['download', 'get', 'save', 'export', 'pdf', 'file']
            is_download = is_download or any(keyword in text for keyword in download_keywords)
            
            if is_download:
                full_url = self._normalize_url(href, base_url)
                if full_url:
                    download_links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True),
                        'file_type': self._get_file_type(href),
                        'size_estimate': self._estimate_file_size(link)
                    })
        
        return download_links

    def _normalize_url(self, href: str, base_url: str) -> str:
        """Normalize URL"""
        try:
            if not href:
                return None
            
            # Handle relative URLs
            if not urlparse(href).netloc:
                href = urljoin(base_url, href)
            
            # Clean up the URL
            parsed = urlparse(href)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                normalized += f"?{parsed.query}"
            
            # Remove trailing slashes for consistency
            if normalized.endswith('/') and len(normalized) > 1:
                normalized = normalized.rstrip('/')
            
            return normalized
        except Exception:
            return None

    def _is_valid_navigation_link(self, text: str, href: str) -> bool:
        """Check if a link is a valid navigation link"""
        # Skip very short or very long text
        if len(text) < 2 or len(text) > 50:
            return False
        
        # Skip links that are just URLs
        if href in text:
            return False
        
        # Skip links with special characters that suggest they're not navigation
        if re.search(r'[<>{}[\]\\]', text):
            return False
        
        return True

    def _calculate_link_priority(self, text: str, href: str, category: str) -> int:
        """Calculate link priority score"""
        score = 0
        
        # Base score by category
        category_scores = {
            'navigation': 10,
            'content': 5,
            'footer': 3
        }
        score += category_scores.get(category, 0)
        
        # Text length scoring (prefer medium-length descriptive text)
        text_len = len(text)
        if 5 <= text_len <= 30:
            score += 5
        elif 30 < text_len <= 50:
            score += 3
        
        # Important keywords
        important_keywords = [
            'about', 'services', 'products', 'contact', 'home',
            'documentation', 'guide', 'tutorial', 'help'
        ]
        
        for keyword in important_keywords:
            if keyword in text.lower():
                score += 3
        
        # Penalize certain patterns
        if re.search(r'^\d+$', text):  # Just numbers
            score -= 5
        
        if 'javascript:' in href or 'mailto:' in href:
            score -= 3
        
        return score

    def _classify_external_link(self, href: str, text: str) -> str:
        """Classify external link type"""
        domain = urlparse(href).netloc.lower()
        
        if any(social in domain for social in ['facebook', 'twitter', 'x.com', 'linkedin', 'instagram']):
            return 'social'
        elif any(code in domain for code in ['github', 'gitlab', 'bitbucket']):
            return 'code_repository'
        elif any(doc in domain for doc in ['docs.', 'documentation', 'wiki']):
            return 'documentation'
        elif 'news' in domain or 'blog' in domain:
            return 'news_blog'
        else:
            return 'general'

    def _identify_social_platform(self, domain: str) -> str:
        """Identify social media platform from domain"""
        social_map = {
            'facebook.com': 'Facebook',
            'twitter.com': 'Twitter',
            'x.com': 'X (Twitter)',
            'linkedin.com': 'LinkedIn',
            'instagram.com': 'Instagram',
            'youtube.com': 'YouTube',
            'tiktok.com': 'TikTok',
            'pinterest.com': 'Pinterest',
            'github.com': 'GitHub',
            'gitlab.com': 'GitLab'
        }
        
        for key, value in social_map.items():
            if key in domain:
                return value
        
        return domain

    def _get_file_type(self, href: str) -> str:
        """Get file type from URL"""
        parsed = urlparse(href)
        path = parsed.path.lower()
        
        if path.endswith('.pdf'):
            return 'PDF'
        elif path.endswith(('.doc', '.docx')):
            return 'Word Document'
        elif path.endswith(('.xls', '.xlsx')):
            return 'Excel Spreadsheet'
        elif path.endswith(('.ppt', '.pptx')):
            return 'PowerPoint Presentation'
        elif path.endswith(('.zip', '.rar', '.tar', '.gz')):
            return 'Archive'
        elif path.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return 'Image'
        elif path.endswith(('.mp3', '.wav')):
            return 'Audio'
        elif path.endswith(('.mp4', '.avi', '.mov')):
            return 'Video'
        else:
            return 'Unknown'

    def _estimate_file_size(self, link) -> str:
        """Estimate file size from link context"""
        # Look for size information in link text or nearby elements
        text = link.get_text(strip=True)
        
        # Common size patterns
        size_pattern = r'(\d+(?:\.\d+)?)\s*(KB|MB|GB|kb|mb|gb)'
        match = re.search(size_pattern, text, re.IGNORECASE)
        
        if match:
            return f"{match.group(1)} {match.group(2).upper()}"
        
        return "Unknown"

    def get_crawlable_links(self, links: Dict, max_links: int = 20) -> List[str]:
        """Get prioritized list of links suitable for crawling"""
        crawlable = []
        
        # Add navigation links (highest priority)
        nav_links = links.get('navigation', [])
        crawlable.extend([link['url'] for link in nav_links[:10]])
        
        # Add important links
        important_links = links.get('important', [])
        crawlable.extend([link['url'] for link in important_links[:5]])
        
        # Add content links
        content_links = links.get('content', [])
        crawlable.extend([link['url'] for link in content_links[:5]])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_crawlable = []
        for url in crawlable:
            if url not in seen:
                seen.add(url)
                unique_crawlable.append(url)
        
        return unique_crawlable[:max_links]
