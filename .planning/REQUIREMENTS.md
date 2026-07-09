# Requirements — v1 Requirements

## v1 Requirements

### Core Functionality (CORE)

- [ ] **CORE-01**: User can add, edit, and delete philosophical quotes
- [ ] **CORE-02**: User can manage philosopher database (add, edit, delete)
- [ ] **CORE-03**: User can generate AI-powered video scripts from quotes using Gemini
- [ ] **CORE-04**: User can generate voice audio from scripts using Eleven Labs
- [ ] **CORE-05**: User can compile videos with audio, background video, captions using FFmpeg
- [ ] **CORE-06**: User can generate viral-style captions for social media
- [ ] **CORE-07**: User can post generated videos to Instagram Reels via Playwright
- [ ] **CORE-08**: User can upload generated videos to YouTube Shorts via Playwright
- [ ] **CORE-09**: User can view dashboard with generated videos and posting status

### User Interface (UI)

- [ ] **UI-01**: Dashboard page displays list of generated videos with status
- [ ] **UI-02**: Studio page allows creating new video with quote selection
- [ ] **UI-03**: Library page shows all quotes and philosophers
- [ ] **UI-04**: History page shows past generated videos and posts

### API & Backend (API)

- [ ] **API-01**: REST API endpoints for all CRUD operations
- [ ] **API-02**: Proper error handling with meaningful error messages
- [ ] **API-03**: CORS configured for frontend development

### Configuration (CONFIG)

- [ ] **CONFIG-01**: Environment variables for all API keys
- [ ] **CONFIG-02**: Database connection configurable via environment

---

## v2 Requirements (Deferred)

### Enhanced Features

- [ ] Multi-language support (Hindi, English, regional languages)
- [ ] Rage level control (adjust tone from calm to aggressive)
- [ ] Theme selection (Harsh Truths, Motivation, etc.)
- [ ] Background music with intelligent selection
- [ ] Auto B-roll using Pexels stock videos
- [ ] Smart SFX (sound effects synced to content)
- [ ] Buffer integration for post scheduling

### Platform Features

- [ ] Analytics dashboard with engagement metrics
- [ ] Multi-user support with role-based access
- [ ] Team collaboration features

### Technical Improvements

- [ ] PostgreSQL for production database
- [ ] Celery background job queue
- [ ] CDN for video storage

---

## Out of Scope

The following are explicitly NOT building in v1:

| Feature | Reason |
|---------|--------|
| Mobile app | Responsive web sufficient |
| Live streaming | Pre-recorded content only |
| Team collaboration | Single user operation |
| Analytics | Post-v1 feature |
| Desktop app | Web-only for now |

---

## Traceability

| Requirement | Phase (to be mapped by roadmap) |
|-------------|-------------------------------|
| CORE-01 | TBD |
| CORE-02 | TBD |
| CORE-03 | TBD |
| CORE-04 | TBD |
| CORE-05 | TBD |
| CORE-06 | TBD |
| CORE-07 | TBD |
| CORE-08 | TBD |
| CORE-09 | TBD |
| UI-01 | TBD |
| UI-02 | TBD |
| UI-03 | TBD |
| UI-04 | TBD |
| API-01 | TBD |
| API-02 | TBD |
| API-03 | TBD |
| CONFIG-01 | TBD |
| CONFIG-02 | TBD |

---

*Requirements document created for GSD project initialization*
*Last updated: 2026-03-28*