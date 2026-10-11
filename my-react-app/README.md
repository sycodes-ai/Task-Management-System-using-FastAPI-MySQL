# Frontend (React + Vite)

The web app for the Task Management System. See the [main README](../README.md) for the full project, the live demo and the API.

```bash
npm ci          # install dependencies
npm run dev     # dev server on http://localhost:5173 (proxies /api to http://127.0.0.1:8000)
npm run lint    # ESLint
npm run build   # production build in dist/ (FastAPI serves it when it exists)
```

Build-time settings:

- `VITE_API_URL`: API base URL. Default `/api/v1` (same origin).
- `VITE_DEMO_MODE`: set to `false` to hide the demo accounts box on the login page.

Code layout:

- `src/api.js`: Axios client (adds the token, sends you to `/login` on a 401)
- `src/hooks/useTasks.js`: filters, debounced search, pagination and data loading
- `src/components/`: pages (`Login`, `Register`, `Home`, `AdminDashboard`, `StaffDashboard`) and shared parts (`TaskToolbar`, `StatCards`, `Pagination`)
