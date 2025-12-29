from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import os
import time

# -------------------------
# App setup
# -------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

print("AGROW – YOLO Intrusion Detection Backend Started")

# -------------------------
# Load YOLO model (FASTEST)
# -------------------------
model = YOLO("yolov8n.pt")   # nano model (best for Render)

CONF_THRESHOLD = 0.5
DETECT_CLASSES = ["person", "dog", "cat", "cow", "horse", "sheep"]

last_alert_time = 0
ALERT_COOLDOWN = 10   # seconds

# -------------------------
# Health check
# -------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "backend working"})


# -------------------------
# Detection route
# -------------------------
@app.route("/detect/frame", methods=["POST"])
def detect_frame():
    global last_alert_time

    try:
        if "frame" not in request.files:
            return jsonify({
                "status": "No Frame Received",
                "object": "—",
                "confidence": "—"
            })

        # Read image from request
        file = request.files["frame"]
        img_bytes = file.read()
        np_img = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({
                "status": "Invalid Image",
                "object": "—",
                "confidence": "—"
            })

        # Resize for speed
        img = cv2.resize(img, (640, 640))

        # YOLO inference
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

        # If intrusion detected
        if detected_object:
            current_time = time.time()

            if current_time - last_alert_time > ALERT_COOLDOWN:
                last_alert_time = current_time
                print(f"🚨 Intrusion detected: {detected_object} ({detected_conf})")

            return jsonify({
                "status": "Intrusion Detected",
                "object": detected_object,
                "confidence": detected_conf
            })

        # No intrusion
        return jsonify({
            "status": "No Intrusion",
            "object": "—",
            "confidence": "—"
        })

    except Exception as e:
        print("Detection error:", e)
        return jsonify({
            "status": "Error",
            "object": "—",
            "confidence": "—"
        }), 500


# -------------------------
# Run app (Render compatible)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
