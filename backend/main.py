from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import rate_limit_middleware
from app.database.session import engine, Base, SessionLocal
from app.websocket_manager import ws_manager
from app.seed_data import seed_database
from app.core.security import decode_token
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="ZeroTrust Hub - AI-Powered Cybersecurity Dashboard API",
    lifespan=lifespan,
)

setup_cors(app)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.middleware("http")(rate_limit_middleware)

SECURE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


@app.middleware("http")
async def add_secure_headers(request, call_next):
    response = await call_next(request)
    for header, value in SECURE_HEADERS.items():
        response.headers[header] = value
    return response


from app.routers import auth as auth_router_mod
from app.routers import dashboard as dash_router_mod
from app.routers import vulnerabilities as vuln_router_mod
from app.routers import threats as threat_router_mod
from app.routers import scans as scan_router_mod
from app.routers import ai as ai_router_mod
from app.routers import reports as report_router_mod
from app.routers import notifications as notif_router_mod
from app.routers import files as file_router_mod
from app.routers import settings as settings_router_mod
from app.routers import users as user_router_mod
from app.routers import audit_logs as audit_router_mod
from app.routers import api_keys as apikey_router_mod

app.include_router(auth_router_mod.router)
app.include_router(user_router_mod.router)
app.include_router(dash_router_mod.router)
app.include_router(vuln_router_mod.router)
app.include_router(threat_router_mod.router)
app.include_router(scan_router_mod.router)
app.include_router(ai_router_mod.router)
app.include_router(report_router_mod.router)
app.include_router(notif_router_mod.router)
app.include_router(file_router_mod.router)
app.include_router(settings_router_mod.router)
app.include_router(audit_router_mod.router)
app.include_router(apikey_router_mod.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": settings.VERSION, "app": settings.APP_NAME}


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        await websocket.close(code=4001)
        return

    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_notification(user_id, {
                "type": "pong",
                "data": data,
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception:
        ws_manager.disconnect(websocket, user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
