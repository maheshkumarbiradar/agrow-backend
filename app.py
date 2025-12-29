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
    return jsonify({
        "status": "Intrusion Detected",
        "object": "person",
        "confidence": 0.99
    })


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


