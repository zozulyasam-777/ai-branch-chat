"""
anonymizer.py
Simple text anonymization module using pattern matching and token replacement.
Supports multiple masking strategies and reversible token mapping.
"""

import re
import hashlib
from typing import Dict, List, Tuple, Optional


class SimpleAnonymizer:
    """
    Lightweight anonymizer that replaces sensitive data with tokens.
    Supports reverse mapping to restore original values.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize anonymizer with configuration.
        """
        self.config = config or {}
        
        # Default patterns for Russian text
        self.patterns = {
            'PERSON': r'\b([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)\b',
            'PERSON_FULL': r'\b([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)\b',
            'PHONE': r'(\+7|8)\s?\(?\d{3}\)?\s?\d{3}-?\d{2}-?\d{2}',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PASSPORT_RU': r'\b\d{4}\s?\d{6}\b',
            'CARD_NUMBER': r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',
            'ADDRESS': r'\b(ул\.|улица|пр\.|проспект|пер\.|переулок)\s+[А-ЯЁа-яё0-9\s,]+\b',
        }
        
        # Override with custom patterns from config
        if 'custom_patterns' in self.config:
            self.patterns.update(self.config['custom_patterns'])
        
        # Token mapping storage
        self.token_maps: Dict[str, Dict[str, str]] = {}
        self.counters: Dict[str, int] = {}
    
    def _generate_token(self, entity_type: str, session_id: str) -> str:
        """Generate a unique token for an entity."""
        key = f"{entity_type}_{session_id}"
        self.counters[key] = self.counters.get(key, 0) + 1
        return f"[{entity_type}_{session_id[:6]}_{self.counters[key]}]"
    
    def _apply_mask(self, text: str, entity_type: str) -> str:
        """Apply masking strategy based on entity type."""
        strategy = self.config.get('mask_strategy', 'token')
        
        if strategy == 'token':
            return text  # Will be replaced by token in anonymize()
        elif strategy == 'mask_partial':
            return '*' * (len(text) - 2) + text[-2:] if len(text) > 2 else '*' * len(text)
        elif strategy == 'mask_all':
            return '*' * len(text)
        elif strategy == 'hash':
            return f"#{hashlib.md5(text.encode()).hexdigest()[:8]}"
        elif strategy == 'generalize':
            generalizations = {
                'PERSON': '[ЧЕЛОВЕК]', 'PHONE': '[ТЕЛЕФОН]', 'EMAIL': '[EMAIL]',
                'PASSPORT_RU': '[ДОКУМЕНТ]', 'CARD_NUMBER': '[КАРТА]', 'ADDRESS': '[АДРЕС]',
            }
            return generalizations.get(entity_type, '[ДАННЫЕ]')
        return text
    
    def anonymize(self, text: str, session_id: str) -> Tuple[str, Dict[str, str]]:
        """Anonymize sensitive data in text."""
        if not self.config.get('enabled', True):
            return text, {}
        
        token_map = {}
        result = text
        
        for entity_type, pattern in self.patterns.items():
            matches = list(re.finditer(pattern, result, re.IGNORECASE))
            for match in reversed(matches):
                original = match.group(0)
                if original.startswith('[') and original.endswith(']'):
                    continue
                
                strategy = self.config.get('mask_strategy', 'token')
                if strategy == 'token':
                    token = self._generate_token(entity_type, session_id)
                    token_map[token] = original
                    replacement = token
                else:
                    token = f"#{hashlib.md5(original.encode()).hexdigest()[:8]}"
                    token_map[token] = original
                    replacement = self._apply_mask(original, entity_type)
                
                result = result[:match.start()] + replacement + result[match.end():]
        
        if session_id not in self.token_maps:
            self.token_maps[session_id] = {}
        self.token_maps[session_id].update(token_map)
        
        return result, token_map
    
    def deanonymize(self, text: str, session_id: str) -> str:
        """Restore original values from tokens."""
        if not self.config.get('enabled', True):
            return text
        
        token_map = self.token_maps.get(session_id, {})
        result = text
        for token in sorted(token_map.keys(), key=len, reverse=True):
            original = token_map[token]
            result = result.replace(token, original)
        
        return result
    
    def get_stats(self, session_id: str) -> Dict:
        """Get anonymization statistics for a session."""
        token_map = self.token_maps.get(session_id, {})
        stats = {'total_entities': len(token_map), 'by_type': {}}
        
        for token, original in token_map.items():
            parts = token.strip('[]').split('_')
            if parts:
                entity_type = parts[0]
                stats['by_type'][entity_type] = stats['by_type'].get(entity_type, 0) + 1
        
        return stats