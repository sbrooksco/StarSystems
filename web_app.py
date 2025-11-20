from fastapi import FastAPI
from database import load_systems, init_db, DB_PATH
from star_system_app import StarSystemApp

app = FastAPI(title="Star Systems API")
app_logic = StarSystemApp()

@app.on_event("startup")
def on_startup():
    init_db(DB_PATH)
    print(f"Database initialized at {DB_PATH}")

@app.get("/")
def home():
    return {"message": "Star Systems API is running!"}

@app.get("/systems")
def systems():
    return [s.to_dict() for s in load_systems()]

@app.post("/import")
def import_from_web():
    new_count = app_logic.import_from_web()
    return {"imported": new_count}