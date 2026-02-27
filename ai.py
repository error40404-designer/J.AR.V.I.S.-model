# coded by error40404-designer
# Any modification or installation must be attributed to the owner.
#This is JARVIS version3 with privacy intergration, tts modulation and countinuos chat.
#This system is still under construction/testing

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import psutil, datetime, sqlite3, pyttsx3, os, random, re, hashlib
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from duckduckgo_search import DDGS
import openai
import wikipedia
import atexit

# --- Initialize Hugging Face local model (backup) ---
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

def hf_generate(prompt: str, history: list) -> str:
    """Generate a conversational reply using Hugging Face DialoGPT with context."""
    inputs = tokenizer.encode(" ".join(history) + prompt + tokenizer.eos_token, return_tensors="pt")
    outputs = model.generate(inputs, max_length=250, pad_token_id=tokenizer.eos_token_id)
    reply = tokenizer.decode(outputs[:, inputs.shape[-1]:][0], skip_special_tokens=True)
    return reply.strip() if reply else "I heard you, but I couldn't generate a proper answer."

# --- Initialize Server ---
app = FastAPI(title="J.A.R.V.I.S. Server", description="AI Assistant Backend", version="6.0")

# --- Voice Announcement on Startup ---
tts = pyttsx3.init()
tts.say("JARVIS server online")
tts.runAndWait()

# --- Database Setup ---
DB_FILE = "jarvis_memory.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# History table
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    prompt TEXT,
    ai_reply TEXT,
    search_reply TEXT
)
""")

# User personalization table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    preferences TEXT,
    last_seen TEXT
)
""")
conn.commit()

# --- Cache (simple dictionary) ---
cache = {}
chat_history = []  # continuous conversation memory

# --- Request Model ---
class PromptRequest(BaseModel):
    prompt: str
    user: str = "Guest"

# --- Privacy Utilities ---
def sanitize_prompt(prompt: str) -> str:
    prompt = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED_EMAIL]", prompt)
    prompt = re.sub(r"\+?\d[\d\s-]{7,}\d", "[REDACTED_PHONE]", prompt)
    prompt = re.sub(r"(instagram|twitter|facebook|in)\s*[:@]?\s*\w+", "[REDACTED_SOCIAL]", prompt, flags=re.IGNORECASE)
    return prompt

