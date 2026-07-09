# Conventions — Code Style, Patterns, and Best Practices

## Frontend Conventions (React/TypeScript)

### Component Structure
- Functional components with hooks
- TypeScript for all components (`.tsx` extension)
- Props interface defined at top of file

### Example
```tsx
interface Props {
  title: string;
  onSubmit: () => void;
}

export function MyComponent({ title, onSubmit }: Props) {
  return (
    <div className="p-4">
      <h1>{title}</h1>
      <button onClick={onSubmit}>Submit</button>
    </div>
  );
}
```

### Styling
- Tailwind CSS classes (no custom CSS files)
- Responsive design with mobile-first approach
- Dark mode support where applicable

### API Communication
- Use `services/api.ts` for HTTP calls
- Axios for HTTP requests
- Async/await pattern

---

## Backend Conventions (Python/FastAPI)

### Function Naming
- `snake_case` for all functions and variables
- `PascalCase` for classes

### FastAPI Patterns
```python
@app.post("/api/endpoint")
def handler(request: RequestModel):
    try:
        result = service.method(request)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Database Models (SQLModel)
```python
class Quote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    philosopher: str
```

### Error Handling
- Use `try/except` blocks
- Return proper HTTP status codes
- Logging with `logging.getLogger(__name__)`

---

## TypeScript Types (types.ts)

Defined types include:
- `Video` — Video metadata
- `Quote` — Quote data
- `Philosopher` — Philosopher info
- `Script` — Generated script
- `ApiResponse` — Standard API response wrapper

---

## Git Conventions

- Commit messages: `type: description` (e.g., `feat: add new API endpoint`)
- Types: `feat`, `fix`, `docs`, `chore`, `refactor`
- GSD planning docs committed separately

---

## File Organization

| Type | Location |
|------|----------|
| React Components | `components/` or `pages/` |
| Backend Services | `backend/services/` |
| Database Models | `backend/database.py` |
| API Endpoints | `backend/main.py` |
| Types | `types.ts` |
| API Client | `services/api.ts` |

---

## Configuration

- **Frontend**: Environment variables in `.env.local`
- **Backend**: Environment variables in `backend/.env`
- Never commit secrets to git (both `.env` files in `.gitignore`)

---

*Document created for GSD codebase mapping*