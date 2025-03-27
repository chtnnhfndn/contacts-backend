from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError
from typing import Optional, Dict, Any


class ErrorResponse(BaseModel):
    """
    Standard error response model
    """

    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ContactsException(HTTPException):
    """
    Custom exception for application-specific errors
    """

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_response = ErrorResponse(
            error_code=error_code, message=message, details=details
        )
        super().__init__(status_code=status_code, detail=error_response.model_dump())


def handle_validation_error(exc: ValidationError) -> ContactsException:
    """
    Convert Pydantic validation errors to a standardized error response
    """
    error_details = {
        error["loc"][-1]: {"type": error["type"], "msg": error["msg"]}
        for error in exc.errors()
    }

    return ContactsException(
        error_code="VALIDATION_ERROR",
        message="Invalid input data",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=error_details,
    )


def database_error_handler(error: Exception) -> ContactsException:
    """
    Convert database-related exceptions to standardized error responses
    """
    if "unique constraint" in str(error).lower():
        return ContactsException(
            error_code="DUPLICATE_ENTRY",
            message="A record with these details already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    return ContactsException(
        error_code="DATABASE_ERROR",
        message="An error occurred while processing the database request",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"original_error": str(error)},
    )


def authentication_error_handler(error: Exception) -> ContactsException:
    """
    Convert authentication-related exceptions
    """
    return ContactsException(
        error_code="AUTH_ERROR",
        message="Authentication failed",
        status_code=status.HTTP_401_UNAUTHORIZED,
        details={"original_error": str(error)},
    )
