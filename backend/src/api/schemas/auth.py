"""Auth API schemas for request/response models - Story 009-02."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Request schema for user login."""

    username: str = Field(..., min_length=1, max_length=50, description="Username")
    password: str = Field(..., min_length=1, description="Password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "secure_password",
            }
        }
    )


class LoginResponse(BaseModel):
    """Response schema for successful login."""

    message: str = Field(default="Login successful")


class LogoutResponse(BaseModel):
    """Response schema for logout."""

    message: str = Field(default="Logout successful")


class UserResponse(BaseModel):
    """Response schema for current user info."""

    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeResponse(BaseModel):
    """Response schema for /me endpoint."""

    data: UserResponse
