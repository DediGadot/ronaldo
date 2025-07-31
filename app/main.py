from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine
from . import models
from .api import app as api_app

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
