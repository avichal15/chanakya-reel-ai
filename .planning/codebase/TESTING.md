# Testing — Test Structure and Practices

## Current Testing Status

**No formal test suite** exists in this project. Testing appears to be done manually via:
- Debug scripts (`debug_captions.py`, `debug_ui.py`, `test_thumb.py`)
- Manual browser testing for Playwright automation
- Console logging and log file inspection

---

## Testing Files (Ad-hoc)

| File | Purpose |
|------|---------|
| `debug_captions.py` | Debug caption generation |
| `debug_ui.py` | Debug UI/rendering issues |
| `test_thumb.py` | Test thumbnail generation |
| `test_buffer_run.py` | Test buffer upload functionality |
| `test_full_pipeline.py` | End-to-end pipeline test |

---

## Recommended Testing Approach

### Frontend (React)
- **Framework**: Vitest or Jest
- **Coverage**: Component rendering, API service functions
- **Pattern**: `*.test.tsx` files alongside components

### Backend (Python)
- **Framework**: pytest
- **Coverage**: Service engines, API endpoints
- **Pattern**: `tests/` directory with `test_*.py` files

### E2E Testing
- **Playwright** already installed for browser automation
- Use for end-to-end testing of:
  - Video generation pipeline
  - Instagram posting flow
  - YouTube upload flow

---

## Log Files

| File | Purpose |
|------|---------|
| `backend/scheduler.log` | Scheduler execution logs |
| `backend/startup.log` | Backend startup logs |
| `backend_debug.log` | General backend debug output |
| `frontend.log` | Frontend console logs |

---

*Document created for GSD codebase mapping*