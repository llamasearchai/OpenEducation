from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory="openeducation/dashboard/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serve the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/api/summary", response_class=JSONResponse)
async def get_summary_data():
    """Fetch summary data from the filesystem."""
    syllabi_path = "data/syllabi"
    coaching_path = "data/coaching"
    progress_path = "data/progress"
    
    syllabi_count = len([f for f in os.listdir(syllabi_path) if f.endswith('.json')]) if os.path.exists(syllabi_path) else 0
    coaching_cycles_count = len([f for f in os.listdir(coaching_path) if f.startswith('cycle_')]) if os.path.exists(coaching_path) else 0
    performance_reports_count = len([f for f in os.listdir(progress_path) if f.endswith('_progress.json')]) if os.path.exists(progress_path) else 0

    return {
        "syllabi_count": syllabi_count,
        "coaching_cycles_count": coaching_cycles_count,
        "performance_reports_count": performance_reports_count,
    }
