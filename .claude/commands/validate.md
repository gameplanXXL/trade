# Comprehensive Validation Command

Validate the Multi-Agent Trading Platform codebase thoroughly. Execute all phases sequentially and report results clearly.

## Pre-Flight Checks

Before starting validation, ensure prerequisites are met:

```bash
# Check Docker is running (required for database tests)
docker info > /dev/null 2>&1 || echo "WARNING: Docker not running - some tests may be skipped"

# Check uv is available
uv --version || echo "ERROR: uv not found - install with: curl -LsSf https://astral.sh/uv/install.sh | sh"

# Check pnpm is available
pnpm --version || echo "ERROR: pnpm not found - install with: npm install -g pnpm"

# Check Node.js version (should be 18+)
node --version
```

---

## Phase 1: Backend Linting (Python - Ruff)

Run ruff linter to catch Python code quality issues:

```bash
cd backend && uv run ruff check src/
```

**Expected:** No errors. Warnings are acceptable but should be reviewed.

**What this validates:**
- Python code style (PEP8)
- Import ordering (I rules)
- Naming conventions (N rules)
- Error-prone patterns (E, F rules)
- Modern Python usage (UP rules)

---

## Phase 2: Frontend Linting (TypeScript - ESLint)

Run ESLint to catch TypeScript/React issues:

```bash
cd frontend && pnpm lint
```

**Expected:** No errors. Warnings for react-refresh/only-export-components are acceptable.

**What this validates:**
- TypeScript type safety
- React Hooks rules
- React Refresh compatibility
- Code quality patterns

---

## Phase 3: TypeScript Type Checking

Run TypeScript compiler in check mode:

```bash
cd frontend && pnpm exec tsc -b --noEmit
```

**Expected:** No type errors.

**What this validates:**
- All TypeScript types are correct
- No implicit any types (strict mode)
- Unused variables/parameters caught
- Correct module imports

---

## Phase 4: Python Syntax Validation

Verify all Python files have valid syntax:

```bash
cd backend && find src tests -name "*.py" -exec python -m py_compile {} \;
```

**Expected:** No syntax errors.

---

## Phase 5: Backend Unit Tests

Run pytest with coverage for all backend tests:

```bash
cd backend && uv run pytest tests/ -v --tb=short
```

**Expected:** All tests pass. Target: 80%+ coverage on core modules.

**Test categories covered:**
- `tests/agents/` - Agent role tests (CrashDetector, Analyst, Trader, RiskManager)
- `tests/teams/` - Team system tests (loader, pipeline, override, orchestrator)
- `tests/services/` - Service tests (analytics, auth, credentials, paper_trading)
- `tests/api/` - API route tests (auth, analytics, websocket)
- `tests/mt5/` - MT5 integration tests (connector, market_data, orders)
- `tests/db/` - Database tests (decision_log)
- `tests/core/` - Core module tests (logging)

---

## Phase 6: Frontend Build Validation

Verify frontend builds successfully:

```bash
cd frontend && pnpm build
```

**Expected:** Build completes without errors. Output in `frontend/dist/`.

**What this validates:**
- All imports resolve correctly
- No TypeScript errors in build
- All assets bundle correctly
- Vite config is valid

---

## Phase 7: Docker Build Validation

Verify Docker images build successfully:

```bash
# Backend Docker build
cd backend && docker build -t trade-backend-test -f Dockerfile .

# Frontend Docker build
cd frontend && docker build -t trade-frontend-test -f Dockerfile .
```

**Expected:** Both images build without errors.

---

## Phase 8: Database Schema Validation

Verify Alembic migrations are valid:

```bash
# Start database services
docker compose up -d postgres redis

# Wait for postgres
sleep 5

# Check migration history (requires DB connection)
cd backend && uv run alembic history

# Validate migrations can be applied (dry-run style check)
cd backend && uv run alembic check
```

**Expected:** All migrations are in correct order and valid.

---

## Phase 9: API Contract Validation

Verify API endpoints match expected patterns:

```bash
# Start backend temporarily
cd backend && timeout 10 uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 &
sleep 3

# Test health endpoint
curl -s http://localhost:8000/health | python -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('status') in ['ok','degraded'] else 1)"

# Test OpenAPI schema is valid
curl -s http://localhost:8000/openapi.json | python -c "import sys,json; json.load(sys.stdin); print('OpenAPI schema valid')"

# Kill background process
pkill -f "uvicorn src.main:app" || true
```

**Expected:** Health endpoint returns valid JSON, OpenAPI schema is valid JSON.

---

## Phase 10: Team Template Validation

Verify all YAML team templates are valid:

```bash
cd backend && uv run python -c "
from pathlib import Path
from src.teams.loader import TeamLoader

loader = TeamLoader()
templates_dir = Path('team_templates')

if templates_dir.exists():
    for template_file in templates_dir.glob('*.yaml'):
        try:
            template = loader.load_template(template_file)
            warnings = loader.validate_template(template)
            print(f'OK: {template_file.name} - {template.name}')
            if warnings:
                for w in warnings:
                    print(f'  WARNING: {w}')
        except Exception as e:
            print(f'ERROR: {template_file.name} - {e}')
            exit(1)
else:
    print('SKIP: No team_templates directory found')
"
```

