# JARVIS History Viewer
import sqlite3, datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

DB_FILE = "jarvis_memory.db"

app = FastAPI(title="JARVIS History Viewer", description="View and search JARVIS history", version="2.0")

# --- Templates and Static ---
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Database Connection ---
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# --- Request Model for Search ---
class SearchRequest(BaseModel):
    query: str

# --- Home Route: Show latest history ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows})

# --- Search Route ---
@app.post("/search", response_class=HTMLResponse)
async def search_history(request: Request, search: SearchRequest):
    q = f"%{search.query}%"
    cursor.execute("SELECT * FROM history WHERE prompt LIKE ? OR ai_reply LIKE ? ORDER BY id DESC", (q, q))
    rows = cursor.fetchall()
    return templates.TemplateResponse("history.html", {"request": request, "rows": rows, "search": search.query})

# --- API Route for JSON access ---
@app.get("/api/history")
async def api_history(limit: int = 20):
    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    return {"history": [{"id": r[0], "timestamp": r[1], "prompt": r[2], "ai_reply": r[3], "search_reply": r[4]} for r in rows]}
