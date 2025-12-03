# Epic 9: Authentifizierung & Sicherheit

**Epic Goal:** User kann sich einloggen; Credentials sind sicher gespeichert

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

---

## Story 9.2: Session-basierte Authentifizierung

Als Operator,
möchte ich mich mit Username/Password einloggen,
damit nur ich Zugriff auf das Dashboard habe.

**Acceptance Criteria:**

**Given** Redis für Sessions
**When** ich Auth implementiere
**Then** existiert `src/api/routes/auth.py`:
```python
router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
async def login(data: LoginRequest, response: Response, redis: Redis = Depends(get_redis)):
    """
    Validiert Credentials, erstellt Session, setzt Cookie.
    """
    user = await validate_credentials(data.username, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    session_token = secrets.token_urlsafe(32)
    await redis.set(f"session:{session_token}", user.id, ex=86400)

    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400
    )
    return {"message": "Login successful"}

@router.post("/logout")
async def logout(request: Request, response: Response, redis: Redis = Depends(get_redis)):
    """Löscht Session und Cookie"""
    session = request.cookies.get("session")
    if session:
        await redis.delete(f"session:{session}")
    response.delete_cookie("session")
    return {"message": "Logout successful"}
```

**And** Auth-Middleware prüft Session:
```python
async def get_current_user(request: Request, redis: Redis = Depends(get_redis)) -> User:
    session = request.cookies.get("session")
    if not session:
        raise HTTPException(401, "Not authenticated")
    user_id = await redis.get(f"session:{session}")
    if not user_id:
        raise HTTPException(401, "Session expired")
    return await get_user(int(user_id))
```

**Technical Notes:**
- Password-Hashing mit bcrypt
- Session-TTL: 24 Stunden
- Single User für MVP (kein User-Management)

**Prerequisites:** Story 1.4

---

## Story 9.3: Login-UI im Frontend

Als Operator,
möchte ich eine Login-Seite,
damit ich mich am Dashboard anmelden kann.

**Acceptance Criteria:**

**Given** Auth-API
**When** ich Login-UI implementiere
**Then** existiert `src/features/auth/LoginForm.tsx`:
```tsx
export function LoginForm() {
  const login = useLogin();
  const form = useForm<LoginInput>();

  const onSubmit = async (data: LoginInput) => {
    try {
      await login.mutateAsync(data);
      navigate('/dashboard');
    } catch (error) {
      form.setError('root', { message: 'Ungültige Anmeldedaten' });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Trading Platform</CardTitle>
          <CardDescription>Melde dich an, um fortzufahren</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <FormField name="username" label="Benutzername" />
            <FormField name="password" label="Passwort" type="password" />
            {form.formState.errors.root && (
              <Alert variant="destructive">{form.formState.errors.root.message}</Alert>
            )}
            <Button type="submit" className="w-full" disabled={login.isPending}>
              {login.isPending ? <Spinner /> : 'Anmelden'}
            </Button>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
```

**And** Auth-State in Zustand Store
**And** Protected Routes redirecten zu Login
**And** Automatischer Logout bei 401

**Technical Notes:**
- Cookie wird automatisch bei Requests gesendet
- Axios Interceptor für 401-Handling
- Remember-Me optional (längere Session)

**Prerequisites:** Story 1.5, 9.2

---

## Story 9.4: LLM-API Retry-Logic

Als Entwickler,
möchte ich robuste LLM-API-Aufrufe mit Retry-Logic,
damit temporäre Fehler automatisch behandelt werden.

**Acceptance Criteria:**

**Given** LLMSignalAnalyst
**When** ich Retry-Logic implementiere
**Then** existiert `src/agents/analyst.py` mit:
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class LLMSignalAnalyst(BaseAgent):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIError, Timeout)),
        before_sleep=lambda retry_state: log.warning(
            "llm_retry",
            attempt=retry_state.attempt_number,
            error=str(retry_state.outcome.exception())
        )
    )
    async def _call_llm(self, prompt: str) -> str:
        """LLM-Aufruf mit Retry"""
        return await self.llm.ainvoke(prompt)
```

**And** Retry bei:
  - Rate Limiting (429)
  - Server Errors (5xx)
  - Timeout

**And** Logging jedes Retry-Versuchs
**And** Fallback nach 3 Versuchen: HOLD-Signal mit Warning

**Technical Notes:**
- tenacity Library für Retry
- Exponential Backoff: 2s, 4s, 8s
- Gesamter Timeout: ~30s

**Prerequisites:** Story 2.5

---

## Story 9.5: Secrets-Filterung in Logs

Als Operator,
möchte ich, dass keine Secrets in Logs erscheinen,
damit Credentials nicht versehentlich exponiert werden.

**Acceptance Criteria:**

**Given** structlog-Setup
**When** ich Secret-Filtering implementiere
**Then** existiert in `src/core/logging.py`:
```python
SENSITIVE_KEYS = {'password', 'api_key', 'secret', 'token', 'authorization'}

def filter_sensitive_data(_, __, event_dict: dict) -> dict:
    """Ersetzt sensitive Werte mit ***REDACTED***"""
    for key in list(event_dict.keys()):
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            event_dict[key] = "***REDACTED***"
    return event_dict

structlog.configure(
    processors=[
        filter_sensitive_data,
        structlog.processors.JSONRenderer(),
    ]
)
```

**And** Gefilterte Keys:
  - `password`, `passwd`
  - `api_key`, `apikey`
  - `secret`
  - `token`
  - `authorization`

**And** Test verifiziert Filterung

**Technical Notes:**
- Case-insensitive Matching
- Recursive für nested Dicts (optional)
- Auch in Exception-Messages filtern

**Prerequisites:** Story 1.2

---

**Epic 9 Complete**

**Stories Created:** 5
**FR Coverage:** FR49, FR50, FR51, FR54
**Technical Context Used:** Architecture Security, Logging Patterns

---