"""
Advanced content cleaning pipeline
"""
import re
from typing import List, Dict
from bs4 import BeautifulSoup

class ContentCleaner:
    """Advanced content cleaning and processing"""
    
    def __init__(self):
        self.web_artifacts = [
            r'Cookie\s+Policy.*?Accept',
            r'Privacy\s+Policy.*?Accept',
            r'This website uses cookies.*?Accept',
            r'Skip to (main )?content',
            r'Loading\.{3,}',
            r'Please enable JavaScript',
            r'Share on (Facebook|Twitter|LinkedIn|Instagram)',
            r'Follow us on',
            r'Subscribe to our newsletter',
            r'Sign up for updates',
            r'Advertisement',
            r'Sponsored content',
            r'Related articles?',
            r'You might also like',
            r'More from this author',
            r'Tags?:',
            r'Categories?:',
            r'Posted (on|by)',
            r'Published (on|by)',
            r'Last updated',
            r'Read more',
            r'Continue reading',
            r'Click here',
            r'Learn more',
            r'Get started',
            r'Try (it )?now',
            r'Download (now|here)',
            r'Buy now',
            r'Order now',
            r'Contact us',
            r'Call us',
            r'Email us'
        ]
        
        self.navigation_patterns = [
            r'^(Home|About|Contact|Services|Products|Blog|News|FAQ)$',
            r'^(Login|Register|Sign up|Sign in)$',
            r'^(Menu|Navigation|Breadcrumb)$',
            r'^(Previous|Next|Back|Forward)$',
            r'^(Page \d+|Go to page)$'
        ]

    def clean_content_pipeline(self, content: str) -> Dict:
        """Complete content cleaning pipeline"""
        if not content:
            return {
                "cleaned_content": "",
                "word_count": 0,
                "cleaning_steps": [],
                "quality_score": 0
            }
        
        cleaning_steps = []
        original_length = len(content)
        
        # Step 1: Basic whitespace cleaning
        content = self._clean_whitespace(content)
        cleaning_steps.append(f"Whitespace cleaning: {original_length} → {len(content)} chars")
        
        # Step 2: Remove web artifacts
        content = self._remove_web_artifacts(content)
        cleaning_steps.append(f"Web artifacts removal: → {len(content)} chars")
        
        # Step 3: Remove navigation elements
        content = self._remove_navigation_elements(content)
        cleaning_steps.append(f"Navigation removal: → {len(content)} chars")
        
        # Step 4: Quality filtering
        content = self._filter_quality_lines(content)
        cleaning_steps.append(f"Quality filtering: → {len(content)} chars")
        
        # Step 5: Structure improvement
        content = self._improve_structure(content)
        cleaning_steps.append(f"Structure improvement: → {len(content)} chars")
        
        # Step 6: Final cleanup
        content = self._final_cleanup(content)
        cleaning_steps.append(f"Final cleanup: → {len(content)} chars")
        
        word_count = len(content.split()) if content else 0
        quality_score = self._calculate_quality_score(content)
        
        return {
            "cleaned_content": content,
            "word_count": word_count,
            "cleaning_steps": cleaning_steps,
            "quality_score": quality_score,
            "reduction_ratio": (original_length - len(content)) / original_length if original_length > 0 else 0
        }

    def _clean_whitespace(self, content: str) -> str:
        """Clean up whitespace while preserving structure"""
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Multiple newlines → double newline
        content = re.sub(r'[ \t]+', ' ', content)             # Multiple spaces → single space
        content = re.sub(r' *\n *', '\n', content)            # Spaces around newlines
        
        return content.strip()

    def _remove_web_artifacts(self, content: str) -> str:
        """Remove common web artifacts and UI elements"""
        for pattern in self.web_artifacts:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove markdown-style links but keep the text
        content = re.sub(r'\[([^\]]+)\]$$[^)]+$$', r'\1', content)
        
        # Remove URLs that appear as standalone text
        content = re.sub(r'https?://[^\s]+', '', content)
        
        # Remove email addresses that appear as standalone text
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
        
        return content

    def _remove_navigation_elements(self, content: str) -> str:
        """Remove navigation and menu elements"""
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip navigation patterns
            is_navigation = False
            for pattern in self.navigation_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_navigation = True
                    break
            
            if not is_navigation:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

    def _filter_quality_lines(self, content: str) -> str:
        """Filter lines based on content quality"""
        lines = content.split('\n')
        quality_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip very short lines (likely navigation or labels)
            if len(line) < 10:
                continue
            
            # Skip very long lines (likely URLs or code)
            if len(line) > 500:
                continue
            
            # Skip lines that are mostly punctuation/symbols
            alpha_ratio = len(re.sub(r'[^a-zA-Z]', '', line)) / len(line)
            if alpha_ratio < 0.3:
                continue
            
            # Skip lines that look like metadata
            metadata_patterns = [
                r'^(Posted|Published|Updated|Modified|Created|By|Author|Date|Time):',
                r'^(Tags?|Categories?|Filed under):',
                r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # Dates
                r'^\d{1,2}:\d{2}(\s?(AM|PM))?',      # Times
            ]
            
            is_metadata = False
            for pattern in metadata_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_metadata = True
                    break
            
            if not is_metadata:
                quality_lines.append(line)
        
        return '\n'.join(quality_lines)

    def _improve_structure(self, content: str) -> str:
        """Improve content structure and readability"""
        lines = content.split('\n')
        structured_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Add spacing before headings (lines that look like titles)
            if self._looks_like_heading(line) and structured_lines:
                structured_lines.append('')  # Add blank line before heading
            
            structured_lines.append(line)
            
            # Add spacing after headings
            if self._looks_like_heading(line) and i < len(lines) - 1:
                next_line = lines[i + 1].strip()
                if next_line and not self._looks_like_heading(next_line):
                    structured_lines.append('')  # Add blank line after heading
        
        return '\n'.join(structured_lines)

    def _looks_like_heading(self, line: str) -> bool:
        """Check if a line looks like a heading"""
        # Short lines that end with colon or are all caps
        if len(line) < 100 and (line.endswith(':') or line.isupper()):
            return True
        
        # Lines that start with numbers (like "1. Introduction")
        if re.match(r'^\d+\.?\s+[A-Z]', line):
            return True
        
        # Lines that are title case and relatively short
        if len(line) < 80 and line.istitle():
            return True
        
        return False

    def _final_cleanup(self, content: str) -> str:
        """Final cleanup and normalization"""
        # Remove excessive blank lines
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Ensure sentences end with proper punctuation
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Add period if line doesn't end with punctuation and looks like a sentence
                if (len(line) > 20 and 
                    not line[-1] in '.!?:;' and 
                    not line.endswith('...') and
                    ' ' in line):
                    line += '.'
                cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Final whitespace cleanup
        return content.strip()

    def _calculate_quality_score(self, content: str) -> int:
        """Calculate overall content quality score"""
        if not content:
            return 0
        
        score = 0
        word_count = len(content.split())
        
        # Length scoring
        if 100 <= word_count <= 3000:
            score += 30
        elif word_count > 3000:
            score += 20
        elif 50 <= word_count < 100:
            score += 10
        
        # Structure scoring
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if lines:
            avg_line_length = sum(len(line) for line in lines) / len(lines)
            if 30 <= avg_line_length <= 150:
                score += 20
        
        # Content diversity scoring
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if 8 <= avg_sentence_length <= 25:
                score += 20
        
        # Vocabulary richness
        words = content.lower().split()
        unique_words = set(words)
        if words:
            vocabulary_ratio = len(unique_words) / len(words)
            if vocabulary_ratio > 0.3:
                score += 15
        
        # Content indicators
        quality_indicators = [
            r'\b(introduction|overview|summary|conclusion)\b',
            r'\b(important|significant|key|main|primary)\b',
            r'\b(example|instance|case|study)\b',
            r'\b(first|second|third|finally|lastly)\b'
        ]
        
        for pattern in quality_indicators:
            if re.search(pattern, content, re.I):
                score += 5
        
        return min(100, score)  # Cap at 100

    def extract_key_information(self, content: str) -> Dict:
        """Extract key information from cleaned content"""
        if not content:
            return {}
        
        info = {
            "key_phrases": self._extract_key_phrases(content),
            "headings": self._extract_headings(content),
            "bullet_points": self._extract_bullet_points(content),
            "numbers_and_stats": self._extract_numbers_and_stats(content),
            "dates": self._extract_dates(content)
        }
        
        return info

    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content"""
        # Simple key phrase extraction based on capitalization and frequency
        phrases = []
        
        # Find capitalized phrases (potential proper nouns/important terms)
        capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        phrases.extend(capitalized_phrases[:10])  # Top 10
        
        return list(set(phrases))

    def _extract_headings(self, content: str) -> List[str]:
        """Extract potential headings from content"""
        lines = content.split('\n')
        headings = []
        
        for line in lines:
            line = line.strip()
            if self._looks_like_heading(line):
                headings.append(line)
        
        return headings

    def _extract_bullet_points(self, content: str) -> List[str]:
        """Extract bullet points and list items"""
        bullet_patterns = [
            r'^\s*[-•*]\s+(.+)$',
            r'^\s*\d+\.\s+(.+)$',
            r'^\s*[a-zA-Z]\.\s+(.+)$'
        ]
        
        bullet_points = []
        for line in content.split('\n'):
            for pattern in bullet_patterns:
                match = re.match(pattern, line)
                if match:
                    bullet_points.append(match.group(1).strip())
                    break
        
        return bullet_points

    def _extract_numbers_and_stats(self, content: str) -> List[str]:
        """Extract numbers, percentages, and statistics"""
        number_patterns = [
            r'\b\d+%\b',  # Percentages
            r'\b\d+\.\d+%\b',  # Decimal percentages
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?\b',  # Money
            r'\b\d+(?:,\d{3})*\b',  # Large numbers with commas
        ]
        
        numbers = []
        for pattern in number_patterns:
            matches = re.findall(pattern, content)
            numbers.extend(matches)
        
        return list(set(numbers))

    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates from content"""
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))
