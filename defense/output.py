import re

class OutputGuardrails:
    def __init__(self):
        self.pii_patterns = [
            r"\b\d{10,16}\b",              # 10-16 digit numbers
            r"password\s*=\s*\w+",         # password = some_value
            r"api[_-]?key\s*=\s*\w+",      # api_key = some_value
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", # email
            r"\b\d{3}-\d{2}-\d{4}\b",      # US SSN
            r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", # IPv4
            r"\b(?:\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\(\d{3}\)\s*\d{3}[-.\s]?\d{4})\b" # phone
        ]

    def check(self, text):
        modified = text
        for pattern in self.pii_patterns:
            modified = re.sub(pattern, "[REDACTED]", modified, flags=re.IGNORECASE)
        return type('GuardResult', (), {"blocked": False, "modified": modified})()
