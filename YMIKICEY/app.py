from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    if "history" not in session:
        session["history"] = [
            {"role": "system", "content": "You are YMIKICEY, a playful, funny, savage-but-chill AI friend who can also generate images if asked. Avoid NSFW or illegal content."}
        ]
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    user_msg = request.form["message"]
    mode = request.form.get("mode", "chat")

    session["history"].append({"role": "user", "content": user_msg})

    bot_reply = ""
    try:
        if mode == "image":
            img = client.images.generate(
                model="gpt-image-1",
                prompt=user_msg,
                size="1024x1024"
            )
            bot_reply = f'<img src="{img.data[0].url}" alt="Generated Image"/>'
            session["history"].append({"role": "assistant", "content": "[Image Generated]"})
        else:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=session["history"],
                max_tokens=200
            )
            bot_reply = response.choices[0].message.content
            session["history"].append({"role": "assistant", "content": bot_reply})

    except Exception as e:
        bot_reply = f"Error: {str(e)}"

    session.modified = True
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
