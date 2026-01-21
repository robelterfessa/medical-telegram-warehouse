import os
import csv
from pathlib import Path

from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "data" / "raw" / "images"
OUTPUT_CSV = BASE_DIR / "data" / "yolo_detections.csv"

model = YOLO("yolov8n.pt")  # YOLOv8 nano


def scan_images():
    rows = []

    for channel_dir in IMAGES_DIR.iterdir():
        if not channel_dir.is_dir():
            continue

        channel_name = channel_dir.name

        for img_path in channel_dir.glob("*.jpg"):
            message_id = img_path.stem  # filename without .jpg

            results = model.predict(source=str(img_path), verbose=False)
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = r.names[cls_id]
                    conf = float(box.conf[0])

                    rows.append(
                        {
                            "message_id": int(message_id),
                            "channel_name": channel_name,
                            "detected_class": cls_name,
                            "confidence_score": conf,
                        }
                    )

    return rows


def save_to_csv(rows):
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "message_id",
                "channel_name",
                "detected_class",
                "confidence_score",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    print("Running YOLO detection on images...")
    detections = scan_images()
    save_to_csv(detections)
    print(f"Saved {len(detections)} detections to {OUTPUT_CSV}")
