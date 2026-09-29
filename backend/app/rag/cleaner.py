"""
Document Extraction, Normalization & Financial Text Cleaner.
Removes regulatory boilerplate, normalizes whitespace, formats tables, and cleans SEC filings.
"""
import re
from typing import Dict, Any


class DocumentCleaner:
    """Cleans and standardizes raw regulatory filings, PDF extracts, and earnings transcripts."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""

        # Normalize line endings and multiple spaces
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remove repetitive HTML/XML artifacts often found in EDGAR extracts
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = re.sub(r"&[a-zA-Z]+;", " ", cleaned)
        
        # Remove page numbers and standalone header artifacts (e.g., "Page 45 of 120", "Table of Contents")
        cleaned = re.sub(r"(?i)\bpage\s+\d+\s+(?:of\s+\d+)?\b", "", cleaned)
        cleaned = re.sub(r"(?i)\bTable\s+of\s+Contents\b", "", cleaned)
        
        # Collapse redundant whitespace while preserving paragraph breaks
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned)
        
        return cleaned.strip()

    @staticmethod
    def extract_sections(text: str) -> dict:
        """Extracts primary SEC 10-K sections such as Item 1, Item 1A, Item 7, Item 8."""
        patterns = {
            "Item 1. Business": r"(?i)Item\s+1\.\s+Business(.*?)(?=Item\s+1A|\Z)",
            "Item 1A. Risk Factors": r"(?i)Item\s+1A\.\s+Risk\s+Factors(.*?)(?=Item\s+1B|Item\s+2|\Z)",
            "Item 7. MD&A": r"(?i)Item\s+7\.\s+Management['’]s\s+Discussion(.*?)(?=Item\s+7A|Item\s+8|\Z)",
            "Item 8. Financial Statements": r"(?i)Item\s+8\.\s+Financial\s+Statements(.*?)(?=Item\s+9|\Z)"
        }
        sections = {}
        for sec_name, pat in patterns.items():
            match = re.search(pat, text, re.DOTALL)
            if match:
                sections[sec_name] = DocumentCleaner.clean_text(match.group(1))
        return sections


document_cleaner = DocumentCleaner()
