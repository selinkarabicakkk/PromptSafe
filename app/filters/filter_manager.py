"""Filter manager to handle and combine all filtering strategies."""
from typing import Dict, List, Optional, Tuple, Any

from app.core.config import settings
from app.filters.regex_filters import RegexFilter
# Conditional import for NER filter based on configuration
if settings.ENABLE_NER_FILTERS:
    try:
        from app.filters.ner_filters import NERFilter
    except ImportError:
        # Fallback if spacy or model not installed
        NERFilter = None
else:
    NERFilter = None


class FilterManager:
    """Manager class to handle all text filtering operations."""
    
    def __init__(self):
        """Initialize all available filters."""
        # Always initialize regex filters
        self.regex_filter = RegexFilter() if settings.ENABLE_REGEX_FILTERS else None
        
        # Initialize NER filter if enabled and available
        self.ner_filter = None
        if settings.ENABLE_NER_FILTERS and NERFilter is not None:
            try:
                self.ner_filter = NERFilter()
            except ImportError:
                # Log this error for the admin to fix
                print("UYARI: NER filtreleri için SpaCy model yüklü değil.")
    
    def filter_text(self, text: str) -> Tuple[str, List[Dict[str, Any]], bool]:
        """
        Apply all available filters to the text.
        
        Args:
            text: The text to filter
            
        Returns:
            Tuple[str, List[Dict], bool]:
                - Filtered text
                - List of masked elements
                - Whether sensitive content was detected
        """
        if not text:
            return "", [], False
            
        filtered_text = text
        all_masked_elements = []
        has_sensitive_content = False
        
        # Apply regex filtering first
        if self.regex_filter:
            filtered_text, masked_elements, has_regex_sensitive = self.regex_filter.filter_text(filtered_text)
            all_masked_elements.extend(masked_elements)
            has_sensitive_content = has_sensitive_content or has_regex_sensitive
        
        # Then apply NER filtering if available
        if self.ner_filter:
            filtered_text, masked_elements, has_ner_sensitive = self.ner_filter.filter_text(filtered_text)
            all_masked_elements.extend(masked_elements)
            has_sensitive_content = has_sensitive_content or has_ner_sensitive
        
        return filtered_text, all_masked_elements, has_sensitive_content


# Singleton instance for the application
filter_manager = FilterManager() 