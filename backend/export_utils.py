"""
Export utilities for different formats
"""
import json
import csv
import io
from typing import Dict, List, Any
from datetime import datetime

class ExportUtils:
    """Utilities for exporting scraped data in various formats"""
    
    @staticmethod
    def to_json(data: Dict, pretty: bool = True) -> str:
        """Export data to JSON format"""
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        else:
            return json.dumps(data, ensure_ascii=False, default=str)
    
    @staticmethod
    def to_csv(data: Dict) -> str:
        """Export data to CSV format"""
        output = io.StringIO()
        
        # Determine if we have multiple pages or single page
        if isinstance(data, list):
            # Multiple pages
            ExportUtils._write_multiple_pages_csv(data, output)
        else:
            # Single page
            ExportUtils._write_single_page_csv(data, output)
        
        return output.getvalue()
    
    @staticmethod
    def _write_single_page_csv(data: Dict, output: io.StringIO):
        """Write single page data to CSV"""
        writer = csv.writer(output)
        
        # Write headers
        headers = [
            'URL', 'Title', 'Description', 'Content', 'Word Count',
            'Extraction Method', 'Quality Score', 'Important Links',
            'Navigation Links', 'External Links', 'Scraped At'
        ]
        writer.writerow(headers)
        
        # Extract important links
        important_links = ExportUtils._extract_important_links_text(data.get('links', {}))
        nav_links = ExportUtils._extract_nav_links_text(data.get('links', {}))
        external_links = ExportUtils._extract_external_links_text(data.get('links', {}))
        
        # Write data row
        row = [
            data.get('url', ''),
            data.get('title', ''),
            data.get('description', ''),
            data.get('cleaned_content', ''),
            data.get('word_count', 0),
            data.get('extraction_method', ''),
            data.get('quality_score', 0),
            important_links,
            nav_links,
            external_links,
            datetime.now().isoformat()
        ]
        writer.writerow(row)
    
    @staticmethod
    def _write_multiple_pages_csv(data: List[Dict], output: io.StringIO):
        """Write multiple pages data to CSV"""
        writer = csv.writer(output)
        
        # Write headers
        headers = [
            'URL', 'Title', 'Description', 'Content', 'Word Count',
            'Extraction Method', 'Quality Score', 'Important Links',
            'Navigation Links', 'External Links', 'Success', 'Error', 'Scraped At'
        ]
        writer.writerow(headers)
        
        # Write data rows
        for page_data in data:
            if page_data.get('success', False):
                important_links = ExportUtils._extract_important_links_text(page_data.get('links', {}))
                nav_links = ExportUtils._extract_nav_links_text(page_data.get('links', {}))
                external_links = ExportUtils._extract_external_links_text(page_data.get('links', {}))
                
                row = [
                    page_data.get('url', ''),
                    page_data.get('title', ''),
                    page_data.get('description', ''),
                    page_data.get('cleaned_content', ''),
                    page_data.get('word_count', 0),
                    page_data.get('extraction_method', ''),
                    page_data.get('quality_score', 0),
                    important_links,
                    nav_links,
                    external_links,
                    'Yes',
                    '',
                    datetime.now().isoformat()
                ]
            else:
                row = [
                    page_data.get('url', ''),
                    '', '', '', 0, '', 0, '', '', '',
                    'No',
                    page_data.get('error', ''),
                    datetime.now().isoformat()
                ]
            
            writer.writerow(row)
    
    @staticmethod
    def _extract_important_links_text(links: Dict) -> str:
        """Extract important links as text"""
        important = links.get('important', [])
        if not important:
            return ''
        
        link_texts = []
        for link in important[:5]:  # Limit to top 5
            text = link.get('text', '')
            url = link.get('url', '')
            if text and url:
                link_texts.append(f"{text} ({url})")
        
        return '; '.join(link_texts)
    
    @staticmethod
    def _extract_nav_links_text(links: Dict) -> str:
        """Extract navigation links as text"""
        nav = links.get('navigation', [])
        if not nav:
            return ''
        
        link_texts = []
        for link in nav[:10]:  # Limit to top 10
            text = link.get('text', '')
            url = link.get('url', '')
            if text and url:
                link_texts.append(f"{text} ({url})")
        
        return '; '.join(link_texts)
    
    @staticmethod
    def _extract_external_links_text(links: Dict) -> str:
        """Extract external links as text"""
        external = links.get('external', [])
        if not external:
            return ''
        
        link_texts = []
        for link in external[:5]:  # Limit to top 5
            text = link.get('text', '')
            url = link.get('url', '')
            if text and url:
                link_texts.append(f"{text} ({url})")
        
        return '; '.join(link_texts)
    
    @staticmethod
    def create_structured_export(data: Dict) -> Dict:
        """Create a structured export with organized data"""
        if isinstance(data, list):
            # Multiple pages
            return ExportUtils._create_multi_page_export(data)
        else:
            # Single page
            return ExportUtils._create_single_page_export(data)
    
    @staticmethod
    def _create_single_page_export(data: Dict) -> Dict:
        """Create structured export for single page"""
        export_data = {
            "metadata": {
                "scraped_at": datetime.now().isoformat(),
                "total_pages": 1,
                "successful_pages": 1 if data.get('success', False) else 0,
                "export_format": "structured_json"
            },
            "pages": [
                {
                    "url": data.get('url', ''),
                    "title": data.get('title', ''),
                    "description": data.get('description', ''),
                    "content": {
                        "cleaned_text": data.get('cleaned_content', ''),
                        "word_count": data.get('word_count', 0),
                        "quality_score": data.get('quality_score', 0),
                        "extraction_method": data.get('extraction_method', '')
                    },
                    "links": {
                        "important": data.get('links', {}).get('important', []),
                        "navigation": data.get('links', {}).get('navigation', []),
                        "external": data.get('links', {}).get('external', []),
                        "social": data.get('links', {}).get('social', []),
                        "download": data.get('links', {}).get('download', [])
                    },
                    "success": data.get('success', False),
                    "error": data.get('error', None)
                }
            ]
        }
        
        return export_data
    
    @staticmethod
    def _create_multi_page_export(data: List[Dict]) -> Dict:
        """Create structured export for multiple pages"""
        successful_pages = [page for page in data if page.get('success', False)]
        
        export_data = {
            "metadata": {
                "scraped_at": datetime.now().isoformat(),
                "total_pages": len(data),
                "successful_pages": len(successful_pages),
                "failed_pages": len(data) - len(successful_pages),
                "export_format": "structured_json"
            },
            "summary": {
                "total_word_count": sum(page.get('word_count', 0) for page in successful_pages),
                "average_quality_score": sum(page.get('quality_score', 0) for page in successful_pages) / len(successful_pages) if successful_pages else 0,
                "unique_domains": len(set(ExportUtils._get_domain(page.get('url', '')) for page in data)),
                "total_important_links": sum(len(page.get('links', {}).get('important', [])) for page in successful_pages)
            },
            "pages": []
        }
        
        for page_data in data:
            page_export = {
                "url": page_data.get('url', ''),
                "title": page_data.get('title', ''),
                "description": page_data.get('description', ''),
                "success": page_data.get('success', False)
            }
            
            if page_data.get('success', False):
                page_export.update({
                    "content": {
                        "cleaned_text": page_data.get('cleaned_content', ''),
                        "word_count": page_data.get('word_count', 0),
                        "quality_score": page_data.get('quality_score', 0),
                        "extraction_method": page_data.get('extraction_method', '')
                    },
                    "links": {
                        "important": page_data.get('links', {}).get('important', []),
                        "navigation": page_data.get('links', {}).get('navigation', []),
                        "external": page_data.get('links', {}).get('external', []),
                        "social": page_data.get('links', {}).get('social', []),
                        "download": page_data.get('links', {}).get('download', [])
                    }
                })
            else:
                page_export["error"] = page_data.get('error', 'Unknown error')
            
            export_data["pages"].append(page_export)
        
        return export_data
    
    @staticmethod
    def _get_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ''
