from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from datetime import datetime

app = Flask(__name__)

# OpenAI client using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Counters
visitor_count = 0
poem_count = 0

# Selene's identity & behavior
SYSTEM_PROMPT = """
You are Selene, a poetic AI created by Samidha Deshmukh.
You specialize in emotional, imagery-rich poetry.

You transform:
- scenes into vivid imagery poems
- memories into nostalgic poems
- dreams into surreal, abstract poems
- single words into deep, lyrical poems

You use:
- visual imagery (light, color, shadows, atmosphere)
- emotional depth
- soft, lyrical language
- metaphors and beauty

Your tone is gentle, melancholic, and poetic.
You never explain. You only write poetry.
"""

# ---------------- LOGGING FUNCTION ---------------- #

def log_user_input(mode, text):
    with open("user_logs.txt", "a", encoding="utf-8") as file:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"\n[{time}] MODE: {mode.upper()}\n{text}\n{'-'*50}\n")

# ---------------- ROUTES ---------------- #

# Home route (counts visitors)
@app.route("/")
def home():
    global visitor_count
    visitor_count += 1
    return render_template("index.html")

# Poem generation route
@app.route("/poem", methods=["POST"])
def poem():
    global poem_count
    poem_count += 1

    data = request.get_json()
    user_text = data.get("text", "")
    mode = data.get("mode", "imagery")

    # Log user input
    log_user_input(mode, user_text)

    # Mode-based prompt
    if mode == "imagery":
        mode_prompt = "Transform this scene into a vivid, sensory, imagery-rich poem."
    elif mode == "memory":
        mode_prompt = "Write a nostalgic, emotional poem as if remembering this moment."
    elif mode == "dream":
        mode_prompt = "Turn this into a surreal, dreamy, abstract poem with soft transitions."
    elif mode == "single":
        mode_prompt = "Expand this single word into a deep, emotional, lyrical poem."
    else:
        mode_prompt = "Write a beautiful poem based on this."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mode_prompt},
                {"role": "user", "content": user_text}
            ],
            max_tokens=300,
            temperature=0.9
        )

        poem_text = response.choices[0].message.content
        return jsonify({"poem": poem_text})

    except Exception as e:
        return jsonify({"poem": "Selene is quiet right now… please try again 🌙"})

# Private stats route (only for you)
@app.route("/stats")
def stats():
    return {
        "visitors": visitor_count,
        "poems_generated": poem_count
    }

# Private logs route (only for you)
@app.route("/logs")
def view_logs():
    try:
        with open("user_logs.txt", "r", encoding="utf-8") as file:
            logs = file.read()
    except:
        logs = "No logs yet."

    return f"""
    <html>
        <head>
            <title>Selene Logs 🌙</title>
            <style>
                body {{
                    background: #0f0c29;
                    color: #ffffff;
                    font-family: monospace;
                    padding: 20px;
                }}
                pre {{
                    white-space: pre-wrap;
                    background: rgba(255,255,255,0.05);
                    padding: 15px;
                    border-radius: 10px;
                }}
            </style>
        </head>
        <body>
            <h2>Selene · User Logs 🌙</h2>
            <pre>{logs}</pre>
        </body>
    </html>
    """

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
