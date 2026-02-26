import requests
import psutil
import datetime
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Initialize THOOVARA Client ---
app = FastAPI(title="THOOVARA Client", description="Middleman between Web UI and AI Backbone", version="1.0")

# Allow CORS (so browser can send POST requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins (you can restrict later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backbone URL (ai.py server)
BACKBONE_URL = "http://127.0.0.1:8000"

# --- Routes ---
@app.get("/system")
async def system_status():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    battery_status = f"{battery.percent}% {'charging' if battery.power_plugged else 'not charging'}" if battery else "N/A"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "cpu_usage": f"{cpu}%",
        "memory_usage": f"{memory}%",
        "battery": battery_status,
        "time": now,
        "server_status": "ACTIVE"
    }

@app.post("/ask")
async def ask_jarvis(request: dict):
    # Forward prompt to backbone ai.py
    prompt = request.get("prompt", "")
    try:
        response = requests.post(f"{BACKBONE_URL}/ask", json={"prompt": prompt})
        return response.json()
    except Exception as e:
        return {"ai_reply": f"Error contacting backbone: {str(e)}", "search_reply": "N/A"}

if __name__ == "__main__":
    uvicorn.run("thoovara_client:app", host="127.0.0.1", port=9000, reload=True)