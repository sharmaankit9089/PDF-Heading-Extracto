"""
Enhanced PDF Processor - Robust PDF processing and outline extraction
Works for any PDF files within 50 pages
"""

import fitz  # PyMuPDF
import re
import logging
from typing import Dict, List, Optional
from collections import Counter
from heading_detector import HeadingDetector

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Enhanced PDF processing class for extracting document outlines"""
    
    def __init__(self):
        self.heading_detector = HeadingDetector()
    
    def extract_outline(self, pdf_path: str) -> Dict:
        """
        Extract outline from PDF file with comprehensive error handling
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            Dict: Extracted outline in required JSON format
        """
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Check page count constraint
            if len(doc) > 50:
                logger.warning(f"PDF has {len(doc)} pages, exceeding 50 page limit")
            
            # Extract title and outline
            title = self._extract_title(doc, pdf_path)
            outline = self._extract_headings(doc)
            
            # Close document
            doc.close()
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise
    
    def _extract_title(self, doc: fitz.Document, pdf_path: str) -> str:
        """
        Extract document title using multiple strategies for any PDF
        """
        if len(doc) == 0:
            return ""
        
        # Strategy 1: Check PDF metadata first
        try:
            metadata = doc.metadata
            if metadata and 'title' in metadata and metadata['title']:
                metadata_title = metadata['title'].strip()
                if metadata_title and len(metadata_title) > 3 and not self._is_generic_metadata_title(metadata_title):
                    return self._clean_title_text(metadata_title)
        except:
            pass
        
        # Strategy 2: Analyze first page for title using font analysis
        try:
            first_page = doc[0]
            text_dict = first_page.get_text("dict")
            
            title_candidates = []
            
            # Extract text elements with properties
            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text and len(text) > 3:
                            # Calculate title score based on font properties and position
                            score = self._calculate_title_score(span, text, block)
                            if score > 15:  # Minimum threshold for title candidates
                                title_candidates.append((text, score))
            
            # Return best candidate if found
            if title_candidates:
                title_candidates.sort(key=lambda x: x[1], reverse=True)
                best_title = title_candidates[0][0]
                cleaned_title = self._clean_title_text(best_title)
                if len(cleaned_title) > 5:  # Ensure it's substantial enough
                    return cleaned_title
        
        except Exception as e:
            logger.warning(f"Error extracting title from first page: {e}")
        
        # Strategy 3: Use table of contents if available
        try:
            toc = doc.get_toc()
            if toc and len(toc) > 0:
                first_toc = toc[0]
                if len(first_toc) >= 2:
                    toc_title = first_toc[1].strip()
                    if 5 <= len(toc_title) <= 100:
                        return self._clean_title_text(toc_title)
        except:
            pass
        
        # Strategy 4: Look for title-like patterns in first few text blocks
        try:
            first_page = doc[0]
            blocks = first_page.get_text("dict")["blocks"]
            
            # Collect all text from first page
            all_text_elements = []
            for block in blocks[:10]:  # Check first 10 blocks
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text and len(text) > 5:
                                all_text_elements.append(text)
            
            # Look for common title patterns
            for text in all_text_elements[:5]:  # Check first 5 text elements
                if self._looks_like_title(text):
                    return self._clean_title_text(text)
        
        except Exception as e:
            logger.warning(f"Error in title pattern search: {e}")
        
        return ""
    
    def _is_generic_metadata_title(self, title: str) -> bool:
        """Check if metadata title is too generic/unhelpful"""
        generic_patterns = [
            r'^Microsoft\s+Word',
            r'^Document\d*$',
            r'^Untitled',
            r'^\.pdf$',
            r'^\w+\.pdf$',
            r'^Page\s+\d+',
            r'^Draft',
            r'^Copy\s+of',
        ]
        
        for pattern in generic_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return True
        return False
    
    def _calculate_title_score(self, span: Dict, text: str, block: Dict) -> float:
        """Calculate title candidacy score for text element"""
        score = 0.0
        
        # Font size score (larger = better for titles)
        font_size = span.get("size", 12)
        if font_size >= 18:
            score += 40
        elif font_size >= 16:
            score += 30
        elif font_size >= 14:
            score += 20
        else:
            score += font_size
        
        # Position score (higher on page = better for titles)
        bbox = block.get("bbox", [0, 0, 0, 0])
        y_pos = bbox[1] if len(bbox) > 1 else 0
        if y_pos < 150:  # Top of page
            score += 30
        elif y_pos < 300:  # Upper portion
            score += 15
        
        # Font weight score
        flags = span.get("flags", 0)
        if flags & 2**4:  # Bold
            score += 20
        if flags & 2**1:  # Italic
            score += 5
        
        # Text characteristics
        text_len = len(text)
        if 10 <= text_len <= 80:  # Good title length
            score += 15
        elif text_len > 150:  # Too long for title
            score -= 20
        elif text_len < 5:  # Too short
            score -= 10
        
        # Penalize obvious non-titles
        if re.search(r'^\d+$|^Page\s+|^©|^www\.|^http|^\s*\d+\s*$|^[A-Z]{1,3}\s*$', text, re.IGNORECASE):
            score -= 50
        
        # Boost for title-like patterns
        title_indicators = [
            r'^(RFP|Request|Understanding|Introduction|Overview|Application|Report|Analysis|Study|Guide|Manual)',
            r'(Report|Analysis|Study|Guide|Manual|Plan|Strategy|Framework|Policy|Proposal)$',
            r':\s*[A-Z]',  # Contains colon followed by capital letter
        ]
        
        for pattern in title_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                score += 15
                break
        
        # Penalize body text patterns
        if text.count('.') >= 2:  # Multiple sentences
            score -= 25
        
        common_words = ["the", "and", "of", "to", "in", "for", "with", "on", "at", "by", "a", "an"]
        word_count = sum(1 for word in common_words if word in text.lower().split())
        if word_count >= 4:  # Too many common words
            score -= 15
        
        return score
    
    def _looks_like_title(self, text: str) -> bool:
        """Check if text looks like a document title"""
        # Good length for titles
        if not (5 <= len(text) <= 150):
            return False
        
        # Title-like patterns
        title_patterns = [
            r'^[A-Z][^.]*[^.]$',  # Starts with capital, no ending period
            r'.*:\s*[A-Z].*',     # Contains colon
            r'^(RFP|Request|Application|Report|Analysis|Study|Guide|Manual|Plan|Strategy)',
            r'.*(Report|Analysis|Study|Guide|Manual|Plan|Strategy|Framework|Policy|Proposal).*',
        ]
        
        for pattern in title_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        # Avoid obvious non-titles
        non_title_patterns = [
            r'^\d+$',
            r'^Page\s+\d+',
            r'^[a-z]',  # Starts with lowercase
            r'.*[.!?]\s+[A-Z].*',  # Multiple sentences
        ]
        
        for pattern in non_title_patterns:
            if re.match(pattern, text):
                return False
        
        return False
    
    def _clean_title_text(self, title: str) -> str:
        """Clean and normalize title text"""
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Remove common prefixes but keep meaningful ones
        prefixes_to_remove = [
            r'^(Document:|Report:|Title:)\s*',
            r'^Microsoft\s+Word\s*-\s*',
        ]
        
        for prefix in prefixes_to_remove:
            title = re.sub(prefix, '', title, flags=re.IGNORECASE)
        
        # Remove trailing artifacts
        title = re.sub(r'[.]{2,}$|^\s*[.]+\s*', '', title)
        title = re.sub(r'\s*\.pdf\s*$', '', title, flags=re.IGNORECASE)
        
        return title.strip()
    
    def _extract_headings(self, doc: fitz.Document) -> List[Dict]:
        """
        Extract hierarchical headings from PDF document
        """
        if len(doc) == 0:
            return []
        
        all_text_elements = []
        
        # Extract text elements from all pages
        for page_num in range(min(len(doc), 50)):  # Respect 50 page limit
            try:
                page = doc[page_num]
                page_elements = self._extract_page_text_elements(page, page_num)
                all_text_elements.extend(page_elements)
            except Exception as e:
                logger.warning(f"Error processing page {page_num + 1}: {e}")
                continue
        
        logger.info(f"Extracted {len(all_text_elements)} text elements from PDF")
        
        # Filter elements for heading detection
        filtered_elements = self._filter_heading_candidates(all_text_elements)
        logger.info(f"Filtered to {len(filtered_elements)} potential heading candidates")
        
        # Detect headings using enhanced algorithms
        headings = self.heading_detector.detect_headings(filtered_elements)
        
        logger.info(f"Detected {len(headings)} headings")
        return headings
    
    def _extract_page_text_elements(self, page: fitz.Page, page_num: int) -> List[Dict]:
        """Extract text elements with formatting from a single page"""
        elements = []
        
        try:
            # Get text with formatting information
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                
                # Process each line to preserve formatting
                for line in block["lines"]:
                    line_texts = []
                    line_sizes = []
                    line_flags = []
                    line_fonts = []
                    
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            line_texts.append(text)
                            line_sizes.append(span.get("size", 12))
                            line_flags.append(span.get("flags", 0))
                            line_fonts.append(span.get("font", ""))
                    
                    if line_texts:
                        # Combine text spans into single line
                        combined_text = " ".join(line_texts)
                        
                        # Calculate representative font properties
                        avg_size = sum(line_sizes) / len(line_sizes) if line_sizes else 12
                        max_flags = max(line_flags) if line_flags else 0
                        primary_font = line_fonts[0] if line_fonts else ""
                        
                        elements.append({
                            "text": combined_text,
                            "page": page_num,  # 0-based page numbering
                            "font_size": avg_size,
                            "font_flags": max_flags,
                            "font_name": primary_font,
                            "bbox": line.get("bbox", [0, 0, 0, 0])
                        })
        
        except Exception as e:
            logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
        
        return elements
    
    def _filter_heading_candidates(self, elements: List[Dict]) -> List[Dict]:
        """Filter text elements to find potential headings"""
        candidates = []
        
        for element in elements:
            text = element["text"].strip()
            
            # Skip empty or very short text
            if len(text) < 3:
                continue
            
            # Skip obvious page artifacts
            if self._is_page_artifact(text):
                continue
            
            # Skip very long text blocks (likely body text)
            if len(text) > 250:
                continue
            
            # Skip obvious body text patterns
            if self._is_body_text(text):
                continue
            
            candidates.append(element)
        
        return candidates
    
    def _is_page_artifact(self, text: str) -> bool:
        """Check if text is a page artifact (headers, footers, page numbers)"""
        artifact_patterns = [
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
        ]
        
        for pattern in artifact_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _is_body_text(self, text: str) -> bool:
        """Check if text appears to be body content rather than a heading"""
        # Multiple sentences suggest body text
        if text.count('.') >= 2 and len(text) > 50:
            return True
        
        # Common body text indicators
        common_words = ["the", "and", "of", "to", "in", "for", "with", "on", "at", "by"]
        word_count = sum(1 for word in common_words if word in text.lower().split())
        
        if word_count >= 3 and len(text) > 40:
            return True
        
        # Lowercase text (except specific patterns) suggests body content
        if text.islower() and not re.match(r'^[a-z]\)', text):
            return True
        
        return False
