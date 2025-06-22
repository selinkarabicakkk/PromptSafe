"""Regex pattern based filters for sensitive data."""
import re
from typing import Dict, List, Tuple, Pattern


# API Anahtarları ve gizli bilgiler
API_KEY_PATTERNS = [
    # OpenAI API anahtarları
    (r'sk-[A-Za-z0-9]{48}', "[OPENAI_API_KEY]"),
    
    # Generic API anahtarları  
    (r'api[_-]?key[=: "\']+([A-Za-z0-9_\-\.]{20,})', "[API_KEY]"),
    
    # AWS erişim anahtarları
    (r'AKIA[0-9A-Z]{16}', "[AWS_ACCESS_KEY]"),
    
    # GitHub kişisel erişim tokenları
    (r'ghp_[A-Za-z0-9]{36}', "[GITHUB_TOKEN]"),
    (r'github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}', "[GITHUB_PAT]"),
    
    # Google API anahtarları
    (r'AIza[0-9A-Za-z\-_]{35}', "[GOOGLE_API_KEY]"),
    
    # Slack tokenları
    (r'xox[pbar]-[0-9]{12}-[0-9]{12}-[0-9a-zA-Z]{24}', "[SLACK_TOKEN]"),
]

# Kişisel tanımlayıcı bilgiler
PII_PATTERNS = [
    # E-posta adresleri
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "[EMAIL]"),
    
    # Telefon numaraları (farklı formatlar)
    (r'(?:\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', "[PHONE_NUMBER]"),
    
    # Kredi kartı numaraları
    (r'(?:\d{4}[- ]?){3}\d{4}', "[CREDIT_CARD]"),
    
    # Sosyal güvenlik numaraları (Türkiye için TC kimlik no)
    (r'\d{11}', "[TC_KIMLIK_NO]"),
    
    # IP adresleri
    (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', "[IP_ADDRESS]"),
    
    # URL'ler
    (r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', "[URL]"),
]

# Kuruluşa özel gizli bilgiler (proje örneğine göre değiştirilebilir)
ORGANIZATION_PATTERNS = [
    # Proje kodu/takma adı
    (r'Project[\s\-_:]+(Falcon|Phoenix|Bluebird|Titan)', "[PROJE_ADI]"),
    
    # İç ürün kodları
    (r'PRD-\d{4}-\d{2}', "[ÜRÜN_KODU]"),
    
    # Company internal domains
    (r'(?:[\w-]+\.)*internal\.example\.com', "[İÇ_DOMAIN]"),
]

# Tüm desenleri birleştir
ALL_PATTERNS = API_KEY_PATTERNS + PII_PATTERNS + ORGANIZATION_PATTERNS


def compile_patterns(patterns: List[Tuple[str, str]]) -> List[Tuple[Pattern, str]]:
    """Regex desenlerini derle."""
    return [(re.compile(pattern), replacement) for pattern, replacement in patterns]


class RegexFilter:
    """Regex tabanlı hassas veri filtreleme sınıfı."""

    def __init__(self):
        """Regex desenlerini derle."""
        self.compiled_patterns = compile_patterns(ALL_PATTERNS)
    
    def filter_text(self, text: str) -> Tuple[str, List[Dict], bool]:
        """
        Metindeki hassas verileri maskeler.
        
        Args:
            text: İşlenecek metin
            
        Returns:
            Tuple[str, List[Dict], bool]: 
                - Filtrelenmiş metin
                - Maskelenen öğeler listesi
                - Hassas içerik tespit edildi mi?
        """
        if not text:
            return "", [], False
            
        filtered_text = text
        masked_elements = []
        has_sensitive_content = False
        
        for pattern, replacement in self.compiled_patterns:
            matches = pattern.finditer(filtered_text)
            
            # Son eşleşmeden başlayarak geriye doğru değiştir (pozisyonları bozmamak için)
            matches_list = list(matches)
            
            for match in reversed(matches_list):
                start, end = match.span()
                matched_text = match.group()
                
                # Orijinal metinle eşleşen içeriği kaydet
                masked_elements.append({
                    "type": replacement.strip("[]"),
                    "start_idx": start,
                    "end_idx": end,
                    "length": end - start,
                })
                
                # Metni maskele
                filtered_text = filtered_text[:start] + replacement + filtered_text[end:]
                has_sensitive_content = True
        
        return filtered_text, masked_elements, has_sensitive_content 