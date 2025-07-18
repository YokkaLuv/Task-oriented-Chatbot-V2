from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import os
from dotenv import load_dotenv

from chat_routes import router as chat_router
from services.db_service import get_design_data_for_session

load_dotenv()

FRONTEND_DIR = os.getenv("FRONT_END", "frontend")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeaderMiddleware)

app.include_router(chat_router)

@app.get("/design_data/{session_id}")
def get_design_data(session_id: str):
    try:
        data = get_design_data_for_session(session_id)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/ping")
def ping():
    return {"message": "✅ API OK"}

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"error": "index.html not found"})
