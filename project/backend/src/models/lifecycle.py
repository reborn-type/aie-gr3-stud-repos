from contextlib import asynccontextmanager
from fastapi import FastAPI
from models.inference import load_model, load_tokenizer

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = load_model()
    app.state.tokenizer = load_tokenizer()
    yield
    app.state.model = None
    app.state.tokenizer = None