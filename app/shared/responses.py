from typing import Any, Optional
from pydantic import BaseModel


class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


def success_response(message: str, data: Any = None) -> StandardResponse:
    return StandardResponse(success=True, message=message, data=data)


def error_response(message: str, error: str = None) -> StandardResponse:
    return StandardResponse(success=False, message=message, error=error)
