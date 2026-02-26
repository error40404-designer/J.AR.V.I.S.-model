# --- Imports ---
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import psutil, datetime, sqlite3, pyttsx3, os, random
import speech_recognition as sr
from transformers import pipeline
from duckduckgo_search import DDGS
import openai
import wikipedia

# --- Initialize Hugging Face local model (backup) ---
generator = pipeline("text-generation", model="microsoft/DialoGPT-small")

# --- Initialize Server ---
app = FastAPI(title="THOOVARA Server", description="AI Assistant Backend", version="5.0")

# --- Voice Announcement on Startup ---
tts = pyttsx3.init()
tts.say("JARVIS Thoovara server online")
tts.runAndWait()

# --- Database Setup ---
DB_FILE = "jarvis_history.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    prompt TEXT,
    ai_reply TEXT,
    search_reply TEXT
)
""")
conn.commit()

# --- Cache (simple dictionary) ---
cache = {}

# --- Request Model ---
class PromptRequest(BaseModel):
    prompt: str

# --- Helper: Decide if query needs search ---
def needs_search(prompt: str) -> bool:
    keywords = ["what", "who", "when", "where", "define", "explain", "information", "history"]
    return any(prompt.lower().startswith(k) for k in keywords)

# --- Core AI Function ---
def process_prompt(prompt: str):
    # Check cache
    if prompt in cache:
        return cache[prompt]

    pl = prompt.lower()

    # --- Command Routing ---
    if "open" in pl and "edge" in pl:
        os.system('start microsoft-edge:https://www.google.com')
        return {"ai_reply": "Opening Microsoft Edge...", "search_reply": "Search not used"}

    elif "open" in pl and "youtube" in pl:
        os.system('start microsoft-edge:https://www.youtube.com/')
        return {"ai_reply": "Opening YouTube...", "search_reply": "Search not used"}

    elif "open" in pl and "spotify" in pl:
        os.system('start microsoft-edge:https://open.spotify.com/')
        return {"ai_reply": "Opening Spotify...", "search_reply": "Search not used"}

    elif "open" in pl and "netflix" in pl:
        os.system('start netflix:')
        return {"ai_reply": "Opening Netflix...", "search_reply": "Search not used"}

    elif "open" in pl and ("cmd" in pl or "command prompt" in pl):
        os.system('start cmd')
        return {"ai_reply": "Opening Command Prompt...", "search_reply": "Search not used"}

    elif "open" in pl and ("explorer" in pl or "file explorer" in pl):
        os.system('explorer')
        return {"ai_reply": "Opening File Explorer...", "search_reply": "Search not used"}

    elif "open" in pl and ("code" in pl or "visual studio" in pl):
        os.system('code')
        return {"ai_reply": "Opening Visual Studio Code...", "search_reply": "Search not used"}

    elif "open" in pl:
        words = pl.split()
        try:
            idx = words.index("open")
            site = words[idx+1]
            url = f"https://{site}.com"
            os.system(f'start microsoft-edge:{url}')
            return {"ai_reply": f"Opening {site.title()}...", "search_reply": "Search not used"}
        except Exception:
            return {"ai_reply": "I couldn't detect the website name.", "search_reply": "Search not used"}

    # --- Wikipedia Integration for explain/what ---
    if pl.startswith("explain") or pl.startswith("what"):
        try:
            summary = wikipedia.summary(prompt, sentences=2)
            ai_reply = summary
        except Exception:
            ai_reply = "I couldn't fetch Wikipedia info right now."
    else:
        # --- Conversational AI (Groq API first, fallback to local model) ---
        ai_reply = None
        try:
            # Save your Groq API key here later
            JARVIS = "YOUR_GROQ_KEYgsk_adUEM7ycipUC1ZeJXB5LWGdyb3FYNRBEhNx72di50WVhfFqCiQzR"
            openai.api_base = "https://api.groq.com/openai/v1"
            openai.api_key = JARVIS

            response = openai.ChatCompletion.create(
                model="mixtral-8x7b",
                messages=[{"role": "user", "content": prompt}]
            )
            ai_reply = response["choices"][0]["message"]["content"].strip()

        except Exception:
            # Fallback to local Hugging Face model
            try:
                ai_output = generator(prompt, max_length=100, num_return_sequences=1)
                full_text = ai_output[0]["generated_text"]
                ai_reply = full_text[len(prompt):].strip()
                if "." in ai_reply:
                    ai_reply = ai_reply.split(".")[0] + "."
                if not ai_reply:
                    ai_reply = "I heard you, but I couldn't generate a proper answer."
            except Exception:
                # Final randomized fun fallback
                fallbacks = [
                    "MODULE ERROR — Follow HARI on Instagram!",
                    "SYSTEM MALFUNCTION — DM error_404_hari!",
                    "AI GLITCH — Support Hari on Insta!",
                    "JARVIS BUG — Ping Hari on Instagram!"
                ]
                ai_reply = random.choice(fallbacks)

    # --- Search response (DuckDuckGo free API) ---
    search_reply = None
    if needs_search(prompt):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(prompt, max_results=1))
                if results:
                    search_reply = f"{results[0]['title']}: {results[0]['body']} ({results[0]['href']})"
        except Exception as e:
            search_reply = f"Error from search: {str(e)}"

    # --- Save to DB ---
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO history (timestamp, prompt, ai_reply, search_reply) VALUES (?, ?, ?, ?)",
                   (now, prompt, ai_reply, search_reply if search_reply else "Search not used"))
    conn.commit()

    result = {"prompt": prompt, "ai_reply": ai_reply,
              "search_reply": search_reply if search_reply else "Search not used"}
    cache[prompt] = result
    return result

# --- Routes ---
@app.get("/")
async def home():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    battery_status = f"{battery.percent}% {'charging' if battery.power_plugged else 'not charging'}" if battery else "N/A"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"server_status": "ACTIVE", "time": now,
            "cpu_usage": f"{cpu}%", "memory_usage": f"{memory}%",
            "battery": battery_status, "details": "THOOVARA server is running"}

@app.post("/ask")
async def ask_jarvis(request: PromptRequest):
    return process_prompt(request.prompt)

# --- Web UI Integration ---
templates = Jinja2Templates(directory="templates")

@app.get("/ui", response_class=HTMLResponse)
async def ui(request: Request):
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    battery_status = f"{battery.percent}% {'charging' if battery.power_plugged else 'not charging'}" if battery else "N/A"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return templates.TemplateResponse("jarvis.html", {
        "request": request,
        "cpu_usage": f"{cpu}%",
        "memory_usage": f"{memory}%",
        "battery": battery_status,
        "time": now
    })

# --- Shutdown Hook ---
import atexit
def shutdown_message():
    print("JARVIS SHUTTING DOWN, follow error_404_hari on INSTA")
atexit.register(shutdown_message)