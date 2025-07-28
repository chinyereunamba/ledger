"""
Utility routes (health check, API info, etc.)
"""
from fastapi import APIRouter
from models import HealthResponse, APIInfoResponse

router = APIRouter(tags=["utility"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Ledger API is running"
    )

@router.get("/", response_model=APIInfoResponse)
async def root():
    """API information and available endpoints"""
    return APIInfoResponse(
        message="Welcome to Ledger API",
        version="1.0.0",
        endpoints={
            "expenses": {
                "POST /expenses": "Add a new expense",
                "GET /expenses": "Get all expenses (with optional filters)",
                "PUT /expenses/{date}/{index}": "Edit an expense",
                "DELETE /expenses/{date}/{index}": "Delete an expense"
            },
            "analytics": {
                "GET /summary": "Get expense summary (with optional filters)",
                "GET /stats": "Get comprehensive analytics"
            },
            "utility": {
                "GET /health": "Health check",
                "GET /": "API information"
            }
        },
        filters={
            "date": "YYYY-MM-DD format",
            "week": "Boolean for current week",
            "range": "start_date,end_date format"
        }
    )