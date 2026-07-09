# Stack — Recommended Technology Choices

## Current Stack (Validated)

| Category | Technology | Rationale |
|----------|------------|-----------|
| Frontend Framework | React 19 + Vite 6 | Fast HMR, modern React features |
| Language | TypeScript | Type safety, better DX |
| Styling | Tailwind CSS | Utility-first, rapid development |
| Backend | FastAPI | Python async, auto OpenAPI docs |
| Database | SQLite + SQLModel | Simple setup, type-safe ORM |
| AI | Google Gemini | Multi-modal, cost-effective |
| TTS | Eleven Labs | High-quality voice synthesis |
| Browser Automation | Playwright | Cross-browser, reliable selectors |
| Video Processing | FFmpeg | Industry standard, full feature set |

---

## Recommendations for v1

### Keep Current Stack

The existing stack is well-suited for the project:
- React/Vite for fast frontend development
- FastAPI for rapid backend development
- Playwright for reliable social media automation

### Considerations

1. **PostgreSQL for Production** — SQLite fine for development, but PostgreSQL recommended for production with concurrent users
2. **Celery for Background Jobs** — Video processing is CPU-intensive; consider Celery + Redis for async queue
3. **CDN for Video Assets** — Use AWS S3 + CloudFront for video storage in production

---

## Technology Versions (Current)

| Package | Version | Notes |
|---------|---------|-------|
| React | 19.2.4 | Latest |
| Vite | 6.2.0 | Latest |
| TypeScript | 5.8.2 | Latest |
| Tailwind CSS | 3.4.17 | Stable |
| FastAPI | Latest from pip | Check requirements.txt |
| Python | 3.10+ | Required |

---

## What NOT to Use

| Technology | Reason |
|------------|--------|
| Jest (frontend) | Vitest is faster and Vite-native |
| Django | FastAPI is lighter for this use case |
| Selenium | Playwright is more modern and reliable |
| MongoDB | SQLModel + SQLite/PostgreSQL is better fit |

---

*Research document created for GSD project initialization*