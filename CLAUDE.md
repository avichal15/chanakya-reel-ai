<!-- GSD:project-start source:PROJECT.md -->
## Project

**Project: Chanakya Reel AI**

A full-stack web application for generating viral video reels with philosophical quotes from Chanakya and other thinkers. The system generates AI-powered scripts, creates text-to-speech audio, compiles videos with captions, and posts to Instagram/YouTube automatically.

**Core Value:** Automate the creation and posting of short-form video content featuring philosophical wisdom, enabling consistent social media presence without manual video production.

---
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

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
## Runtime Environment
- **Frontend**: Node.js 18+ / Vite dev server (localhost:5173)
- **Backend**: Python 3.10+ with virtual environment (`.venv`)
- **Database**: SQLite (`database.db` in project root)
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Frontend Conventions (React/TypeScript)
### Component Structure
- Functional components with hooks
- TypeScript for all components (`.tsx` extension)
- Props interface defined at top of file
### Example
### Styling
- Tailwind CSS classes (no custom CSS files)
- Responsive design with mobile-first approach
- Dark mode support where applicable
### API Communication
- Use `services/api.ts` for HTTP calls
- Axios for HTTP requests
- Async/await pattern
## Backend Conventions (Python/FastAPI)
### Function Naming
- `snake_case` for all functions and variables
- `PascalCase` for classes
### FastAPI Patterns
### Database Models (SQLModel)
### Error Handling
- Use `try/except` blocks
- Return proper HTTP status codes
- Logging with `logging.getLogger(__name__)`
## TypeScript Types (types.ts)
- `Video` — Video metadata
- `Quote` — Quote data
- `Philosopher` — Philosopher info
- `Script` — Generated script
- `ApiResponse` — Standard API response wrapper
## Git Conventions
- Commit messages: `type: description` (e.g., `feat: add new API endpoint`)
- Types: `feat`, `fix`, `docs`, `chore`, `refactor`
- GSD planning docs committed separately
## File Organization
| Type | Location |
|------|----------|
| React Components | `components/` or `pages/` |
| Backend Services | `backend/services/` |
| Database Models | `backend/database.py` |
| API Endpoints | `backend/main.py` |
| Types | `types.ts` |
| API Client | `services/api.ts` |
## Configuration
- **Frontend**: Environment variables in `.env.local`
- **Backend**: Environment variables in `backend/.env`
- Never commit secrets to git (both `.env` files in `.gitignore`)
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Overall Architecture
```
```
## Pattern: Service-Oriented Architecture
| Service | Purpose | Key Functions |
|---------|---------|---------------|
| `script_engine.py` | Generate video scripts from quotes using Gemini | `generate_script()` |
| `voice_engine.py` | Text-to-speech generation | `generate_voice()` |
| `video_engine.py` | Video compilation with FFmpeg | `generate_video()` |
| `caption_engine.py` | Generate viral captions | `generate_caption()` |
| `scene_engine.py` | Scene detection/management | `detect_scenes()` |
| `ingestion_engine.py` | Quote/philosopher data ingestion | `ingest_quotes()` |
| `ass_engine.py` | ASS subtitle generation | `create_ass_subs()` |
| `viral_caption_engine.py` | Viral-style captions for social | `create_viral_caption()` |
| `thumbnail_engine.py` | Thumbnail generation | `create_thumbnail()` |
| `pexels_engine.py` | Stock video integration | `search_videos()` |
## Data Flow
### Video Generation Pipeline
### Social Posting Pipeline
## Entry Points
| Component | Entry Point | Port |
|-----------|-------------|------|
| Frontend Dev Server | `npm run dev` | 5173 |
| Backend API | `uvicorn backend.main:app` | 8000 |
| Background Scheduler | `python backend/scheduler.py` | — |
## Key Abstractions
- **Database Models**: SQLModel for type-safe ORM
- **Service Registry**: Import-based service discovery
- **Static Assets**: `/assets` and `/output` mounted as FastAPI static
- **Environment**: `.env` files for configuration (backend-specific)
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
