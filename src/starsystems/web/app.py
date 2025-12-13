"""FastAPI web application for StarSystems."""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import threading
from typing import Optional, List

from ..database import DatabaseConnection, StarSystemRepository
from ..services import ExoplanetService, SearchService
from ..config import config

app = FastAPI(title="Star Systems Explorer", version="2.0.0")

# Initialize services
db_conn = DatabaseConnection()
repository = StarSystemRepository(db_conn)
exoplanet_service = ExoplanetService()
search_service = SearchService()

# Templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Admin password from environment
ADMIN_PASSWORD = config.admin_password

# Background import tracking
import_status = {
    "running": False,
    "completed": False,
    "count": 0,
    "error": None
}


@app.on_event("startup")
def startup_event():
    """Initialize database and optionally sync data on startup."""
    db_conn.initialize_schema()
    print(f"✓ Database initialized at {config.db_path}")

    # Auto-sync if database is empty
    if repository.count() == 0:
        print("Database is empty. Starting background data sync...")

        def background_sync():
            import_status["running"] = True
            try:
                systems = exoplanet_service.fetch_systems()
                success, failed = repository.save_batch(systems)
                import_status["count"] = success
                import_status["completed"] = True
                print(f"✓ Background sync complete: {success} systems imported")
            except Exception as e:
                import_status["error"] = str(e)
                print(f"✗ Background sync failed: {e}")
            finally:
                import_status["running"] = False

        thread = threading.Thread(target=background_sync, daemon=True)
        thread.start()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to main systems page."""
    return RedirectResponse(url="/systems")


@app.get("/systems", response_class=HTMLResponse)
async def systems_page(
        request: Request,
        distance: Optional[float] = None,
        spectral_type: Optional[str] = None,
        has_planets: Optional[str] = None,
        name: Optional[str] = None
):
    """Main page showing all star systems with optional filters."""
    # Load all systems
    systems = repository.find_all()

    # Apply filters
    spectral_types_list = None
    if spectral_type:
        spectral_types_list = [st.strip() for st in spectral_type.split(',')]

    has_planets_bool = None
    if has_planets == "true":
        has_planets_bool = True
    elif has_planets == "false":
        has_planets_bool = False

    # Filter systems
    filtered = search_service.filter_systems(
        systems,
        max_distance=distance,
        spectral_types=spectral_types_list,
        has_planets=has_planets_bool
    )

    # Name search
    if name:
        filtered = search_service.search_by_name(filtered, name)

    # Get statistics
    stats = search_service.get_statistics(systems)

    return templates.TemplateResponse(
        "systems.html",
        {
            "request": request,
            "systems": filtered,
            "total_systems": len(systems),
            "filtered_count": len(filtered),
            "stats": stats,
            "import_status": import_status,
            "filters": {
                "distance": distance,
                "spectral_type": spectral_type,
                "has_planets": has_planets,
                "name": name
            }
        }
    )


@app.get("/api/systems")
async def api_systems(
        distance: Optional[float] = None,
        spectral_type: Optional[str] = None,
        has_planets: Optional[bool] = None,
        min_planets: Optional[int] = None,
        name: Optional[str] = None,
        limit: Optional[int] = None
):
    """API endpoint for searching star systems.

    Query Parameters:
        distance: Maximum distance from Earth in light years
        spectral_type: Comma-separated spectral types (e.g., 'G,K,M')
        has_planets: Filter by presence of planets (true/false)
        min_planets: Minimum number of planets
        name: Search by system name (partial match)
        limit: Maximum number of results

    Returns:
        List of star system dictionaries
    """
    systems = repository.find_all()

    # Parse spectral types
    spectral_types_list = None
    if spectral_type:
        spectral_types_list = [st.strip() for st in spectral_type.split(',')]

    # Apply filters
    results = search_service.filter_systems(
        systems,
        max_distance=distance,
        spectral_types=spectral_types_list,
        has_planets=has_planets,
        min_planets=min_planets
    )

    # Name search
    if name:
        results = search_service.search_by_name(results, name)

    # Apply limit
    if limit:
        results = results[:limit]

    return [s.to_dict() for s in results]


@app.get("/api/systems/{system_name}")
async def api_system_detail(system_name: str):
    """Get detailed information about a specific star system.

    Args:
        system_name: Name of the star system

    Returns:
        Star system dictionary with all details
    """
    system = repository.find_by_name(system_name)

    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    return system.to_dict()


@app.get("/api/stats")
async def api_stats():
    """Get database statistics.

    Returns:
        Statistics dictionary
    """
    systems = repository.find_all()
    return search_service.get_statistics(systems)


@app.post("/admin/sync")
async def admin_sync(admin_key: str = Form(...)):
    """Manually trigger data sync from NASA (requires admin password).

    Args:
        admin_key: Admin password

    Returns:
        Redirect to systems page
    """
    if admin_key != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Sync data
    try:
        systems = exoplanet_service.fetch_systems()
        success, failed = repository.save_batch(systems)
        print(f"Manual sync: {success} systems saved, {failed} failed")
    except Exception as e:
        print(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse(url="/systems", status_code=303)


@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    system_count = repository.count()
    return {
        "status": "healthy",
        "database": "connected",
        "systems_count": system_count
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)