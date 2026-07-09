# Project: Chanakya Reel AI

## What This Is

A full-stack web application for generating viral video reels with philosophical quotes from Chanakya and other thinkers. The system generates AI-powered scripts, creates text-to-speech audio, compiles videos with captions, and posts to Instagram/YouTube automatically.

## Core Value

Automate the creation and posting of short-form video content featuring philosophical wisdom, enabling consistent social media presence without manual video production.

---

## Context

### What Exists Already

The project has a complete functional prototype with:

- **React/Vite Frontend**: Dashboard, Studio, Library, and History pages for managing video creation
- **FastAPI Backend**: REST API for all video generation and posting endpoints
- **AI Integration**: Google Gemini for script generation, Eleven Labs for text-to-speech
- **Automation**: Playwright-based Instagram and YouTube posting
- **Database**: SQLite with SQLModel for quotes, scripts, and video metadata

### Key Features Implemented

1. **Script Generation** — AI-generated scripts from philosophical quotes
2. **Voice Synthesis** — Text-to-speech with configurable voice
3. **Video Compilation** — FFmpeg-based video creation with background video, music, and captions
4. **Social Posting** — Automated posting to Instagram Reels and YouTube Shorts
5. **Dashboard** — Monitor generated videos and posting status

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 6, TypeScript, Tailwind CSS |
| Backend | Python FastAPI, SQLModel, SQLite |
| AI | Google Gemini, Eleven Labs |
| Automation | Playwright |
| Video | FFmpeg |

---

## Stated Constraints

- Must work with existing database (`database.db`)
- Browser automation requires Playwright with existing profiles
- Environment configuration via `.env` files
- CORS configured for `localhost:5173`

---

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Brownfield initialization | Existing codebase mapped | Initialized with validated requirements from code |

---

## Requirements

### Validated

- ✓ React frontend with Vite build system — existing
- ✓ FastAPI backend with REST endpoints — existing
- ✓ SQLite database with SQLModel — existing
- ✓ Google Gemini script generation — existing
- ✓ Eleven Labs voice synthesis — existing
- ✓ FFmpeg video compilation — existing
- ✓ Playwright Instagram posting — existing
- ✓ Playwright YouTube upload — existing

### Active

- [ ] Enhanced error handling and logging
- [ ] Rate limiting on API endpoints
- [ ] Type annotations for Python backend
- [ ] Formal test suite (pytest + Vitest)
- [ ] CORS restriction to production domain
- [ ] Background job queue for video processing

### Out of Scope

- [Desktop app] — Web-only for now
- [Multi-user] — Single user operation
- [Analytics] — Future phase
- [Mobile app] — Responsive web sufficient

---

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

---
*Last updated: 2026-03-28 after initialization*