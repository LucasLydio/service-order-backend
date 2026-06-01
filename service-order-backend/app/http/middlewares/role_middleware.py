from fastapi import Depends, status
from app.http.middlewares.auth_middleware import verify_token
from app.shared.exceptions import AppException


def require_roles(*allowed_roles: str):
    def dependency(current_user: dict = Depends(verify_token)):
        role = (current_user or {}).get("role")
        if not role or role not in allowed_roles:
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN",
                message="You do not have permission to access this resource",
            )
        return current_user

    return dependency

