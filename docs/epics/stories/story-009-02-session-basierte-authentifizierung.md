---
epic: 009
story: 02
title: "Session-basierte Authentifizierung"
status: backlog
story_points: 3
covers: [FR50]
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

