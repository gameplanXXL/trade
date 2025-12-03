---
epic: 009
story: 01
title: "Fernet-Verschlüsselung für Credentials"
status: backlog
story_points: 2
covers: [FR49]
---

## Story 9.1: Fernet-Verschlüsselung für Credentials

Als Operator,
möchte ich, dass sensible Daten verschlüsselt gespeichert werden,
damit Credentials bei Datenbankzugriff geschützt sind.

**Acceptance Criteria:**

**Given** Backend mit Settings
**When** ich Credential-Verschlüsselung implementiere
**Then** existiert `src/services/credentials.py`:
```python
from cryptography.fernet import Fernet

class CredentialService:
    def __init__(self, encryption_key: str):
        self.fernet = Fernet(encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """Verschlüsselt String, gibt Base64-encoded zurück"""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Entschlüsselt Base64-encoded String"""
        return self.fernet.decrypt(ciphertext.encode()).decode()
```

**And** Verschlüsselt werden:
  - MT5-Passwort
  - LLM API-Keys
  - Andere Secrets

**And** Encryption-Key aus Environment (`ENCRYPTION_KEY`)
**And** Key-Generierung dokumentiert: `Fernet.generate_key()`

**Technical Notes:**
- Fernet = AES-128-CBC mit HMAC
- Key muss 32 Bytes Base64-encoded sein
- Niemals Key im Code oder Logs

**Prerequisites:** Story 1.7

