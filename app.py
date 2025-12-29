from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import requests
import os
import time

# -------------------------
# App setup
# -------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("AGROW – YOLO + Telegram Backend Started")

# -------------------------
# Load YOLO
# -------------------------
model = YOLO("yolov8n.pt")
CONF_THRESHOLD = 0.35
DETECT_CLASSES = ["person", "dog", "cat", "cow", "horse", "sheep"]

# -------------------------
# Telegram config
# -------------------------
BOT_TOKEN = "8518386034:AAFPLoH-TnvlJuls7Qf2WGWPJxWfJeo4UtY"
CHAT_ID = "1517223648"

last_alert_time = 0
ALERT_COOLDOWN = 30  # seconds

# -------------------------
# Health check
# -------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "backend working"})

# -------------------------
# Send Telegram alert
# -------------------------
def send_telegram_alert(image, label, conf):
    try:
        _, img_encoded = cv2.imencode(".jpg", image)
        files = {
            "photo": ("intrusion.jpg", img_encoded.tobytes())
        }
        data = {
            "chat_id": CHAT_ID,
            "caption": f"🚨 AGROW ALERT\n\nIntrusion Detected\nObject: {label}\nConfidence: {conf}"
        }
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        requests.post(url, files=files, data=data, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# -------------------------
# Detection route
# -------------------------
@app.route("/detect/frame", methods=["POST"])
def detect_frame():
    global last_alert_time

    if "frame" not in request.files:
        return jsonify({"status": "No Frame", "object": "—", "confidence": "—"})

    # Decode image
    file = request.files["frame"]
    img_bytes = file.read()
    np_img = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"status": "Invalid Image", "object": "—", "confidence": "—"})

    img = cv2.resize(img, (640, 640))

    # YOLO detection
    results = model(img, verbose=False)

    detected_object = None
    detected_conf = 0

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])

            if label in DETECT_CLASSES and conf >= CONF_THRESHOLD:
                detected_object = label
                detected_conf = round(conf, 2)
                break

    if detected_object:
        now = time.time()
        if now - last_alert_time > ALERT_COOLDOWN:
            last_alert_time = now
            send_telegram_alert(img, detected_object, detected_conf)

        return jsonify({
            "status": "Intrusion Detected",
            "object": detected_object,
            "confidence": detected_conf
        })

    return jsonify({
        "status": "No Intrusion",
        "object": "—",
        "confidence": "—"
    })

# -------------------------
# Run (Render compatible)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



