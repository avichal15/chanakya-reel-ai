# Integrations — External Services and APIs

## AI Services

### Google Gemini
- **Purpose**: Script generation for video reels
- **SDK**: `@google/genai` (frontend), `google-generativeai` (backend)
- **Usage**: Generate philosophical scripts from quotes
- **Model**: Configurable via environment

---

## External APIs

### Voice / Text-to-Speech
- **Eleven Labs** (referenced in code)
- **Voice ID**: `JBFqnCBsd6RMkjVDRZzb` (default)
- **API Key**: Configured in backend `.env`

---

## Browser Automation

### Playwright
- **Purpose**: Automated posting to Instagram and YouTube
- **Profile Storage**:
  - `backend/playwright_instagram_profile/` — Instagram session data
  - `backend/playwright_youtube_profile/` — YouTube session data

### Instagram Automation (`instagram_uploader.py`)
- Login via Playwright
- Create reels with video + caption
- Post to Instagram

### YouTube Automation (`youtube_uploader.py`)
- Login via Playwright
- Upload video with title, description, tags
- Publish as public/unlisted

---

## Database

### SQLite
- **Location**: `database.db` (project root)
- **ORM**: SQLModel
- **Tables**:
  - `Philosopher` — Philosopher metadata
  - `Quote` — Quote storage
  - `GeneratedScript` — Generated scripts
  - `VideoExport` — Video export metadata

---

## Environment Configuration

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `ELEVEN_API_KEY` | Eleven Labs API key |
| `DATABASE_URL` | SQLite database path |
| `OPENAI_API_KEY` | OpenAI (if used) |

---

*Document created for GSD codebase mapping*