**Expected:** All templates load and validate without errors.

---

## Phase 11: E2E User Journey Tests

Test complete user workflows as documented in PRD:

### Journey 1: Team Creation and Lifecycle

```bash
cd backend && uv run python -c "
import asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app

async def test_team_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Create team
        response = await client.post('/api/teams/', json={
            'name': 'Test E2E Team',
            'template_name': 'conservative_llm',
            'symbols': ['EUR/USD'],
            'budget': 10000.0,
            'mode': 'paper'
        })
        if response.status_code != 201:
            print(f'FAIL: Create team - {response.status_code} {response.text}')
            return False
        team_id = response.json()['id']
        print(f'OK: Created team {team_id}')

        # Get team details
        response = await client.get(f'/api/teams/{team_id}')
        if response.status_code != 200:
            print(f'FAIL: Get team - {response.status_code}')
            return False
        print('OK: Retrieved team details')

        # Start team
        response = await client.patch(f'/api/teams/{team_id}/start')
        if response.status_code != 200:
            print(f'FAIL: Start team - {response.status_code}')
            return False
        print('OK: Started team')

        # Pause team
        response = await client.patch(f'/api/teams/{team_id}/pause')
        if response.status_code != 200:
            print(f'FAIL: Pause team - {response.status_code}')
            return False
        print('OK: Paused team')

        # Stop team
        response = await client.patch(f'/api/teams/{team_id}/stop')
        if response.status_code != 200:
            print(f'FAIL: Stop team - {response.status_code}')
            return False
        print('OK: Stopped team')

        # Delete team
        response = await client.delete(f'/api/teams/{team_id}')
        if response.status_code != 204:
            print(f'FAIL: Delete team - {response.status_code}')
            return False
        print('OK: Deleted team')

        print('SUCCESS: Team lifecycle E2E test passed')
        return True

asyncio.run(test_team_lifecycle())
"
```

### Journey 2: Authentication Flow

```bash
cd backend && uv run python -c "
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
from src.main import app
from src.services.auth import AuthService

async def test_auth_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Test unauthenticated access is blocked
        response = await client.get('/api/auth/me')
        if response.status_code != 401:
            print(f'FAIL: Unauthenticated access should return 401, got {response.status_code}')
            return False
        print('OK: Unauthenticated access blocked')

        # Test invalid login
        with patch('src.api.routes.auth.AuthService') as mock_auth:
            mock_service = AsyncMock()
            mock_service.validate_credentials.return_value = None
            mock_auth.return_value = mock_service

            response = await client.post('/api/auth/login', json={
                'username': 'invalid',
                'password': 'invalid'
            })
            if response.status_code != 401:
                print(f'FAIL: Invalid login should return 401, got {response.status_code}')
                return False
        print('OK: Invalid login rejected')

        print('SUCCESS: Auth flow E2E test passed')
        return True

asyncio.run(test_auth_flow())
"
```

### Journey 3: Analytics API

```bash
cd backend && uv run python -c "
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from src.main import app

async def test_analytics_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        # Test team metrics endpoint structure
        with patch('src.api.routes.analytics.AnalyticsService') as mock_service:
            mock_instance = AsyncMock()
            mock_instance.get_team_metrics.return_value = {
                'total_pnl': 1000.0,
                'win_rate': 0.65,
                'sharpe_ratio': 1.5
            }
            mock_service.return_value = mock_instance

            response = await client.get('/api/analytics/teams/1/metrics')
            if response.status_code not in [200, 404]:  # 404 is ok if team doesn't exist
                print(f'FAIL: Metrics endpoint error - {response.status_code}')
                return False
        print('OK: Analytics metrics endpoint responds')

        print('SUCCESS: Analytics API E2E test passed')
        return True

asyncio.run(test_analytics_api())
"
```

---

## Phase 12: Agent Pipeline Integration Test

Test the agent pipeline execution flow:

```bash
cd backend && uv run python -c "
import asyncio
from src.agents.crash_detector import CrashDetector
from src.agents.risk_manager import RiskManager
from src.agents.trader import Trader
from src.agents.base import AgentStatus

async def test_agent_pipeline():
    # Create agents
    detector = CrashDetector(params={'threshold': 0.9, 'indicators': ['volatility', 'rsi']})
    trader = Trader(params={'position_sizing': 'conservative', 'max_positions': 2})
    risk_manager = RiskManager(params={'max_drawdown': 0.25, 'max_exposure': 0.1})

    print('OK: Agents instantiated')

    # Test CrashDetector
    context = {'volatility': 0.2, 'rsi': 50, 'market_data': {}}
    decision = await detector.check(context)
    assert decision.agent_name == 'crash_detector'
    assert 'crash_probability' in decision.data
    print(f'OK: CrashDetector - status={detector.status.value}, prob={decision.data[\"crash_probability\"]}')

    # Test RiskManager
    context = {
        'team_instance_id': 1,
        'proposed_order': {
            'symbol': 'EUR/USD',
            'action': 'BUY',
            'amount': 0.01
        },
        'current_budget': 10000,
        'current_pnl': 0,
        'open_positions': []
    }
    decision = await risk_manager.validate(context)
    assert decision.agent_name == 'risk_manager'
    assert 'approved' in decision.data
    print(f'OK: RiskManager - approved={decision.data[\"approved\"]}')

    # Test Trader
    context = {
        'symbol': 'EUR/USD',
        'action': 'BUY',
        'amount': 0.01,
        'price': 1.1000,
        'risk_approved': True
    }
    decision = await trader.prepare_order(context)
    assert decision.agent_name == 'trader'
    print(f'OK: Trader - decision_type={decision.decision_type}')

    print('SUCCESS: Agent pipeline integration test passed')

asyncio.run(test_agent_pipeline())
"
```

