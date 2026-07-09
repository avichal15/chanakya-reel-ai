# Features — Product Requirements Analysis

## Table Stakes (Must Have)

These features are expected by users and must be present:

1. **Quote Management** — Add, edit, delete philosophical quotes
2. **Philosopher Database** — Store and categorize philosophers (Chanakya, etc.)
3. **Script Generation** — AI-generated video scripts from quotes
4. **Voice Synthesis** — Text-to-speech for video narration
5. **Video Compilation** — Combine audio, background video, captions into MP4
6. **Caption Generation** — Viral-style captions for social media
7. **Instagram Posting** — Automated reel posting via Playwright
8. **YouTube Upload** — Automated short video upload via Playwright
9. **Dashboard** — View generated videos and posting status

---

## Differentiators (Competitive Advantage)

Features that set this apart:

1. **Multi-language Support** — Hindi, English, regional languages
2. **Rage Level Control** — Adjust tone from calm to aggressive
3. **Theme Selection** — Predefined themes (Harsh Truths, Motivation, etc.)
4. **Background Music** — Intelligent music selection based on mood
5. **Auto B-Roll** — Automatic stock video selection via Pexels
6. **Smart SFX** — Sound effects synced to video content
7. **Buffer Integration** — Schedule posts via Buffer API

---

## Anti-Features (Deliberately NOT Building)

Features out of scope for v1:

1. **Multi-user System** — Single user operation only
2. **Video Editing Studio** — Full video editor (use external tools)
3. **Analytics Dashboard** — View metrics (future phase)
4. **Mobile App** — Responsive web sufficient
5. **Team Collaboration** — Single user workflow
6. **Live Streaming** — Pre-recorded content only

---

## Feature Dependencies

| Feature | Depends On |
|---------|------------|
| Video Compilation | Script Generation, Voice Synthesis |
| Instagram Posting | Video Compilation |
| YouTube Upload | Video Compilation |
| Auto B-Roll | Pexels API integration |
| Buffer Integration | Platform API keys |

---

## Complexity Notes

| Feature | Complexity | Notes |
|---------|------------|-------|
| Script Generation | Medium | Requires Gemini API |
| Video Compilation | High | FFmpeg complexity, many parameters |
| Playwright Posting | High | UI changes break selectors |
| Multi-language | Medium | Prompt engineering + TTS voices |

---

*Research document created for GSD project initialization*