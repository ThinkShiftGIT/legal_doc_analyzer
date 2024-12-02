from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Verify Mistral API key
if not os.getenv("MISTRAL_API_KEY"):
    raise ValueError("MISTRAL_API_KEY environment variable is not set. Please set it in your .env file.")

from .routes import router

# Initialize FastAPI app
app = FastAPI(
    title="Legal Document Analyzer",
    description="API for analyzing legal documents using AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")