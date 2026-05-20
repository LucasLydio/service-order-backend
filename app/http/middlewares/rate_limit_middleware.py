from fastapi import Request, HTTPException, status
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

# Simple in-memory rate limiter
requests_by_ip: Dict[str, list] = defaultdict(list)
REQUESTS_PER_MINUTE = 60


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=1)

    # Clean old requests
    requests_by_ip[client_ip] = [
        req_time for req_time in requests_by_ip[client_ip]
        if req_time > window_start
    ]

    # Check rate limit
    if len(requests_by_ip[client_ip]) >= REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )

    # Record this request
    requests_by_ip[client_ip].append(now)

    response = await call_next(request)
    return response
