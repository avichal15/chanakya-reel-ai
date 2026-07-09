# Architecture — System Design and Patterns

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         React Frontend                         │
│                   (Vite + TypeScript + Tailwind)               │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │Dashboard │  │  Studio  │  │ Library  │  │    History   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
│                                                                 │
│                         Services Layer                          │
│                    (api.ts, geminiService.ts)                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                           │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Endpoints                        │   │
│  │  /api/generate-caption  /api/generate-script           │   │
│  │  /api/generate-voice    /api/generate-video            │   │
│  │  /api/post-instagram    /api/post-youtube              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Service Engines                        │   │
│  │  script_engine  │  voice_engine  │  video_engine      │   │
│  │  caption_engine │  scene_engine   │  ingestion_engine  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Database Layer                       │   │
│  │              SQLModel + SQLite (database.db)             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         ┌─────────┐    ┌───────────┐   ┌───────────┐
         │ Gemini  │    │ElevenLabs│   │ Playwright│
         │   AI    │    │   TTS    │   │  Browser  │
         └─────────┘    └───────────┘   └───────────┘
```

---

## Pattern: Service-Oriented Architecture

The backend follows a modular service engine pattern:

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

---

## Data Flow

### Video Generation Pipeline
1. **Input**: Quote + Philosopher + Settings (rage_level, theme)
2. **Script Generation**: `script_engine` → Gemini AI → Script text
3. **Voice Generation**: `voice_engine` → Eleven Labs → Audio file
4. **Caption Generation**: `caption_engine` → Formatted captions
5. **Video Compilation**: `video_engine` → FFmpeg → Final MP4
6. **Export**: Save to `backend/output/`

### Social Posting Pipeline
1. **Instagram**: `instagram_uploader.py` → Playwright → Post Reel
2. **YouTube**: `youtube_uploader.py` → Playwright → Upload Video

---

## Entry Points

| Component | Entry Point | Port |
|-----------|-------------|------|
| Frontend Dev Server | `npm run dev` | 5173 |
| Backend API | `uvicorn backend.main:app` | 8000 |
| Background Scheduler | `python backend/scheduler.py` | — |

---

## Key Abstractions

- **Database Models**: SQLModel for type-safe ORM
- **Service Registry**: Import-based service discovery
- **Static Assets**: `/assets` and `/output` mounted as FastAPI static
- **Environment**: `.env` files for configuration (backend-specific)

---

*Document created for GSD codebase mapping*