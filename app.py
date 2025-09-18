from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from dotenv import load_dotenv
# โหลดค่า .env ตอนรันในเครื่อง (Render จะไม่เห็นไฟล์นี้ แต่ไม่ error)
load_dotenv()

# กำหนด API Key จาก Environment Variable
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__, template_folder="templates", static_folder="static")

# --- SYMPTOMS (เก็บไว้เผื่อใช้งานในอนาคต) ---
SYMPTOMS = [
    "ไข้","ไอ","เจ็บคอ","น้ำมูกไหล","ปวดศีรษะ","เวียนศีรษะ","คลื่นไส้","อ่อนเพลีย","หายใจลำบาก",
    "ปวดท้อง","ผื่น","คัน","หนาวสั่น","ถ่ายเหลว","เจ็บหน้าอก","ปวดกล้ามเนื้อ","เหนื่อยง่าย",
    "ท้องเสีย","คลื่นไส้อาเจียน","ง่วงนอน","ใจสั่น","บวม","แดง","ระคายเคือง","จุกเสียดหน้าอก",
    "เวียนหัว","ไวต่อแสง","ปวดท้องมาก","ตาพร่ามัว","ไม่สบายตัว"
]
print(">>> SYMPTOMS loaded:", len(SYMPTOMS))

# ----------------- ROUTES -----------------
@app.get("/")
def home():
    return render_template("index.html")

@app.get("/aibot")
def aibot():
    return render_template("aibot.html")

@app.get("/health")
def health():
    # ใช้โหมดพิมพ์อิสระเป็นหลัก
    return render_template("health.html")
    # ถ้าจะใช้ชิปอาการ:
    # return render_template("health.html", symptoms=SYMPTOMS)

@app.get("/follow")
def follow():
    return render_template("follow.html")

@app.get("/testresults")
def testresults():
    return render_template("testresults.html")

@app.get("/login")
def login():
    return render_template("login.html")

@app.get("/signup")
def signup():
    return render_template("signup.html")


# ----------------- API: Chat Bot (หน้า aibot) -----------------
@app.post("/api/chat")
def chat():
    user_msg = (request.json or {}).get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "message is required"}), 400

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        res = client.responses.create(
            model="gpt-4o-mini",
            input=f"ตอบเป็นภาษาไทยกระชับ: {user_msg}"
        )
        return jsonify({"response": res.output_text})
    except Exception as e:
        return jsonify({"response": f"เกิดข้อผิดพลาด: {e}"}), 200


# ----------------- Helper -----------------
def _to_int(v):
    try:
        return int(v) if v not in (None, "",) else None
    except Exception:
        return None

def _to_float(v):
    try:
        return float(v) if v not in (None, "",) else None
    except Exception:
        return None

def _calc_bmi(height_cm, weight_kg):
    """คำนวณ BMI (ถ้าให้มาไม่ครบจะคืน None)"""
    h = _to_float(height_cm)
    w = _to_float(weight_kg)
    if not h or not w:
        return None
    h_m = h / 100.0
    if h_m <= 0:
        return None
    try:
        return round(w / (h_m * h_m), 1)
    except Exception:
        return None


