# Project Research Summary

**Project:** Chanakya Reel AI
**Domain:** AI Video Generation / Social Media Automation
**Researched:** 2026-03-28
**Confidence:** HIGH

## Executive Summary

Chanakya Reel AI is a full-stack web application for automatically generating and posting viral video reels featuring philosophical quotes. The system combines AI-powered script generation, text-to-speech synthesis, video compilation, and browser-based social media posting into an end-to-end pipeline.

Research confirms the current technology stack (React/Vite/FastAPI/Playwright) is well-suited for this use case. Key differentiators include multi-language support and rage-level controlled content. The main risks are Playwright selector fragility (Instagram/YouTube UI changes), API rate limits, and the lack of a formal test suite.

## Key Findings

### Recommended Stack

The existing stack is validated and production-ready for v1:
- React 19 + Vite 6 for fast frontend development with hot module reload
- FastAPI + SQLModel + SQLite for rapid backend development with type-safe ORM
- Playwright for reliable cross-browser automation
- FFmpeg for industry-standard video processing
- Google Gemini + Eleven Labs for AI content generation

**Core technologies:**
- **React/Vite**: Fast HMR, modern React features, excellent DX
- **FastAPI**: Python async, auto OpenAPI docs, easy to extend
- **Playwright**: Cross-browser support, reliable selectors
- **FFmpeg**: Full-featured video processing, well-documented

### Expected Features

**Must have (table stakes):**
- Quote/Philosopher management
- AI script generation via Gemini
- Voice synthesis via Eleven Labs
- Video compilation via FFmpeg
- Caption generation
- Instagram Reels posting via Playwright
- YouTube Shorts upload via Playwright
- Dashboard for monitoring

**Should have (competitive):**
- Multi-language support (Hindi, English)
- Rage level control (tone adjustment)
- Theme selection (Harsh Truths, Motivation, etc.)
- Background music integration
- Auto B-roll (Pexels stock videos)
- Buffer scheduling integration

**Defer (v2+):**
- Analytics dashboard
- Multi-user system
- Mobile app
- Team collaboration

### Architecture Approach

The application uses a client-server architecture with a REST API backend. Video generation follows a sequential pipeline: Script → Voice → Caption → Video. Social posting uses browser automation with Playwright profiles for session management.

**Major components:**
1. **Frontend (React)**: Dashboard, Studio, Library, History pages
2. **Backend (FastAPI)**: Service engines for each pipeline stage
3. **Database (SQLite)**: Quotes, scripts, video metadata
4. **AI Layer**: Gemini (scripts), Eleven Labs (voice)
5. **Automation Layer**: Playwright (Instagram/YouTube)

### Critical Pitfalls

1. **Playwright UI Selector Fragility** — Instagram/YouTube UI updates break automation; use stable selectors and validate
2. **Session Expiration** — Browser sessions expire causing auth failures; implement refresh mechanism
3. **FFmpeg Dependency** — Video generation fails without FFmpeg; add startup validation
4. **API Rate Limits** — Gemini/Eleven Labs rate limits cause failures; add throttling
5. **No Automated Tests** — Manual testing misses regressions; add pytest + Vitest
6. **SQLite Concurrency** — Not ideal for production with multiple users; consider PostgreSQL

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Backend Foundation
**Rationale:** Core API and database layer must exist first
**Delivers:** FastAPI endpoints, SQLModel schemas, error handling, type annotations
**Addresses:** API-01, API-02, API-03, DB-01 from features
**Avoids:** Database pitfall (proper schema from start)

### Phase 2: Script & Voice Generation
**Rationale:** AI content generation is the core value
**Delivers:** Script engine integration, voice engine integration
**Addresses:** Script generation, voice synthesis features
**Avoids:** API rate limit pitfall (add throttling)

### Phase 3: Video Compilation
**Rationale:** Core video processing depends on script+voice
**Delivers:** Video engine, caption generation, FFmpeg pipeline
**Addresses:** Video compilation, caption generation
**Avoids:** FFmpeg dependency pitfall (validate on startup)

### Phase 4: Social Posting
**Rationale:** Platform posting completes the value chain
**Delivers:** Instagram posting, YouTube upload, session management
**Addresses:** Instagram posting, YouTube upload
**Avoids:** Selector fragility pitfall (use stable selectors)

### Phase 5: Testing & Polish
**Rationale:** Ensure quality before production use
**Delivers:** pytest test suite, Vitest frontend tests, error handling
**Addresses:** Test coverage, reliability improvements
**Avoids:** No automated tests pitfall

### Phase Ordering Rationale

- Backend first provides foundation for all subsequent phases
- Script+Voice before Video Compilation (dependency)
- Video before Social Posting (needs video output)
- Testing last ensures everything works together

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (Social Posting):** Playwright selectors change frequently — needs research on selector stability
- **Phase 3 (Video Compilation):** FFmpeg has many options — needs research on optimal encoding settings

Phases with standard patterns (skip research-phase):
- **Phase 1 (Backend):** FastAPI patterns well-documented
- **Phase 2 (Script/Voice):** Standard API integration

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Current stack validated, well-suited |
| Features | HIGH | Features from existing codebase |
| Architecture | HIGH | Pipeline pattern confirmed in code |
| Pitfalls | HIGH | Identified from code analysis |

**Overall confidence:** HIGH

### Gaps to Address

- **Pexels API specifics**: Need to verify API key requirements and rate limits
- **Buffer API integration**: Verify current API and scheduling capabilities

## Sources

### Primary (HIGH confidence)
- Existing codebase analysis — `.codex/get-shit-done/` codebase mapping
- FastAPI official documentation
- Playwright official documentation

### Secondary (MEDIUM confidence)
- Gemini API documentation — general patterns
- Eleven Labs API documentation — general patterns

### Tertiary (LOW confidence)
- Pexels API — needs verification during implementation

---

*Research completed: 2026-03-28*
*Ready for roadmap: yes*