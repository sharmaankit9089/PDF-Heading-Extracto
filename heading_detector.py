"""
Advanced Heading Detector - Robust heading detection for any PDF
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)

class HeadingDetector:
    """Intelligent heading detector using multiple heuristics for any PDF"""
    
    def __init__(self):
        # Initialize generic patterns for heading detection
        self._init_heading_patterns()
    
    def _init_heading_patterns(self):
        """Initialize patterns for generic heading detection"""
        
        # H1 patterns - Major sections
        self.h1_patterns = [
            r'^CHAPTER\s+\d+',
            r'^SECTION\s+\d+',
            r'^\d+\.\s+[A-Z][^.]*$',  # "1. Introduction"
            r'^[A-Z][A-Z\s]{3,}$',    # ALL CAPS headings
            r'^(Introduction|Overview|Summary|Conclusion|Abstract|Executive\s+Summary)',
            r'^(Background|Methodology|Results|Discussion|References|Bibliography)',
            r'^(Appendix\s+[A-Z]|Appendix\s+\d+)',
            r'^(Table\s+of\s+Contents|Acknowledgements?|Preface)',
            r'^(Revision\s+History|Document\s+History)',
        ]
        
        # H2 patterns - Section headings
        self.h2_patterns = [
            r'^\d+\.\d+\s+[A-Z]',     # "1.1 Subsection"
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]*)*\s*:?\s*$',  # "Background:", "Summary"
            r'^(Phase\s+[IVX]+|Phase\s+\d+)',
            r'^(Step\s+\d+|Stage\s+\d+)',
            r'^[A-Z][A-Za-z\s]{5,30}$',  # Mixed case headings
        ]
        
        # H3 patterns - Subsection headings
        self.h3_patterns = [
            r'^\d+\.\d+\.\d+\s+[A-Z]',   # "1.1.1 Sub-subsection"
            r'^[a-z]\)\s+[A-Z]',         # "a) Item"
            r'^[A-Z]\.\s+[A-Z]',         # "A. Item"
            r'^\d+\.\s+[A-Z][a-z]',      # "1. Preamble"
            r'^[A-Z][a-z]+\s*:\s*$',     # "Timeline:", "Access:"
            r'^(For\s+each|What\s+could|How\s+to)',
        ]
        
        # H4 patterns - Sub-subsection headings
        self.h4_patterns = [
            r'^\d+\.\d+\.\d+\.\d+\s+[A-Z]',  # "1.1.1.1 Deep subsection"
            r'^[a-z]\.\d+\s+[A-Z]',          # "a.1 Item"
            r'^[IVX]+\.\s+[A-Z]',            # "I. Roman numeral"
            r'^\([a-z]\)\s+[A-Z]',           # "(a) Parenthetical"
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = {
            "H1": [re.compile(p, re.IGNORECASE) for p in self.h1_patterns],
            "H2": [re.compile(p, re.IGNORECASE) for p in self.h2_patterns],
            "H3": [re.compile(p, re.IGNORECASE) for p in self.h3_patterns],
            "H4": [re.compile(p, re.IGNORECASE) for p in self.h4_patterns],
        }
    
    def detect_headings(self, text_elements: List[Dict]) -> List[Dict]:
        """
        Detect headings using multiple heuristics for any PDF
        """
        if not text_elements:
            return []
        
        # Analyze document structure
        font_analysis = self._analyze_fonts(text_elements)
        
        detected_headings = []
        
        for element in text_elements:
            text = element["text"].strip()
            page = element["page"]
            font_size = element.get("font_size", 12)
            font_flags = element.get("font_flags", 0)
            
            # Skip obvious non-headings
            if self._should_skip_text(text):
                continue
            
            # Multi-strategy heading detection
            level = self._detect_heading_level(text, font_size, font_flags, font_analysis)
            
            if level:
                cleaned_text = self._clean_heading_text(text)
                if cleaned_text:
                    detected_headings.append({
                        "level": level,
                        "text": cleaned_text,
                        "page": page
                    })
        
        # Sort by page and remove duplicates
        return self._finalize_headings(detected_headings)
    
    def _analyze_fonts(self, text_elements: List[Dict]) -> Dict:
        """Analyze font usage patterns in the document"""
        font_sizes = [elem.get("font_size", 12) for elem in text_elements]
        font_flags = [elem.get("font_flags", 0) for elem in text_elements]
        
        if not font_sizes:
            return {"avg_size": 12, "large_threshold": 14, "xlarge_threshold": 16}
        
        avg_size = sum(font_sizes) / len(font_sizes)
        sorted_sizes = sorted(set(font_sizes), reverse=True)
        
        # Determine size thresholds
        large_threshold = avg_size + 2
        xlarge_threshold = avg_size + 4
        
        if len(sorted_sizes) >= 3:
            xlarge_threshold = sorted_sizes[0] if sorted_sizes[0] > avg_size + 2 else avg_size + 4
            large_threshold = sorted_sizes[1] if sorted_sizes[1] > avg_size + 1 else avg_size + 2
        
        return {
            "avg_size": avg_size,
            "large_threshold": large_threshold,
            "xlarge_threshold": xlarge_threshold,
            "sizes": sorted_sizes
        }
    
    def _detect_heading_level(self, text: str, font_size: float, font_flags: int, font_analysis: Dict) -> Optional[str]:
        """Detect heading level using multiple strategies"""
        
        # Strategy 1: Pattern matching (highest priority)
        for level in ["H1", "H2", "H3", "H4"]:
            for pattern in self.compiled_patterns[level]:
                if pattern.match(text):
                    return level
        
        # Strategy 2: Font-based detection
        font_level = self._classify_by_font(text, font_size, font_flags, font_analysis)
        if font_level:
            return font_level
        
        # Strategy 3: Structural analysis
        structure_level = self._classify_by_structure(text)
        if structure_level:
            return structure_level
        
        # Strategy 4: Content-based classification
        content_level = self._classify_by_content(text)
        if content_level:
            return content_level
        
        return None
    
    def _classify_by_font(self, text: str, font_size: float, font_flags: int, font_analysis: Dict) -> Optional[str]:
        """Classify heading level based on font properties"""
        is_bold = bool(font_flags & 2**4)
        is_large = font_size >= font_analysis["large_threshold"]
        is_xlarge = font_size >= font_analysis["xlarge_threshold"]
        
        # Very large fonts are likely H1
        if is_xlarge and (is_bold or len(text) < 60):
            return "H1"
        
        # Large fonts with bold are likely H2
        if is_large and is_bold and len(text) < 80:
            return "H2"
        
        # Moderately large fonts might be H3
        if font_size > font_analysis["avg_size"] + 1 and len(text) < 100:
            return "H3"
        
        return None
    
    def _classify_by_structure(self, text: str) -> Optional[str]:
        """Classify based on structural patterns"""
        
        # Numbered sections
        if re.match(r'^\d+\.\s+[A-Z]', text):
            return "H1"
        elif re.match(r'^\d+\.\d+\s+[A-Z]', text):
            return "H2"
        elif re.match(r'^\d+\.\d+\.\d+\s+[A-Z]', text):
            return "H3"
        elif re.match(r'^\d+\.\d+\.\d+\.\d+\s+[A-Z]', text):
            return "H4"
        
        # Lettered sections
        if re.match(r'^[A-Z]\.\s+[A-Z]', text):
            return "H2"
        elif re.match(r'^[a-z]\)\s+[A-Z]', text):
            return "H3"
        elif re.match(r'^\([a-z]\)\s+[A-Z]', text):
            return "H4"
        
        return None
    
    def _classify_by_content(self, text: str) -> Optional[str]:
        """Classify based on content and context"""
        
        # All caps short text is likely a major heading
        if text.isupper() and 5 <= len(text) <= 50:
            return "H1"
        
        # Title case with colon suggests section heading
        if re.match(r'^[A-Z][a-z]+.*:\s*$', text):
            return "H2"
        
        # Questions might be subsection headings
        if text.endswith('?') and len(text) < 100:
            return "H3"
        
        # Common heading words
        h1_words = ['introduction', 'overview', 'summary', 'conclusion', 'abstract', 'preface']
        h2_words = ['background', 'methodology', 'results', 'discussion', 'analysis']
        h3_words = ['timeline', 'objectives', 'requirements', 'specifications']
        
        text_lower = text.lower()
        
        for word in h1_words:
            if word in text_lower and len(text) < 50:
                return "H1"
        
        for word in h2_words:
            if word in text_lower and len(text) < 80:
                return "H2"
        
        for word in h3_words:
            if word in text_lower and len(text) < 100:
                return "H3"
        
        return None
    
    def _should_skip_text(self, text: str) -> bool:
        """Determine if text should be skipped as non-heading"""
        
        # Skip very short or very long text
        if len(text) < 3 or len(text) > 200:
            return True
        
        # Skip obvious page artifacts
        skip_patterns = [
            r'^\s*\d+\s*$',  # Just page numbers
            r'^Page\s+\d+',
            r'^©\s*\d{4}',
            r'^Copyright',
            r'^www\.|^http',
            r'^\w+@\w+\.\w+',  # Email addresses
            r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # Dates
            r'^Figure\s+\d+',
            r'^Table\s+\d+',
            r'^Chart\s+\d+',
            r'^Version\s+\d+\.\d+',
            r'^Draft\s+\d+',
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        # Skip body text (contains many common words and punctuation)
        common_words = ["the", "and", "of", "to", "in", "for", "with", "on", "at", "by", "a", "an"]
        word_count = sum(1 for word in common_words if word in text.lower().split())
        
        # If text has many common words and is long, it's likely body text
        if word_count >= 4 and len(text) > 50:
            return True
        
        # Skip text with multiple sentences
        if text.count('.') >= 2 and len(text) > 40:
            return True
        
        return False
    
    def _clean_heading_text(self, text: str) -> str:
        """Clean and normalize heading text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common artifacts
        text = re.sub(r'^\s*[•\-\*]\s*', '', text)  # Remove bullet points
        text = re.sub(r'\s*[.]{2,}\s*\d*\s*$', '', text)  # Remove trailing dots and page numbers
        
        # Ensure proper capitalization for certain patterns
        if re.match(r'^\d+\.\s+[a-z]', text):
            # Capitalize first letter after numbering
            text = re.sub(r'^(\d+\.\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        return text.strip()
    
    def _finalize_headings(self, headings: List[Dict]) -> List[Dict]:
        """Final processing and deduplication"""
        if not headings:
            return []
        
        # Remove duplicates while preserving order
        seen = set()
        unique_headings = []
        
        for heading in headings:
            # Create a key for deduplication
            key = (heading["text"].lower().strip(), heading["page"])
            if key not in seen:
                seen.add(key)
                unique_headings.append(heading)
        
        # Sort by page number, then by hierarchical level
        level_order = {"H1": 1, "H2": 2, "H3": 3, "H4": 4}
        unique_headings.sort(key=lambda h: (h["page"], level_order.get(h["level"], 5)))
        
        # Validate hierarchy (optional - ensure logical heading progression)
        validated_headings = self._validate_hierarchy(unique_headings)
        
        return validated_headings
    
    def _validate_hierarchy(self, headings: List[Dict]) -> List[Dict]:
        """Validate and adjust heading hierarchy if needed"""
        if not headings:
            return []
        
        validated = []
        last_level = 0
        level_map = {"H1": 1, "H2": 2, "H3": 3, "H4": 4}
        
        for heading in headings:
            current_level = level_map[heading["level"]]
            
            # If we jump more than one level, adjust
            if current_level > last_level + 1 and last_level > 0:
                # Don't adjust - keep original classification as it might be correct
                pass
            
            validated.append(heading)
            last_level = current_level
        
        return validated