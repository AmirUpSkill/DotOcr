from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(
    title="DotOCR API",
    description="Backend service for the DotOCR application, powered by Mistral OCR.",
    version="1.0.0"
)

# --- Middleware Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)


# --- API Router Inclusion ---
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health Check"])
def read_root():
    """
    A simple health check endpoint to confirm the API is running.
    """
    return {"status": "ok", "message": "Welcome to the DotOCR API"}