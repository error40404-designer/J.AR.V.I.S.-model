import requests, pyttsx3, speech_recognition as sr, atexit, time, sys

SERVER_URL = "http://127.0.0.1:8000/ask"
SERVER_HOME = "http://127.0.0.1:8000/"

# Initialize TTS
tts = pyttsx3.init()

def speak(text: str):
    try:
        tts.say(text)
        tts.runAndWait()
    except Exception as e:
        print(f"TTS Error: {e}")

# Startup voice
speak("Initiating JARVIS client...")

# Try connecting to server
def check_server():
    try:
        r = requests.get(SERVER_HOME)
        if r.status_code == 200:
            speak("Connected to JARVIS server backend.")
            return True
    except Exception:
        speak("Unable to connect to server. Retrying...")
        return False

while not check_server():
    time.sleep(2)

recognizer = sr.Recognizer()

def ask(prompt: str):
    try:
        r = requests.post(SERVER_URL, json={"prompt": prompt, "user": "Guest"})
        data = r.json()
        reply = data["ai_reply"]
        print(f"JARVIS: {reply}")
        speak(reply)
    except Exception as e:
        print(f"Error contacting server: {e}")
        speak("Error contacting server.")

def voice_loop():
    while True:
        with sr.Microphone() as source:
            print("Listening.......")
            audio = recognizer.listen(source)
        try:
            prompt = recognizer.recognize_google(audio)
            print(f"You said: {prompt}")

            # Shutdown trigger
            if "system shutdown" in prompt.lower():
                speak("JARVIS shutting down. Goodbye.")
                # Optional: call server shutdown endpoint if implemented
                try:
                    requests.post("http://127.0.0.1:8000/shutdown")
                except:
                    pass
                sys.exit(0)

            ask(prompt)
        except Exception as e:
            print(f"Error: {e}")
            speak("I couldn't understand that.")
    
    if "system shutdown" in prompt.lower():
     speak("JARVIS shutting down. Goodbye.")
    try:
        requests.post("http://127.0.0.1:8000/shutdown")  # call server shutdown
    except:
        pass
    sys.exit(0)

# Shutdown hook
def shutdown_message():
    speak("JARVIS shutting down. Goodbye.")
atexit.register(shutdown_message)

if __name__ == "__main__":
    voice_loop()
