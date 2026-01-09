from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

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

if __name__ == "__main__":
    app.run(debug=True)
