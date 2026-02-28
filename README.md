# JARVIS Helmet HUD Assistant

## Overview
This project is a futuristic AI assistant inspired by Iron Man’s JARVIS. It integrates conversational AI, system control, and a sci‑fi styled web interface. The backbone (`ai.py`) runs on FastAPI with Groq API for natural replies, Hugging Face for fallback, DuckDuckGo for factual search, and Wikipedia for explanations. A SQLite database stores history, while THOOVARA client bridges the web UI and backbone, streaming system telemetry.

The web interface (`jarvis.html`) is designed as a helmet HUD, showing CPU, memory, battery, server status, and time. It includes a terminal‑style command console, voice input/output, and a glowing orb representing JARVIS. Commands like “open YouTube” or “open Spotify” are executed directly. Replies are spoken aloud via TTS.

This project is **still underway** and was coded with guidance from **Microsoft Copilot**. Version 3 currently available. released on 27-2-26

---

## Features
- Conversational AI via Groq API (Mixtral model).
- Fallback Hugging Face model for replies.
- Wikipedia integration for “explain” and “what” prompts.
- DuckDuckGo search for factual queries.
- System control: open Edge, YouTube, Spotify, Netflix, CMD, Explorer, VS Code.
- SQLite history logging.
- THOOVARA client as middle‑man between web UI and backbone.
- Futuristic HUD web interface with live system telemetry.
- Voice input/output integration.
- Countinuos chat
- Voice response
- Enhanced privacy

---

## Installation
```bash
git clone https://github.com/yourusername/jarvis-hud.git
cd jarvis-hud
pip install -r requirements.txt
