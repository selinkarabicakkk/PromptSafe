"""NER (Named Entity Recognition) based filters for sensitive data."""
import spacy
from typing import Dict, List, Tuple, Set, Optional

# SpaCy Entity türleri ve maskelemesi
ENTITY_MASK_MAP = {
    # SpaCy'nin standart entity türleri
    "PERSON": "[KIŞI]",
    "ORG": "[ORGANIZASYON]",
    "GPE": "[LOKASYON]",  # Geopolitical entity
    "LOC": "[LOKASYON]",
    "MONEY": "[PARA]",
    "DATE": "[TARIH]",
    "TIME": "[ZAMAN]",
    "CARDINAL": "[SAYI]",
    "PERCENT": "[YÜZDE]",
    # Özel entity türleri
    "EMAIL": "[EMAIL]",
    "PHONE": "[TELEFON]",
    "CREDIT_CARD": "[KREDI_KARTI]",
    "SSN": "[TC_KIMLIK_NO]",
}

# Maskelenecek entity türlerinin kümesi
ENTITIES_TO_MASK: Set[str] = {
    "PERSON", "ORG", "GPE", "LOC", "MONEY", "DATE", 
    "EMAIL", "PHONE", "CREDIT_CARD", "SSN"
}


class NERFilter:
    """SpaCy tabanlı NER (Named Entity Recognition) filtreleme sınıfı."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        NER modelini yükle.
        
        Args:
            model_name: Kullanılacak SpaCy model adı
        """
        self._model = None
        self.model_name = model_name
        
    @property
    def model(self):
        """SpaCy modelini lazy loading ile yükle."""
        if self._model is None:
            try:
                self._model = spacy.load(self.model_name)
            except OSError:
                # Model henüz yüklenmemişse indirme komutu verilmeli
                # python -m spacy download en_core_web_sm
                raise ImportError(
                    f"SpaCy modeli '{self.model_name}' yüklü değil. "
                    f"Yüklemek için: python -m spacy download {self.model_name}"
                )
        return self._model
    
    def filter_text(self, text: str) -> Tuple[str, List[Dict], bool]:
        """
        Metindeki varlıkları (entities) tespit eder ve maskeler.
        
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
            
        # SpaCy ile metni işle
        doc = self.model(text)
        
        # Maskelenecek entity'leri topla ve sırala (sondan başa)
        entities_to_mask = []
        for ent in doc.ents:
            if ent.label_ in ENTITIES_TO_MASK:
                entities_to_mask.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start_idx": ent.start_char,
                    "end_idx": ent.end_char,
                    "mask": ENTITY_MASK_MAP.get(ent.label_, f"[{ent.label_}]")
                })
        
        # Sondan başa doğru sırala
        entities_to_mask.sort(key=lambda x: x["start_idx"], reverse=True)
        
        # Metni maskele
        filtered_text = text
        masked_elements = []
        
        for entity in entities_to_mask:
            start = entity["start_idx"]
            end = entity["end_idx"]
            mask = entity["mask"]
            
            # Maskeleme işlemini uygula
            filtered_text = filtered_text[:start] + mask + filtered_text[end:]
            
            # Maskelenen içeriği kaydet
            masked_elements.append({
                "type": entity["type"],
                "start_idx": start,
                "end_idx": end,
                "length": end - start,
            })
        
        has_sensitive_content = len(masked_elements) > 0
        return filtered_text, masked_elements, has_sensitive_content 