# Concerns — Technical Debt, Issues, and Areas of Risk

## Technical Debt

### 1. No Formal Test Suite
- **Impact**: High — no automated regression testing
- **Risk**: Breaking changes go unnoticed until manual testing
- **Recommendation**: Add pytest for backend, Vitest/Jest for frontend

### 2. Hardcoded API Keys/Values
- Voice ID hardcoded: `JBFqnCBsd6RMkjVDRZzb`
- No environment variable abstraction for service configs
- **Recommendation**: Move all configs to `.env` files

### 3. Missing Type Annotations
- Python backend has incomplete type hints
- LSP shows type errors in `main.py`
- **Recommendation**: Add full type annotations to all Python functions

### 4. No Linting/Formatting
- No Prettier or ESLint for frontend
- No Black or Ruff for Python
- **Recommendation**: Add CI/CD lint checks

---

## Known Issues

### 1. Playwright Session Management
- Browser profiles stored in `playwright_instagram_profile/`
- Session can expire or become invalid
- Debug images show stalled automation (`ig_bot_debug_final_stalled.png`)

### 2. API Error Handling
- `main.py:479` — `requests` imported but may not be used
- Some endpoints lack proper error responses
- **Recommendation**: Add global exception handler

### 3. Video Generation Failures
- FFmpeg dependency may not be installed in all environments
- Background video/music paths can be `None` causing type errors
- **Recommendation**: Add dependency validation on startup

### 4. Database Concurrency
- SQLite not ideal for concurrent writes
- No connection pooling
- **Recommendation**: Consider PostgreSQL for production

---

## Security Concerns

### 1. Environment Variables
- `.env` files may contain secrets
- Already in `.gitignore` — good
- **Recommendation**: Validate on startup that required env vars exist

### 2. CORS
- `allow_origins=["*"]` in FastAPI — too permissive
- **Recommendation**: Restrict to frontend domain

### 3. No Rate Limiting
- API endpoints not rate-limited
- **Recommendation**: Add FastAPI rate limiting middleware

---

## Performance Considerations

### 1. Video Processing
- FFmpeg operations are CPU-intensive
- No async queue for video generation
- **Recommendation**: Add Celery or similar for background processing

### 2. Database Queries
- No query optimization
- N+1 queries possible
- **Recommendation**: Add database indexes and query optimization

### 3. Static Files
- Large video files served via FastAPI static mount
- **Recommendation**: Use CDN or separate storage for production

---

## Fragile Areas

| Area | Risk Level | Reason |
|------|------------|--------|
| Playwright automation | High | UI changes break selectors |
| Video FFmpeg pipeline | Medium | Codec/config issues |
| Gemini API calls | Medium | API rate limits, timeouts |
| Browser sessions | High | Expiration, captchas |

---

*Document created for GSD codebase mapping*