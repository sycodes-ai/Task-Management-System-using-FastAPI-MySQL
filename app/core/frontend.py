from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

# Paths that never fall back to index.html: unknown API routes and missing
# build files must stay real 404s instead of being hidden behind the React page.
BACKEND_PREFIXES = ("/api", "/assets")

def frontend_available(static_dir: Path) -> bool:
    return (static_dir / "index.html").is_file()

def _is_backend_path(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in BACKEND_PREFIXES)

def _static_file(static_dir: Path, path: str):
    """Return a file from the build folder (e.g. /vite.svg), or None. Never leaves static_dir."""
    root = static_dir.resolve()
    candidate = (root / path.lstrip("/")).resolve()
    if candidate != root and candidate.is_relative_to(root) and candidate.is_file():
        return candidate
    return None

def add_frontend(app: FastAPI, static_dir: Path) -> None:
    """
    Serve the React build: hashed files from /assets, and index.html for every
    other GET that no route matched, so React Router can handle /login, /register, ...
    API routes, /docs and /openapi.json are matched first because they are routes.
    """
    index_file = static_dir / "index.html"
    if (static_dir / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.exception_handler(StarletteHTTPException)
    async def spa_fallback(request: Request, exc: StarletteHTTPException):
        path = request.url.path
        if exc.status_code == 404 and request.method in ("GET", "HEAD") and not _is_backend_path(path):
            file = _static_file(static_dir, path)
            if file is not None:
                return FileResponse(file)
            # index.html must not be cached, so a new deploy is picked up straight away
            return FileResponse(index_file, headers={"Cache-Control": "no-cache"})
        return await http_exception_handler(request, exc)
