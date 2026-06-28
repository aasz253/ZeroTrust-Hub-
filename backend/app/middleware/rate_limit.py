from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from app.core.config import settings

request_counts: dict[str, list[float]] = defaultdict(list)


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = 60.0

    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if now - t < window
    ]

    if len(request_counts[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."},
        )

    request_counts[client_ip].append(now)
    return await call_next(request)
