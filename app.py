from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from dotenv import load_dotenv
import os

# โหลด .env
load_dotenv()

app = Flask(__name__, template_folder="templates")

# สร้าง client (อ่านคีย์จาก ENV ตามปกติ)
client = OpenAI()  # อย่าลืมตั้ง OPENAI_API_KEY ใน .env

@app.route("/")
def index():
    # เสิร์ฟ templates/aibot.html
    return render_template("Main/aibot.html")

@app.route("/aibot")
def aibot_alias():
    return render_template("aibot.html")

# รับเฉพาะ POST เพื่อหลีกเลี่ยงปัญหา get_json()==None
@app.route("/api", methods=["POST"])
def chat_api():
    # ตรวจ API key
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({"response": "API key not configured."}), 500

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"response": "Message cannot be empty."}), 400

    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": user_message}],
            temperature=0.7,
            max_tokens=300,
        )
        ai_text = resp.choices[0].message.content
        return jsonify({"response": ai_text})
    except Exception as e:
        # ล็อกแล้วส่งข้อความสั้น ๆ กลับไป
        print(f"OpenAI API error: {e}")
        return jsonify({"response": "OpenAI API error. Please try again."}), 502

if __name__ == "__main__":
    print("🚀 Starting Flask app on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
