# Credential Encryption Service

## Übersicht

Der `CredentialService` verschlüsselt sensible Daten (MT5-Passwörter, API-Keys) mit Fernet (AES-128-CBC + HMAC).

## Encryption Key generieren

```python
from cryptography.fernet import Fernet

# Erzeuge einen neuen 32-Byte Fernet Key (44 Zeichen Base64)
key = Fernet.generate_key()
print(key.decode())
# Beispiel: Ey8lXWMZDHnykY-LQx63JUg0rdx_hj-yx5pszkqdyoA=
```

## Environment Variable setzen

Füge den generierten Key in `.env` ein:

```env
ENCRYPTION_KEY=Ey8lXWMZDHnykY-LQx63JUg0rdx_hj-yx5pszkqdyoA=
```

**WICHTIG:**
- Der Key MUSS genau 44 Zeichen lang sein
- NIEMALS im Git committen
- NIEMALS loggen
- Für Production: Sichere Key-Rotation implementieren

## Verwendung

```python
from src.config.settings import get_settings
from src.services.credentials import CredentialService

# Service initialisieren
settings = get_settings()
credential_service = CredentialService(settings.encryption_key)

# MT5-Passwort verschlüsseln
mt5_password = "MySecurePassword123!"
encrypted_password = credential_service.encrypt(mt5_password)
# Speichere encrypted_password in Datenbank

# Später: Passwort entschlüsseln für MT5-Login
decrypted_password = credential_service.decrypt(encrypted_password)
# Nutze decrypted_password für MT5-Verbindung
```

## Welche Daten werden verschlüsselt?

1. **MT5 Credentials:**
   - `mt5_password` (in `teams` Tabelle)

2. **LLM API Keys:**
   - `anthropic_api_key` (wenn Team-spezifisch)
   - `openai_api_key` (wenn Team-spezifisch)

3. **Andere Secrets:**
   - Redis-Passwörter
   - Webhook-Tokens
   - OAuth-Tokens

## Sicherheitsrichtlinien

### DO:
- Key aus Environment Variable laden
- Key in sicherem Vault speichern (Production)
- Regelmäßige Key-Rotation planen
- Verschlüsselte Werte in DB speichern

### DON'T:
- Key in Code hardcoden
- Key in Logs ausgeben
- Key in Git committen
- Verschlüsselte Werte cachen ohne Kontrolle

## Fehlerbehandlung

```python
from cryptography.fernet import InvalidToken

try:
    decrypted = credential_service.decrypt(encrypted_value)
except InvalidToken:
    # Ciphertext wurde manipuliert oder falscher Key verwendet
    log.error("credential_decryption_failed", reason="invalid_token")
    raise
```

## Tests

Alle Tests laufen mit:

```bash
uv run pytest tests/services/test_credentials.py -v
```

Test-Coverage:
- Encryption/Decryption
- Unicode-Support
- Fehlerbehandlung (falscher Key, korrupte Daten)
- Security Properties (keine Info-Leaks)

## Technische Details

- **Algorithmus:** Fernet (AES-128-CBC + HMAC-SHA256)
- **Key-Größe:** 32 Bytes (256 Bit)
- **IV:** Automatisch zufällig pro Encryption
- **Padding:** PKCS7
- **Authentication:** HMAC verhindert Tampering

## Key-Rotation (Zukunft)

Für Production sollte Key-Rotation implementiert werden:

```python
# Pseudo-Code für Key-Rotation
old_service = CredentialService(old_key)
new_service = CredentialService(new_key)

for team in teams:
    plaintext = old_service.decrypt(team.encrypted_password)
    team.encrypted_password = new_service.encrypt(plaintext)
    db.commit()
```
