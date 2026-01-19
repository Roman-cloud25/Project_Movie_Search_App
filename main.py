from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from routes import pages

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(pages.router)