def anonymize(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

# --- Voice Output Helper ---
def speak_response(text: str):
    try:
        tts.say(text)
        tts.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

# --- Helper: Decide if query needs search ---
def needs_search(prompt: str) -> bool:
    keywords = ["what", "who", "when", "where", "define", "explain", "information", "history"]
    return any(prompt.lower().startswith(k) for k in keywords)

# --- Core AI Function ---
def process_prompt(prompt: str, user: str = "Guest"):
    safe_prompt = sanitize_prompt(prompt)

    # Check cache
    if safe_prompt in cache:
        result = cache[safe_prompt]
        speak_response(result["ai_reply"])
        return result

    pl = safe_prompt.lower()

    # --- Command Routing ---
        # --- Command Routing ---
    if "open" in pl and "spotify" in pl:
        os.system('start microsoft-edge:https://open.spotify.com/')
        ai_reply = "Opening Spotify..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "youtube" in pl:
        os.system('start microsoft-edge:https://www.youtube.com/')
        ai_reply = "Opening YouTube..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "edge" in pl:
        os.system('start microsoft-edge:https://www.google.com')
        ai_reply = "Opening Microsoft Edge..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "netflix" in pl:
        os.system('start microsoft-edge:https://www.netflix.com/')
        ai_reply = "Opening Netflix..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and ("cmd" in pl or "command prompt" in pl):
        os.system('start cmd')
        ai_reply = "Opening Command Prompt..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and ("explorer" in pl or "file explorer" in pl):
        os.system('explorer')
        ai_reply = "Opening File Explorer..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and ("code" in pl or "visual studio" in pl):
        os.system('code')
        ai_reply = "Opening Visual Studio Code..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "chatgpt" in pl:
        os.system('start microsoft-edge:https://chat.openai.com/')
        ai_reply = "Opening ChatGPT..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "copilot" in pl:
        os.system('start microsoft-edge:https://copilot.microsoft.com/')
        ai_reply = "Opening Microsoft Copilot..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "geofs" in pl:
        os.system('start microsoft-edge:https://www.geo-fs.com/')
        ai_reply = "Opening GeoFS Flight Simulator..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "settings" in pl:
        os.system('start ms-settings:')
        ai_reply = "Opening System Settings..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "xbox" in pl:
        os.system('start xbox:')
        ai_reply = "Opening Xbox..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    elif "open" in pl and "store" in pl:
        os.system('start ms-windows-store:')
        ai_reply = "Opening Microsoft Store..."
        speak_response(ai_reply)
        return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    # --- Fallback: detect word after "open" ---
    else:
        words = pl.split()
        try:
            idx = words.index("open")
            site = words[idx+1]
            url = f"https://{site}.com"
            os.system(f'start microsoft-edge:{url}')
            ai_reply = f"Opening {site.title()}..."
            speak_response(ai_reply)
            return {"ai_reply": ai_reply, "search_reply": "Search not used"}
        except Exception:
            ai_reply = "I couldn't detect the website name."
            speak_response(ai_reply)
            return {"ai_reply": ai_reply, "search_reply": "Search not used"}

    

    # --- Wikipedia Integration ---
    if pl.startswith("explain") or pl.startswith("what"):
        try:
            summary = wikipedia.summary(safe_prompt, sentences=2)
            ai_reply = summary
        except Exception:
            ai_reply = "I couldn't fetch Wikipedia info right now."
        speak_response(ai_reply)

    else:
        # --- Conversational AI (Groq API first, fallback to Hugging Face) ---
        try:
            JARVIS = "GROQ API KEY HERE"
            openai.api_base = "https://api.groq.com/openai/v1"
            openai.api_key = JARVIS

            response = openai.ChatCompletion.create(
                model="mixtral-8x7b",
                messages=[{"role": "user", "content": safe_prompt}]
            )
            ai_reply = response["choices"][0]["message"]["content"].strip()

        except Exception:
            try:
                ai_reply = hf_generate(safe_prompt, chat_history)
            except Exception:
                fallbacks = [
                    "MODULE ERROR — Follow INPUT YOUR NAME HERE!",
                    "SYSTEM MALFUNCTION — Contact INPUT YOUR NAME HERE!",
                    "AI GLITCH — Support INPUT YOUR NAME HERE!",
                    "JARVIS BUG — Ping INPUT YOUR NAME HERE!"
                ]
                ai_reply = random.choice(fallbacks)

        speak_response(ai_reply)

    # --- Search response ---
    search_reply = None
    if needs_search(safe_prompt):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(safe_prompt, max_results=1))
                if results:
                    search_reply = f"{results[0]['title']}: {results[0]['body']} ({results[0]['href']})"
        except Exception as e:
            search_reply = f"Error from search: {str(e)}"

    # --- Save to DB ---
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO history (timestamp, prompt, ai_reply, search_reply) VALUES (?, ?, ?, ?)",
        (now, anonymize(safe_prompt), ai_reply, search_reply if search_reply else "Search not used")
    )
    cursor.execute(
        "INSERT INTO users (name, preferences, last_seen) VALUES (?, ?, ?)",
        (user, "{}", now)
    )
    conn.commit()

    # Update continuous chat memory
    chat_history.append(f"User: {safe_prompt}")
    chat_history.append(f"JARVIS: {ai_reply}")

    result = {"prompt": safe_prompt, "ai_reply": ai_reply,
              "search_reply": search_reply if search_reply else "Search not used"}
    cache[safe_prompt] = result
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
            "battery": battery_status, "details": "JARVIS server is running"}

@app.post("/ask")
async def ask_jarvis(request: PromptRequest):
    return process_prompt(request.prompt, request.user)

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

import os
import sys
from fastapi import Request

@app.post("/shutdown")
async def shutdown(request: Request):
    # Announce shutdown in terminal
    print("JARVIS server shutting down...")

    # Optional: speak shutdown message
    try:
        tts.say("JARVIS server shutting down. Goodbye.")
        tts.runAndWait()
    except Exception:
        pass

    # Close DB connection cleanly
    try:
        conn.close()
    except:
        pass

    # Exit the process
    os._exit(0)  # force exit
# --- Shutdown Hook ---
def shutdown_message():
    print("JARVIS SHUTTING DOWN")
atexit.register(shutdown_message)

import subprocess

@app.on_event("startup")
async def launch_history_viewer():
    try:
        # Launch history viewer on port 8500
        subprocess.Popen(["uvicorn", "history_viewer:app", "--host", "127.0.0.1", "--port", "8500"])
        print("History Viewer started at http://127.0.0.1:8500")
    except Exception as e:
        print(f"Failed to start History Viewer: {e}")

