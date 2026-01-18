"""Utility API models."""

from pydantic import BaseModel
from typing import Dict


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    message: str


class APIInfoResponse(BaseModel):
    """Response model for API information."""

    message: str
    version: str
    endpoints: Dict[str, Dict[str, str]]
    filters: Dict[str, str]

