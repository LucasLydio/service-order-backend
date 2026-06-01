from app.shared.security import decode_access_token
from app.shared.exceptions import UnauthorizedException, InvalidTokenException
from fastapi import Header


def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise UnauthorizedException()

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException()

    token = parts[1]
    payload = decode_access_token(token)

    if payload is None:
        raise InvalidTokenException()

    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role")
    }

