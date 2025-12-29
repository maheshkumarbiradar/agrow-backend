from ultralytics import YOLO
import cv2
import os
import time
import requests
from datetime import datetime

# ---------------- CONFIG ----------------
BOT_TOKEN = "8518386034:AAFPLoH-TnvlJuls7Qf2WGWPJxWfJeo4UtY"
CHAT_ID = "1517223648"

INTRUDERS = [
    "person", "cow", "dog", "cat",
    "horse", "sheep", "goat", "elephant"
]

CONFIDENCE_THRESHOLD = 0.5
ALERT_COOLDOWN = 20  # seconds
# ----------------------------------------

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

if not os.path.exists("captures"):
    os.makedirs("captures")

last_alert_time = 0

print("AGROW – Intrusion Detection (Telegram Auto Alert) Started...")

def send_telegram_alert(message, image_path):
    # Send text message
    text_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(text_url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

    # Send image
    photo_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as img:
        requests.post(photo_url, data={"chat_id": CHAT_ID}, files={"photo": img})

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    intrusion = False

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            confidence = float(box.conf[0])

            if label in INTRUDERS and confidence >= CONFIDENCE_THRESHOLD:
                intrusion = True

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    frame,
                    f"{label.upper()} ({confidence:.2f})",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

    if intrusion:
        now = time.time()
        if now - last_alert_time > ALERT_COOLDOWN:
            last_alert_time = now

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = f"captures/intrusion_{timestamp}.jpg"
            cv2.imwrite(img_path, frame)

            message = (
                "🚨 AGROW INTRUSION ALERT 🚨\n\n"
                "Human/Animal detected near your farm.\n"
                f"Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n"
                "Image captured."
            )

            send_telegram_alert(message, img_path)
            print("Telegram alert sent")

        cv2.putText(
            frame,
            "🚨 INTRUSION DETECTED 🚨",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 0, 255), 3
        )

    cv2.imshow("AGROW – Intrusion Detection (Telegram)", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
