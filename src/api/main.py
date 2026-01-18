"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import route modules
from .routes.expenses import router as expenses_router
from .routes.analytics import router as analytics_router
from .routes.utility import router as utility_router
from .routes.nlp import router as nlp_router
from .routes.budget import router as budget_router

# Create FastAPI app
app = FastAPI(
    title="Ledger API",
    description="A comprehensive API for expense tracking and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expenses_router)
app.include_router(analytics_router)
app.include_router(utility_router)
app.include_router(nlp_router)
app.include_router(budget_router)

