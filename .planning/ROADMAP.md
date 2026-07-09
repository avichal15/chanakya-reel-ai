# Roadmap: Chanakya Reel AI

## Overview

This roadmap guides the development of Chanakya Reel AI from initial foundation to a fully functional automated video reel generation and posting system. The journey progresses from backend infrastructure through AI integration, video processing, social media automation, and finally quality assurance.

## Phases

- [ ] **Phase 1: Backend Foundation** - FastAPI setup, database models, core API endpoints
- [ ] **Phase 2: Script & Voice Generation** - AI script generation, text-to-speech integration
- [ ] **Phase 3: Video Compilation** - FFmpeg video creation, caption generation
- [ ] **Phase 4: Social Posting** - Instagram Reels, YouTube Shorts automation
- [ ] **Phase 5: Testing & Polish** - Test suite, error handling, UI refinements

## Phase Details

### Phase 1: Backend Foundation
**Goal**: Set up FastAPI backend with database layer and core API endpoints
**Depends on**: Nothing (first phase)
**Requirements**: API-01, API-02, API-03, CONFIG-01, CONFIG-02, CORE-01, CORE-02
**Success Criteria** (what must be TRUE):
  1. FastAPI server starts without errors
  2. Database tables created automatically on startup
  3. API endpoints respond with proper JSON
  4. CORS allows frontend communication
  5. Environment variables load correctly
**Plans**: 3 plans

Plans:
- [ ] 01-01: Set up FastAPI project with SQLModel and SQLite
- [ ] 01-02: Create database models (Quote, Philosopher, GeneratedScript, VideoExport)
- [ ] 01-03: Implement CRUD API endpoints for quotes and philosophers

### Phase 2: Script & Voice Generation
**Goal**: Integrate Google Gemini for script generation and Eleven Labs for voice synthesis
**Depends on**: Phase 1
**Requirements**: CORE-03, CORE-04
**Success Criteria** (what must be TRUE):
  1. Script generation endpoint returns AI-generated script
  2. Voice synthesis endpoint generates audio file
  3. Scripts stored in database with proper metadata
  4. API handles errors gracefully when AI services fail
**Plans**: 2 plans

Plans:
- [ ] 02-01: Integrate Google Gemini for script generation
- [ ] 02-02: Integrate Eleven Labs for text-to-speech

### Phase 3: Video Compilation
**Goal**: Implement video generation pipeline with FFmpeg, including captions
**Depends on**: Phase 2
**Requirements**: CORE-05, CORE-06
**Success Criteria** (what must be TRUE):
  1. Video compilation creates valid MP4 file
  2. Captions appear synchronized with audio
  3. Background video and music integrate correctly
  4. Output saved to backend/output/ directory
  5. API validates FFmpeg availability on startup
**Plans**: 3 plans

Plans:
- [ ] 03-01: Implement video compilation with FFmpeg
- [ ] 03-02: Create caption generation for videos
- [ ] 03-03: Add background music and video integration

### Phase 4: Social Posting
**Goal**: Automate posting to Instagram Reels and YouTube Shorts via Playwright
**Depends on**: Phase 3
**Requirements**: CORE-07, CORE-08
**Success Criteria** (what must be TRUE):
  1. Instagram posting uploads video successfully
  2. YouTube upload publishes video correctly
  3. Session management handles authentication
  4. Post status tracked in database
  5. Failed posts report clear error messages
**Plans**: 2 plans

Plans:
- [ ] 04-01: Implement Instagram Reels posting with Playwright
- [ ] 04-02: Implement YouTube Shorts upload with Playwright

### Phase 5: Testing & Polish
**Goal**: Ensure reliability through testing, improve error handling, refine UI
**Depends on**: Phase 4
**Requirements**: UI-01, UI-02, UI-03, UI-04, CORE-09
**Success Criteria** (what must be TRUE):
  1. Backend has test suite with pytest covering critical paths
  2. Frontend components render correctly
  3. Dashboard displays generated videos with status
  4. Studio page enables video creation workflow
  5. Library and History pages show data correctly
**Plans**: 3 plans

Plans:
- [ ] 05-01: Add pytest test suite for backend
- [ ] 05-02: Add Vitest tests for frontend components
- [ ] 05-03: Verify all UI pages work end-to-end

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Backend Foundation | 0/3 | Not started | - |
| 2. Script & Voice Generation | 0/2 | Not started | - |
| 3. Video Compilation | 0/3 | Not started | - |
| 4. Social Posting | 0/2 | Not started | - |
| 5. Testing & Polish | 0/3 | Not started | - |