# Stack — Technology and Dependencies

## Frontend

| Category | Technology | Version |
|----------|------------|---------|
| Framework | React | 19.2.4 |
| Build Tool | Vite | 6.2.0 |
| Language | TypeScript | 5.8.2 |
| Styling | Tailwind CSS | 3.4.17 |
| UI Icons | Lucide React | 0.574.0 |
| HTTP Client | Axios | 1.13.5 |
| AI SDK | @google/genai | 1.41.0 |

### Dev Dependencies
- `@vitejs/plugin-react` 5.0.0
- `autoprefixer` 10.4.19
- `postcss` 8.4.38
- `tailwindcss-animate` 1.0.7
- `@types/node` 22.14.0

---

## Backend

| Category | Technology | Notes |
|----------|------------|-------|
| Framework | FastAPI | Python web framework |
| Database | SQLModel + SQLite | ORM with SQLite |
| External AI | Google Gemini | Script generation |
| Automation | Playwright | Instagram/YouTube posting |
| Voice | Eleven Labs / External | Text-to-speech (voice_id: JBFqnCBsd6RMkjVDRZzb) |

### Python Dependencies (from requirements.txt)
- `fastapi`
- `uvicorn`
- `sqlmodel`
- `python-dotenv`
- `playwright` (browser automation)

---

## Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Frontend dependencies |
| `vite.config.ts` | Vite build configuration |
| `tailwind.config.js` | Tailwind CSS configuration |
| `tsconfig.json` | TypeScript configuration |
| `postcss.config.js` | PostCSS configuration |
| `backend/.env` | Backend environment variables |
| `.env.local` | Local environment overrides |

---

## Runtime Environment

- **Frontend**: Node.js 18+ / Vite dev server (localhost:5173)
- **Backend**: Python 3.10+ with virtual environment (`.venv`)
- **Database**: SQLite (`database.db` in project root)

---

*Document created for GSD codebase mapping*