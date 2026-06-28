from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
import json
from app.services.security_service import (
    is_bot_user_agent, is_blocked_path, has_sql_injection, has_xss,
    sanitize_input, is_rate_limited, get_client_ip,
)

SENSITIVE_PATHS = ["/api/auth/login", "/api/auth/register", "/api/auth/change-password"]
LOGIN_PATH = "/api/auth/login"
REGISTER_PATH = "/api/auth/register"

CONTENT_TYPES = {
    "POST": "application/json",
    "PUT": "application/json",
    "PATCH": "application/json",
}

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://*.vercel.app wss:; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    ),
}


async def security_middleware(request: Request, call_next):
    ip = get_client_ip(request)
    path = request.url.path
    method = request.method

    if method == "OPTIONS":
        return await call_next(request)

    if is_blocked_path(path):
        return JSONResponse(
            status_code=403,
            content={"detail": "Forbidden"},
            headers={"Access-Control-Allow-Origin": "*"},
        )

    ua = request.headers.get("user-agent", "")
    if is_bot_user_agent(ua):
        if path.startswith("/api/"):
            return JSONResponse(
                status_code=403,
                content={"detail": "Automated access not allowed"},
                headers={"Access-Control-Allow-Origin": "*"},
            )

    if path.startswith("/api/"):
        if is_rate_limited(f"ip:{ip}:general", max_requests=60, window=60):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Slow down."},
                headers={
                    "Retry-After": "60",
                    "Access-Control-Allow-Origin": "*",
                },
            )

    if path == LOGIN_PATH and method == "POST":
        if is_rate_limited(f"ip:{ip}:login", max_requests=5, window=60):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many login attempts. Try again in 60 seconds."},
                headers={"Access-Control-Allow-Origin": "*"},
            )

    if path == REGISTER_PATH and method == "POST":
        if is_rate_limited(f"ip:{ip}:register", max_requests=3, window=3600):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many registration attempts from this IP."},
                headers={"Access-Control-Allow-Origin": "*"},
            )

    if method in CONTENT_TYPES and path.startswith("/api/"):
        if path.endswith("/upload") or "/files/upload" in path:
            pass
        else:
            ct = request.headers.get("content-type", "")
            expected = CONTENT_TYPES[method]
            if expected not in ct and ct:
                return JSONResponse(
                    status_code=415,
                    content={"detail": f"Expected {expected} content type"},
                    headers={"Access-Control-Allow-Origin": "*"},
                )

    if method in ("POST", "PUT", "PATCH") and path.startswith("/api/"):
        if path.endswith("/upload") or "/files/upload" in path:
            pass
        else:
            body = await request.body()
            if len(body) > 500000:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"},
                    headers={"Access-Control-Allow-Origin": "*"},
                )
            if body:
                try:
                    data = json.loads(body)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, str):
                                if has_sql_injection(value) or has_xss(value):
                                    return JSONResponse(
                                        status_code=400,
                                        content={"detail": f"Invalid input detected in field: {key}"},
                                        headers={"Access-Control-Allow-Origin": "*"},
                                    )
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, str) and (has_sql_injection(item) or has_xss(item)):
                                return JSONResponse(
                                    status_code=400,
                                    content={"detail": "Invalid input detected"},
                                    headers={"Access-Control-Allow-Origin": "*"},
                                )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    if not path.endswith("/upload") and "/files/" not in path:
                        return JSONResponse(
                            status_code=400,
                            content={"detail": "Invalid JSON in request body"},
                            headers={"Access-Control-Allow-Origin": "*"},
                        )

    try:
        response = await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers={"Access-Control-Allow-Origin": "*"},
        )

    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With, Origin, Accept"

    return response
