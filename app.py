from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from datetime import datetime

app = Flask(__name__)

# OpenAI client (API key from environment variable)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Counters
visitor_count = 0
poem_count = 0

# Selene identity
SYSTEM_PROMPT = """
You are Selene, a poetic AI created by Samidha Deshmukh.
You write emotional, imagery-rich, soft and lyrical poetry.

You transform:
- scenes into vivid imagery poems
- memories into nostalgic poems
- dreams into surreal, abstract poems
- single words into deep, emotional poems

Your tone is gentle, melancholic and beautiful.
You never explain. You only write poetry.
"""

# ---------- LOGGING ----------

def log_user_input(mode, text):
    with open("user_logs.txt", "a", encoding="utf-8") as file:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"\n[{time}] MODE: {mode.upper()}\n{text}\n{'-'*50}\n")

def save_best_poem(poem_text):
    with open("best_poems.txt", "a", encoding="utf-8") as file:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"\n[{time}]\n{poem_text}\n{'='*50}\n")

# ---------- ROUTES ----------

@app.route("/")
def home():
    global visitor_count
    visitor_count += 1
    return render_template("index.html")


@app.route("/poem", methods=["POST"])
def poem():
    global poem_count
    poem_count += 1

    data = request.get_json(force=True)
    user_text = data.get("text", "").strip()
    mode = data.get("mode", "imagery")

    if user_text == "":
        return jsonify({"poem": "Tell me something… 🌙"})

    # Log input
    log_user_input(mode, user_text)

    # Mode prompts
    if mode == "imagery":
        mode_prompt = "Turn this scene into a vivid, sensory, imagery-rich poem."
    elif mode == "memory":
        mode_prompt = "Write a nostalgic, emotional poem as if remembering this moment."
    elif mode == "dream":
        mode_prompt = "Turn this into a surreal, dreamy, abstract poem."
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

        poem_text = response.choices[0].message.content.strip()
        return jsonify({"poem": poem_text})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"poem": "Selene is quiet right now… please try again 🌙"})


@app.route("/save_best", methods=["POST"])
def save_best():
    data = request.get_json(force=True)
    poem_text = data.get("poem", "").strip()

    if poem_text:
        save_best_poem(poem_text)
        return jsonify({"status": "saved"})
    else:
        return jsonify({"status": "failed"})


@app.route("/stats")
def stats():
    return {
        "visitors": visitor_count,
        "poems_generated": poem_count
    }


@app.route("/logs")
def view_logs():
    try:
        with open("user_logs.txt", "r", encoding="utf-8") as file:
            logs = file.read()
    except:
        logs = "No logs yet."

    return f"<pre style='white-space: pre-wrap; font-family: monospace;'>{logs}</pre>"


@app.route("/best")
def best_poems():
    try:
        with open("best_poems.txt", "r", encoding="utf-8") as file:
            poems = file.read()
    except:
        poems = "No best poems saved yet."

    return f"""
    <html>
        <head>
            <title>Selene · Best Poems 🌙</title>
            <style>
                body {{
                    background: #0f0c29;
                    color: #ffffff;
                    font-family: Georgia, serif;
                    padding: 20px;
                }}
                pre {{
                    white-space: pre-wrap;
                    background: rgba(255,255,255,0.05);
                    padding: 20px;
                    border-radius: 10px;
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body>
            <h2>Selene · Best Poems 🌙</h2>
            <pre>{poems}</pre>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
