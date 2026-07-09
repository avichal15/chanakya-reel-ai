# Architecture — System Design for Video Reel Generation

## Overview

The application follows a client-server architecture with a REST API backend and React frontend. Video generation is a pipeline of AI services, and social posting uses browser automation.

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  Dashboard → Studio → Library → History                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST
┌──────────────────────────▼──────────────────────────────────┐
│                      FastAPI Backend                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ API Layer    │  │ Service      │  │ Database         │ │
│  │ (main.py)    │  │ Engines      │  │ (SQLModel/SQLite)│ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
│         │                 │                                  │
│         ▼                 ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Video Generation Pipeline                │   │
│  │  Script → Voice → Caption → Video → Export           │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Social Posting Pipeline                  │   │
│  │  Instagram (Playwright) │ YouTube (Playwright)      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
  Gemini              Eleven Labs            Playwright
  (AI Script)         (TTS)                   (Browser)
```

---

## Service Engines (Backend)

| Engine | Responsibility |
|--------|---------------|
| `script_engine.py` | Generate scripts via Gemini |
| `voice_engine.py` | Text-to-speech via Eleven Labs |
| `video_engine.py` | FFmpeg video compilation |
| `caption_engine.py` | Generate viral captions |
| `scene_engine.py` | Scene detection/management |
| `ingestion_engine.py` | Quote/philosopher data |
| `ass_engine.py` | ASS subtitle generation |
| `viral_caption_engine.py` | Social-optimized captions |
| `thumbnail_engine.py` | Thumbnail generation |
| `pexels_engine.py` | Stock video search |

---

## Data Flow

### Video Generation Flow
1. **Input**: Quote + Philosopher + Settings
2. **Script**: `script_engine.generate_script()` → Gemini → Script text
3. **Voice**: `voice_engine.generate_voice()` → Eleven Labs → Audio file
4. **Caption**: `caption_engine.generate_caption()` → Formatted text
5. **Video**: `video_engine.generate_video()` → FFmpeg → MP4
6. **Output**: Saved to `backend/output/`

### Social Posting Flow
1. **Instagram**: `instagram_uploader.py` → Playwright → Post
2. **YouTube**: `youtube_uploader.py` → Playwright → Upload

---

## Suggested Build Order

1. **Phase 1**: Core API + Script Generation (foundation)
2. **Phase 2**: Voice Synthesis + Video Compilation
3. **Phase 3**: Social Posting Integration
4. **Phase 4**: UI Enhancements + Testing

---

## Integration Points

| External Service | Integration |
|-----------------|-------------|
| Google Gemini | REST API (SDK) |
| Eleven Labs | REST API (voice synthesis) |
| Pexels | REST API (stock video) |
| Playwright | Browser automation |
| Buffer | REST API (scheduling) |

---

*Research document created for GSD project initialization*