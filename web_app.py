from fastapi import FastAPI, Request, Header, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import load_systems, init_db, DB_PATH
from star_system_app import StarSystemApp
import os
import threading

app = FastAPI(title="Star Systems API")
templates = Jinja2Templates(directory="templates")

app_logic = StarSystemApp()

# Admin key
ADMIN_PASSWORD = os.getenv("STARADMIN", "changeme")

# Track import status for UI (optional)
import_status = {"running": False, "last_count": 0}


@app.on_event("startup")
def startup():
    # Initialize database
    init_db(DB_PATH)
    print(f"DB Initialized at {DB_PATH}")

    # Automatically fetch data if DB is empty
    if len(load_systems()) == 0:
        def fetch_data():
            import_status["running"] = True
            count = app_logic.import_from_web()
            import_status["last_count"] = count
            import_status["running"] = False
            print(f"Startup import complete: {count} systems added.")

        threading.Thread(target=fetch_data, daemon=True).start()


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return RedirectResponse("/systems")


@app.get("/systems", response_class=HTMLResponse)
def systems_page(request: Request):
    systems = load_systems()
    return templates.TemplateResponse(
        "systems.html",
        {"request": request, "systems": systems, "import_status": import_status}
    )


@app.post("/import")
def import_route(admin_key: str = Form(...)):
    if admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Run import synchronously on demand
    imported = app_logic.import_from_web()
    print(f"Imported {imported} systems via manual import")
    return RedirectResponse(url="/systems", status_code=303)


@app.get("/search")
def search_data(
    max_distance: float = None,
    min_mass: float = None,
    planet_type: str = None
):
    results = app_logic.systems

    if max_distance is not None:
        results = app_logic.search_by_distance(max_distance)

    if min_mass is not None:
        mass_results = app_logic.search_by_mass(min_mass)
        names = set([sys_name for sys_name, _ in mass_results])
        results = [s for s in results if s.name in names]

    if planet_type:
        type_results = app_logic.search_by_type(planet_type)
        names = set([sys_name for sys_name, _ in type_results])
        results = [s for s in results if s.name in names]

    return [s.to_dict() for s in results]
