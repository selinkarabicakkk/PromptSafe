"""Filter unit tests."""
import pytest

from app.filters.regex_filters import RegexFilter


class TestRegexFilters:
    """Test class for regex based filters."""

    def test_api_key_detection(self):
        """Test API key detection in text."""
        filter_engine = RegexFilter()
        test_text = "My OpenAI API key is sk-abcdefghi1234567890abcdefghi1234567890abcdefghi1234"
        
        filtered_text, masked_elements, has_sensitive = filter_engine.filter_text(test_text)
        
        assert has_sensitive is True
        assert "[OPENAI_API_KEY]" in filtered_text
        assert "sk-abcdefghi1234567890abcdefghi1234567890abcdefghi1234" not in filtered_text
        assert len(masked_elements) == 1
    
    def test_email_detection(self):
        """Test email detection in text."""
        filter_engine = RegexFilter()
        test_text = "Please contact me at test.user@example.com for more information."
        
        filtered_text, masked_elements, has_sensitive = filter_engine.filter_text(test_text)
        
        assert has_sensitive is True
        assert "[EMAIL]" in filtered_text
        assert "test.user@example.com" not in filtered_text
        assert len(masked_elements) == 1
        
    def test_credit_card_detection(self):
        """Test credit card number detection."""
        filter_engine = RegexFilter()
        test_text = "My credit card number is 4532-1234-5678-9012 and expires on 12/24."
        
        filtered_text, masked_elements, has_sensitive = filter_engine.filter_text(test_text)
        
        assert has_sensitive is True
        assert "[CREDIT_CARD]" in filtered_text
        assert "4532-1234-5678-9012" not in filtered_text
        
    def test_multiple_sensitive_elements(self):
        """Test detection of multiple sensitive elements in same text."""
        filter_engine = RegexFilter()
        test_text = (
            "My name is John Doe, email is john.doe@example.com, "
            "AWS key is AKIAIOSFODNN7EXAMPLE, and "
            "credit card is 4111 1111 1111 1111."
        )
        
        filtered_text, masked_elements, has_sensitive = filter_engine.filter_text(test_text)
        
        assert has_sensitive is True
        assert "[EMAIL]" in filtered_text
        assert "[AWS_ACCESS_KEY]" in filtered_text
        assert "[CREDIT_CARD]" in filtered_text
        assert len(masked_elements) == 3
        
    def test_no_sensitive_data(self):
        """Test case with no sensitive data."""
        filter_engine = RegexFilter()
        test_text = "This is a normal text without any sensitive information."
        
        filtered_text, masked_elements, has_sensitive = filter_engine.filter_text(test_text)
        
        assert has_sensitive is False
        assert filtered_text == test_text
        assert len(masked_elements) == 0 