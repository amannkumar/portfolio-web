import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app 
from fastapi import FastAPI

root_app = FastAPI()
root_app.mount("/api", app)

app = root_app