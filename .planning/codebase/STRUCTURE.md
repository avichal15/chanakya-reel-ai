# Structure — Directory Layout and Organization

## Project Root

```
chanakya-reel-ai/
├── .codex/                     # GSD framework (Do not modify)
├── .planning/                  # GSD planning files (generated)
│   └── codebase/               # Codebase mapping documents
├── backend/                    # Python FastAPI backend
│   ├── services/              # Service engine modules
│   ├── playwright_*/           # Playwright browser profiles
│   ├── assets/                # Static assets (uploaded media)
│   ├── output/                # Generated videos
│   ├── logs/                  # Backend logs
│   ├── fonts/                 # Font files
│   ├── main.py                # FastAPI application entry
│   ├── scheduler.py           # Background job scheduler
│   ├── database.py           # Database models
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend environment variables
├── pages/                     # React page components
│   ├── Dashboard.tsx
│   ├── Studio.tsx
│   ├── Library.tsx
│   └── History.tsx
├── components/                # React component library
│   ├── Layout.tsx
│   ├── Sidebar.tsx
│   └── VideoPreview.tsx
├── services/                  # Frontend API services
│   ├── api.ts
│   └── geminiService.ts
├── dist/                     # Built frontend (Vite output)
├── node_modules/             # Frontend dependencies
├── package.json              # Frontend package config
├── vite.config.ts            # Vite build config
├── tailwind.config.js        # Tailwind CSS config
├── tsconfig.json             # TypeScript config
├── database.db               # SQLite database
├── .env                      # Environment variables
└── AGENTS.md                 # GSD project agents guide
```

---

## Frontend Structure

| Directory | Purpose |
|-----------|---------|
| `pages/` | Route-level components (Dashboard, Studio, Library, History) |
| `components/` | Reusable UI components |
| `services/` | API communication layer |

**Key Files:**
- `App.tsx` — Main React app component
- `types.ts` — TypeScript type definitions
- `index.tsx` — React entry point
- `index.css` — Global styles

---

## Backend Structure

| Directory | Purpose |
|-----------|---------|
| `backend/services/` | Core business logic engines |
| `backend/playwright_instagram_profile/` | Instagram session data |
| `backend/playwright_youtube_profile/` | YouTube session data |
| `backend/assets/` | Uploaded/generated assets |
| `backend/output/` | Final generated videos |
| `backend/bot_profile/` | Bot configuration |

**Key Files:**
- `main.py` — FastAPI app, all endpoints
- `scheduler.py` — Cron-like job scheduler
- `database.py` — SQLModel definitions
- `instagram_uploader.py` — Instagram posting
- `youtube_uploader.py` — YouTube uploading
- `buffer_uploader.py` — Buffer social scheduling

---

## Key Locations

| Resource | Path |
|----------|------|
| Generated Videos | `backend/output/` |
| Database | `database.db` |
| Backend Logs | `backend/logs/`, `scheduler.log` |
| Debug Images | `backend/*.png` (ig_bot_debug, yt_bot_debug) |
| Environment | `.env`, `backend/.env` |

---

## Naming Conventions

- **Python**: `snake_case` for functions/variables, `PascalCase` for classes
- **TypeScript/React**: `PascalCase` for components/files, `camelCase` for functions/variables
- **CSS**: kebab-case for classes (Tailwind)

---

*Document created for GSD codebase mapping*