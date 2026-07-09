# Pitfalls — Common Mistakes to Avoid

## Video Generation Pitfalls

### 1. FFmpeg Dependency Missing
- **Warning**: Video generation fails if FFmpeg not installed
- **Prevention**: Add startup check for FFmpeg availability
- **Phase**: Video compilation phase

### 2. Background Video/Music Path Issues
- **Warning**: `None` values cause type errors in video_engine
- **Prevention**: Add null checks and default fallbacks
- **Phase**: Video compilation phase

### 3. Audio/Video Sync
- **Warning**: Caption timing may drift from audio
- **Prevention**: Use video_engine's built-in sync features
- **Phase**: Testing/verification

---

## Browser Automation Pitfalls

### 4. Playwright Session Expiration
- **Warning**: Instagram/YouTube sessions expire, causing auth failures
- **Prevention**: Implement session refresh mechanism
- **Phase**: Social posting phase

### 5. UI Selectors Breaking
- **Warning**: Instagram/YouTube UI changes break Playwright selectors
- **Prevention**: Use stable selectors, add selector validation
- **Phase**: Social posting phase

### 6. Captcha Challenges
- **Warning**: Login may trigger captcha, blocking automation
- **Prevention**: Use 2FA app instead of password, monitor for captcha
- **Phase**: Social posting phase

---

## AI Integration Pitfalls

### 7. Gemini API Rate Limits
- **Warning**: High volume of script generation hits rate limits
- **Prevention**: Add request throttling, queue system
- **Phase**: Script generation phase

### 8. Eleven Labs Voice Limits
- **Warning**: Character limits on free tier
- **Prevention**: Track usage, alert on limits
- **Phase**: Voice synthesis phase

### 9. Prompt Engineering Quality
- **Warning**: Poor prompts = low quality scripts
- **Prevention**: Test prompts, iterate on quality
- **Phase**: Script generation phase

---

## Database Pitfalls

### 10. SQLite Concurrency
- **Warning**: SQLite doesn't handle concurrent writes well
- **Prevention**: Use connection pooling, or upgrade to PostgreSQL
- **Phase**: Database layer

### 11. Data Migration
- **Warning**: Schema changes break existing data
- **Prevention**: Use Alembic for migrations
- **Phase**: Database layer

---

## Production Pitfalls

### 12. CORS Misconfiguration
- **Warning**: `allow_origins=["*"]` is insecure
- **Prevention**: Restrict to production domain
- **Phase**: API security

### 13. No Rate Limiting
- **Warning**: API can be overwhelmed by requests
- **Prevention**: Add FastAPI rate limiting
- **Phase**: API security

### 14. Static File Serving
- **Warning**: Large videos served via FastAPI is slow
- **Prevention**: Use CDN or cloud storage (S3)
- **Phase**: Deployment

---

## Testing Pitfalls

### 15. No Automated Tests
- **Warning**: Manual testing misses regressions
- **Prevention**: Add pytest + Vitest
- **Phase**: Testing

---

## Phase Mapping

| Pitfall | Phase to Address |
|---------|-----------------|
| FFmpeg dependency | Video Compilation |
| Path null checks | Video Compilation |
| Audio/video sync | Testing |
| Session expiration | Social Posting |
| UI selector breaks | Social Posting |
| Captcha challenges | Social Posting |
| API rate limits | Script Generation |
| Voice limits | Voice Synthesis |
| Prompt quality | Script Generation |
| SQLite concurrency | Backend Foundation |
| Data migration | Backend Foundation |
| CORS misconfiguration | API Security |
| No rate limiting | API Security |
| Static file serving | Deployment |
| No automated tests | Testing |

---

*Research document created for GSD project initialization*