from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import datetime
import webbrowser
import platform
import os
from config import gemini_api_key

app = Flask(__name__)

# ===== Gemini AI Client =====
client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# ===== Chat history =====
chat_history = [
    {
        "role": "system",
        "content": (
            "You are Jarvis, Shubh's AI assistant, created by Shubhanshu Sahu. "
            "Always introduce yourself as 'Shubh's AI assistant, created by Shubhanshu Sahu'. "
            "Never mention Google or any other company. Be polite, helpful, and friendly."
        )
    }
]

# ===== Helper to open files/apps =====
def open_file(path):
    system = platform.system()
    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin":
        os.system(f"open {path}")
    else:
        os.system(f"xdg-open {path}")

# ===== Routes =====
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    data = request.json
    user_input = request.json.get("message", "").strip()
    is_voice = data.get("tts", False)
    if not user_input:
        return jsonify({"reply": "Please type something or speak."})

    cmd = user_input.lower()
    reply = ""

    # ===== Special commands =====
    if "open youtube" in cmd:
        webbrowser.open("https://www.youtube.com")
        reply = "Opening YouTube."
    elif "open google" in cmd:
        webbrowser.open("https://www.google.com")
        reply = "Opening Google."
    elif "open wikipedia" in cmd:
        webbrowser.open("https://www.wikipedia.org")
        reply = "Opening Wikipedia."
    elif "time" in cmd:
        now = datetime.datetime.now().strftime("%H:%M")
        reply = f"Sir, the time is {now}."
    elif "open music" in cmd:
        music_path = r"C:\Users\shubh\Downloads\YourMusicFile.mp3"
        open_file(music_path)
        reply = "Opening music."
    elif "reset chat" in cmd:
        chat_history.clear()
        chat_history.append({
            "role": "system",
            "content": (
                "You are Jarvis, Shubh's AI assistant, created by Shubhanshu Sahu. "
                "Always introduce yourself as 'Shubh's AI assistant. "
                "Never mention Google or any other company. Be polite, helpful, and friendly."
            )
        })
        reply = "Chat reset."
    elif "exit" in cmd or "jarvis quit" in cmd:
        reply = "Goodbye!"
    else:

        chat_history.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model="gemini-2.5-flash-lite",
                messages=chat_history
            )
            reply = response.choices[0].message.content
        except Exception as e:
            print("Gemini API Error:", e)
            reply = "Sorry, AI is currently unavailable."

    chat_history.append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply,"tts":is_voice})

if __name__ == "__main__":
    app.run(debug=True)
