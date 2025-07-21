## main.py
from routers import analyze_repo_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import generate_doc_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
@app.get("/", tags=["Health"])
async def health_check():
    """
    Root health check endpoint.
    """
    return {"status": "ok", "message": "Service is up and running"}

app.include_router(analyze_repo_router.router, tags=["Analyze Repo"])
app.include_router(generate_doc_router.router, tags=["Generate Doc"])