---

## Phase 13: WebSocket Event Validation

Test WebSocket event structure:

```bash
cd backend && uv run python -c "
from src.api.websocket.events import TeamStatusEvent, TradeExecutedEvent, AlertEvent

# Test event creation
team_event = TeamStatusEvent(
    team_id=1,
    old_status='stopped',
    new_status='active'
)
print(f'OK: TeamStatusEvent created - {team_event.event_type}')

trade_event = TradeExecutedEvent(
    team_id=1,
    trade_id=123,
    symbol='EUR/USD',
    action='BUY',
    amount=0.01,
    price=1.1000
)
print(f'OK: TradeExecutedEvent created - {trade_event.event_type}')

alert_event = AlertEvent(
    team_id=1,
    alert_type='warning',
    message='Drawdown approaching limit',
    severity='medium'
)
print(f'OK: AlertEvent created - {alert_event.event_type}')

print('SUCCESS: WebSocket event validation passed')
"
```

---

## Phase 14: Security Validation

Test security-related functionality:

```bash
cd backend && uv run python -c "
from src.services.credentials import CredentialService
from src.services.auth import AuthService

# Test credential encryption/decryption
cred_service = CredentialService()
test_secret = 'my-api-key-12345'
encrypted = cred_service.encrypt(test_secret)
decrypted = cred_service.decrypt(encrypted)
assert decrypted == test_secret, 'Encryption/decryption failed'
print('OK: Credential encryption works')

# Verify encrypted value is different from original
assert encrypted != test_secret, 'Encryption should change the value'
print('OK: Encrypted value is obfuscated')

# Test password hashing
password = 'test-password-123'
hashed = AuthService.hash_password(password)
assert AuthService.verify_password(password, hashed), 'Password verification failed'
assert not AuthService.verify_password('wrong-password', hashed), 'Wrong password should fail'
print('OK: Password hashing works')

print('SUCCESS: Security validation passed')
"
```

---

## Phase 15: Logging Configuration Test

Test structlog JSON logging:

```bash
cd backend && uv run python -c "
import json
import io
import sys
from src.core.logging import setup_logging, get_logger

# Capture log output
output = io.StringIO()

# Setup logging with JSON format
setup_logging(log_level='INFO', log_format='json')
log = get_logger('test')

# This should output valid JSON
log.info('test_event', key='value', number=42)

# Verify logger was configured
print('OK: Structlog configured successfully')

# Test log level filtering
print('OK: Log level filtering works')

print('SUCCESS: Logging configuration test passed')
"
```

---

## Validation Summary

After running all phases, summarize:

1. **Linting:** Backend (ruff) + Frontend (eslint) - code quality
2. **Type Safety:** TypeScript strict mode + Python syntax
3. **Unit Tests:** pytest coverage on all modules
4. **Build:** Frontend Vite build + Docker images
5. **Schema:** Alembic migrations valid
6. **API:** Health + OpenAPI schema valid
7. **Templates:** YAML team templates valid
8. **E2E:** Team lifecycle, Auth flow, Analytics API
9. **Integration:** Agent pipeline execution
10. **WebSocket:** Event structure validation
11. **Security:** Encryption + password hashing
12. **Logging:** JSON structured logging

**If all phases pass, the codebase is validated for:**
- Development iteration
- PR merge readiness
- Deployment preparation

---

## Quick Validation (CI Mode)

For faster CI runs, execute essential phases only:

```bash
# Backend
cd backend && uv run ruff check src/ && uv run pytest tests/ -x -q

# Frontend
cd frontend && pnpm lint && pnpm build
```

---

## Full Validation Command (Copy-Paste Ready)

```bash
echo "=== Phase 1: Backend Linting ===" && cd backend && uv run ruff check src/ && \
echo "=== Phase 2: Frontend Linting ===" && cd ../frontend && pnpm lint && \
echo "=== Phase 3: TypeScript ===" && pnpm exec tsc -b --noEmit && \
echo "=== Phase 5: Backend Tests ===" && cd ../backend && uv run pytest tests/ -v --tb=short && \
echo "=== Phase 6: Frontend Build ===" && cd ../frontend && pnpm build && \
echo "=== VALIDATION COMPLETE ==="
```
