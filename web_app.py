from fastapi import FastAPI
from database import load_systems, init_db, DB_PATH
from star_system_app import StarSystemApp
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi import Header, HTTPException
import os

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

# Simple access protection
ADMIN_KEY = os.getenv("ADMIN_KEY", "")

@app.post("/import")
def import_from_web(admin_key: str = Header(None)):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_count = app_logic.import_from_web()
    return {"imported": new_count}

@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    systems = load_systems()

    html = """
    <html>
    <head>
        <title>Star Systems UI</title>
    </head>
    <body>
        <h1>Star Systems UI</h1>
        <h2>Existing Systems</h2>
        <ul>
    """

    for sys in systems:
        html += f"<li>{sys.name} ({sys.star_type}) - {sys.distance_from_earth:.2f} ly</li>"

    html += """
        </ul>

        <h2>Import New Data</h2>
        <form id="importForm">
          <input type="password" id="key" placeholder="Enter Admin Key" required />
          <button type="submit">Import</button>
        </form>

        <script>
        document.getElementById("importForm").addEventListener("submit", async (e) => {
          e.preventDefault();
          const key = document.getElementById("key").value;
          const res = await fetch('/import', {
            method: 'POST',
            headers: { 'admin-key': key }
          });
          if (res.ok) {
            alert('Import successful!');
            location.reload();
          } else {
            alert('Import failed: Unauthorized');
          }
        });
        </script>
    </body>
    </html>
    """

    return html
