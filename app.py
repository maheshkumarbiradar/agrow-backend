from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# -------------------------
# App setup
# -------------------------
app = Flask(__name__)

# 🔥 CORS FIX (MOST IMPORTANT LINE)
CORS(app, resources={r"/*": {"origins": "*"}})

print("AGROW – Intrusion Detection Backend Started")

# -------------------------
# Health check route
# -------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "backend working"})


# -------------------------
# Detection route
# -------------------------
@app.route("/detect/frame", methods=["POST"])
def detect_frame():
    try:
        # Check if frame exists
        if "frame" not in request.files:
            return jsonify({
                "status": "No Frame Received",
                "object": "—",
                "confidence": "—"
            }), 200

        frame = request.files["frame"]

        # 🔴 TEMP LOGIC (YOLO CAN BE ADDED LATER)
        # This confirms frontend ↔ backend works

        return jsonify({
            "status": "Intrusion Detected",
            "object": "person",
            "confidence": 0.99
        }), 200

    except Exception as e:
        print("Error:", e)
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
