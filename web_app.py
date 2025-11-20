from fastapi import FastAPI
from database import load_systems, init_db
from star_system_app import StarSystemApp

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def home():
    return {"message": "Star Systems API is running!"}

@app.get("/systems")
def systems():
    return [s.to_dict() for s in load_systems()]

@app.post("/import")
def import_from_web():
    app_logic = StarSystemApp()
    new_count = app_logic.import_from_web()
    return {"imported": new_count}