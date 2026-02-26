

import requests, pyttsx3, speech_recognition as sr

SERVER_URL = "http://127.0.0.1:8000/ask"

# Voice announcement on client startup
tts = pyttsx3.init()
tts.say("JARVIS online: HELLO")
tts.runAndWait()

recognizer = sr.Recognizer()

def ask(prompt: str):
    r = requests.post(SERVER_URL, json={"prompt": prompt})
    data = r.json()
    reply = data["ai_reply"]
    print(f"JARVIS: {reply}")
    tts.say(reply)
    tts.runAndWait()

def voice_loop():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        prompt = recognizer.recognize_google(audio)
        print(f"You said: {prompt}")
        ask(prompt)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    voice_loop()