# ----------------- API: Health Analyze (health/follow) -----------------
@app.post("/api/health/analyze")
def analyze_health():
    """
    รองรับ 2 โหมดพร้อมกัน (ไม่ตีกัน):
    - โหมดเก่า: free_text, systolic/diastolic/heart_rate/symptoms/extra_notes
    - โหมดใหม่: gender/height_cm/weight_kg/sleep_hours/alcohol/smoking/
                 systolic/diastolic/heart_rate/blood_sugar/temperature_c/bmi/symptoms
    """
    data = request.get_json(force=True) or {}

    # ---------- โหมดถามอิสระ (ของเดิม) ----------
    free_text = (data.get("free_text") or "").strip()
    if free_text:
        system_prompt = (
            "คุณเป็นผู้ช่วยด้านสุขภาพ (ไม่ใช่แพทย์). "
            "ให้คำแนะนำเชิงปฏิบัติอย่างระมัดระวัง, อย่าวินิจฉัยโรคแทนแพทย์, "
            "เตือนให้พบแพทย์หากมีสัญญาณอันตราย. ตอบภาษาไทย กระชับ อ่านง่าย."
        )
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            res = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": free_text}
                ],
            )
            return jsonify({"analysis": res.output_text, "flags": []})
        except Exception as e:
            return jsonify({"analysis": "ไม่สามารถเรียกใช้ AI ได้: " + str(e), "flags": []})

    # ---------- รับค่าจากทั้งโครงสร้างเก่า/ใหม่ ----------
    # เก่า
    sys_g = data.get("systolic")
    dia_g = data.get("diastolic")
    hr_g  = data.get("heart_rate")
    symptoms_g = data.get("symptoms", []) or []
    extra_notes = (data.get("extra_notes") or "").strip()

    # ใหม่ (อาจส่งมาหรือไม่ก็ได้)
    gender       = data.get("gender")
    height_cm    = data.get("height_cm")
    weight_kg    = data.get("weight_kg")
    sleep_hours  = data.get("sleep_hours")
    alcohol      = data.get("alcohol")
    smoking      = data.get("smoking")
    systolic     = data.get("systolic", sys_g)
    diastolic    = data.get("diastolic", dia_g)
    heart_rate   = data.get("heart_rate", hr_g)
    blood_sugar  = data.get("blood_sugar")
    temperature  = data.get("temperature_c")
    bmi          = data.get("bmi")  # ถ้าไม่มีจะคำนวณให้ด้านล่าง
    symptoms     = data.get("symptoms") or symptoms_g

    # ---------- แปลง type และคำนวณ BMI ----------
    systolic  = _to_int(systolic)
    diastolic = _to_int(diastolic)
    heart_rate = _to_int(heart_rate)
    blood_sugar = _to_float(blood_sugar)
    temperature = _to_float(temperature)
    sleep_hours = _to_float(sleep_hours)

    if not bmi:
        bmi = _calc_bmi(height_cm, weight_kg)

    # ---------- Rule-based flags ----------
    flags = []
    try:
        if temperature is not None and temperature >= 38.0:
            flags.append("ไข้สูง (≥38°C)")
        if heart_rate is not None and (heart_rate > 100 or heart_rate < 50):
            flags.append("ชีพจรผิดปกติ")
        if (systolic and systolic >= 140) or (diastolic and diastolic >= 90):
            flags.append("ความดันสูง (≥140/90)")
        if (systolic and systolic < 90) or (diastolic and diastolic < 60):
            flags.append("ความดันต่ำ (<90/60)")
        if blood_sugar is not None and blood_sugar >= 180:
            flags.append("น้ำตาลสูง (≥180 mg/dL)")
        if bmi is not None and bmi >= 30:
            flags.append("BMI อ้วนระดับ 2 (≥30)")
        # ตัวอย่าง rule เดิม
        if "เจ็บหน้าอก" in symptoms and ("หายใจลำบาก" in symptoms or "ใจสั่น" in symptoms):
            flags.append("อาการเสี่ยงหัวใจ/ปอด ควรพบแพทย์ทันที")
    except Exception:
        pass

    # ---------- รวมข้อความส่งให้ AI ----------
    # บันทึกข้อมูลครบทุกฟิลด์ (ถ้าว่างจะระบุว่าไม่ระบุ)
    info_lines = [
        f"เพศ: {gender or 'ไม่ระบุ'}",
        f"ส่วนสูง: {height_cm or '-'} ซม., น้ำหนัก: {weight_kg or '-'} กก., BMI: {bmi if bmi is not None else '-'}",
        f"การนอน: {sleep_hours if sleep_hours is not None else '-'} ชม./คืน",
        f"ดื่มแอลกอฮอล์: {alcohol or 'ไม่ระบุ'} | สูบบุหรี่/ยาสูบ: {smoking or 'ไม่ระบุ'}",
        f"ความดันโลหิต: {systolic if systolic is not None else '-'} / {diastolic if diastolic is not None else '-'} mmHg",
        f"ชีพจร: {heart_rate if heart_rate is not None else '-'} ครั้ง/นาที",
        f"น้ำตาลในเลือด: {blood_sugar if blood_sugar is not None else '-'} mg/dL",
        f"อุณหภูมิร่างกาย: {temperature if temperature is not None else '-'} °C",
        "อาการที่พบ: " + (", ".join(symptoms) if symptoms else "ไม่ระบุ"),
    ]
    if extra_notes:
        info_lines.append("อาการเพิ่มเติม/บันทึก: " + extra_notes)

    if flags:
        info_lines.append("ธงเตือนเบื้องต้น: " + ", ".join(flags))

    info_text = "\n".join(info_lines)

    system_prompt = (
        "คุณเป็นผู้ช่วยด้านสุขภาพ (ไม่ใช่แพทย์). "
        "ให้คุณ: 1) สรุปข้อมูลจากฟอร์ม (อ้างทุกฟิลด์ที่มี), "
        "2) วิเคราะห์ความเป็นไปได้/ปัจจัยเสี่ยงโดยรวม (รวม BMI, BP, HR, น้ำตาล, อุณหภูมิ, การนอน, พฤติกรรมดื่ม/สูบ), "
        "3) ให้คำแนะนำเชิงปฏิบัติเป็นข้อ ๆ, "
        "4) ระบุสัญญาณอันตรายที่ควรไปพบแพทย์ทันที. "
        "อย่าวินิจฉัยโรคแบบฟันธง. ตอบเป็นภาษาไทย อ่านง่าย เป็นหัวข้อ."
    )
    user_prompt = f"ข้อมูลผู้ใช้:\n{info_text}"

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        res = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
        )
        analysis = res.output_text
    except Exception as e:
        analysis = "ไม่สามารถเรียกใช้ AI ได้: " + str(e)

    return jsonify({"flags": flags, "analysis": analysis})


# ----------------- RUN -----------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
