from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2, time
from intrusion_telegram_alert import send_telegram_alert

app = Flask(__name__)
CORS(app)

model = YOLO("yolov8n.pt")

INTRUDERS = ["person","cow","dog","cat","horse","sheep","goat"]
CONF_THRESHOLD = 0.5
ALERT_COOLDOWN = 10
last_alert_time = 0

@app.route("/detect/frame", methods=["POST"])
def detect_frame():
    global last_alert_time

    print("📸 Frame received")

    file = request.files["frame"]
    path = "frame.jpg"
    file.save(path)

    img = cv2.imread(path)
    results = model(img)

    intrusion = False
    detected_object = None
    confidence = None

    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls[0])]
            conf = float(box.conf[0])

            if label in INTRUDERS and conf >= CONF_THRESHOLD:
                intrusion = True
                detected_object = label
                confidence = round(conf, 2)

    if intrusion and time.time() - last_alert_time > ALERT_COOLDOWN:
        last_alert_time = time.time()
        send_telegram_alert("🚨 AGROW LIVE INTRUSION DETECTED", path)

    return jsonify({
        "status": "Intrusion Detected" if intrusion else "No Intrusion",
        "object": detected_object,
        "confidence": confidence
    })

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

