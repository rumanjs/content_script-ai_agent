import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from . import routes
from .database import engine
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Content Script AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/")
async def read_root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Content Script AI Agent is running (Frontend not found)"}

@app.get("/{filename}")
async def read_file(filename: str):
    file_path = os.path.join(frontend_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"message": "File not found"}
