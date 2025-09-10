from flask import Flask, render_template, request, jsonify
from pathlib import Path
import os

# กำหนดพาธแบบปลอดภัย
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)

@app.route("/")
def index():
    # DEBUG: พิมพ์รายชื่อไฟล์ใน templates ช่วยเช็คว่ามี Main/aibot.html จริง
    try:
        print("Template root:", TEMPLATES_DIR)
        print("Templates:", [str(p.relative_to(TEMPLATES_DIR)) for p in TEMPLATES_DIR.rglob("*.html")])
    except Exception as e:
        print("List templates error:", e)

    # ✅ ชี้ไปยังไฟล์ในโฟลเดอร์ Main
    return render_template("Main/aibot.html")

# เผื่ออยากเข้าตรง
@app.route("/Main/aibot")
def aibot_page():
    return render_template("Main/aibot.html")

# ตัวอย่าง API (ถ้าใช้ fetch('/api') แบบ POST)
@app.route("/api", methods=["POST"])
def api():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"response": "Message cannot be empty."}), 400
    # ตอบกลับทดสอบ
    return jsonify({"response": f"รับแล้ว: {msg}"}), 200

if __name__ == "__main__":
    # รันจากโฟลเดอร์โปรเจกต์ที่มี app.py
    print("🚀 http://127.0.0.1:5000  (ลอง / และ /Main/aibot)")
    app.run(debug=True)
