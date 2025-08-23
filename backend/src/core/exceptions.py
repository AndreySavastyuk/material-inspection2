"""
Custom exceptions for the application
"""
from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Базовое исключение приложения"""

    def __init__(
            self,
            status_code: int,
            detail: str,
            headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(BaseAppException):
    """Исключение для случаев, когда ресурс не найден"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class BusinessLogicException(BaseAppException):
    """Исключение для нарушения бизнес-логики"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class PermissionDeniedException(BaseAppException):
    """Исключение для отказа в доступе"""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class AuthenticationException(BaseAppException):
    """Исключение для ошибок аутентификации"""

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ValidationException(BaseAppException):
    """Исключение для ошибок валидации"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class ConflictException(BaseAppException):
    """Исключение для конфликтов данных"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class RateLimitException(BaseAppException):
    """Исключение для превышения лимита запросов"""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )


class ServiceUnavailableException(BaseAppException):
    """Исключение для недоступности сервиса"""

    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )