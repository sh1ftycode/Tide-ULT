from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="TideULT",
    description="The all-in-one media server that brings everything to shore.",
    version="0.1.0"
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": "TideULT",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to TideULT 🌊",
        "docs": "/docs"
    }