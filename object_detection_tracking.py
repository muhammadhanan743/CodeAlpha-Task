"""
CodeAlpha Task 4: Object Detection and Tracking
Uses YOLOv8 (ultralytics) + ByteTrack/built-in tracker for real-time tracking.

Install:
    pip install ultralytics opencv-python

Run:
    python object_detection_tracking.py                    # webcam
    python object_detection_tracking.py --source video.mp4  # video file
    python object_detection_tracking.py --source image.jpg  # single image
"""

import argparse
import sys
import time
import random
from pathlib import Path
from collections import defaultdict

try:
    import cv2
    CV2_OK = True
except ImportError:
    CV2_OK = False
    print("❌ OpenCV not found. Run: pip install opencv-python")

try:
    from ultralytics import YOLO
    YOLO_OK = True
except ImportError:
    YOLO_OK = False
    print("❌ ultralytics not found. Run: pip install ultralytics")


# ── Constants ──────────────────────────────────────────────────────────────────
MODEL_NAME   = "yolov8n.pt"     # nano model (fast); change to yolov8s/m/l for better accuracy
CONF_THRESH  = 0.40             # minimum confidence to show a detection
IOU_THRESH   = 0.45             # NMS IoU threshold
IMG_SIZE     = 640
TRACK_HIST   = 30               # frames to keep trail history per track ID

# UI styling
FONT         = cv2.FONT_HERSHEY_SIMPLEX if CV2_OK else None
FONT_SCALE   = 0.55
THICKNESS    = 2
ALPHA        = 0.35             # overlay transparency

# Colour palette (BGR) – one per track ID (deterministic via hash)
PALETTE = [
    (255, 56,  56),  (255, 157, 151), (255, 112, 31),
    (255, 178, 29),  (207, 210,  49), (72,  249, 10),
    (146, 204, 23),  (61,  219, 134), (26,  147, 52),
    (0,   212, 187), (44,  153, 168), (0,   194, 255),
    (52,  69,  147), (100, 115, 255), (0,   24,  236),
    (132, 56,  255), (82,  0,   133), (203, 56,  255),
    (255, 149, 200), (255, 55,  199),
]


def track_color(track_id: int):
    return PALETTE[int(track_id) % len(PALETTE)]


def draw_box(frame, x1, y1, x2, y2, label: str, color, track_id=None):
    """Draw a rounded-corner bounding box with label badge."""
    # Semi-transparent fill
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, ALPHA, frame, 1 - ALPHA, 0, frame)

    # Border
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, THICKNESS)

    # Label badge
    (tw, th), _ = cv2.getTextSize(label, FONT, FONT_SCALE, 1)
    badge_y2 = y1
    badge_y1 = max(0, y1 - th - 10)
    cv2.rectangle(frame, (x1, badge_y1), (x1 + tw + 10, badge_y2), color, -1)
    cv2.putText(frame, label,
                (x1 + 5, badge_y2 - 4),
                FONT, FONT_SCALE, (255, 255, 255), 1, cv2.LINE_AA)


def draw_trail(frame, history: list, color):
    """Draw motion trail for a tracked object."""
    for i in range(1, len(history)):
        if history[i - 1] is None or history[i] is None:
            continue
        thickness = max(1, int(THICKNESS * i / len(history)))
        cv2.line(frame, history[i - 1], history[i], color, thickness, cv2.LINE_AA)


def draw_hud(frame, frame_count: int, fps: float, n_tracks: int):
    """Draw heads-up display overlay."""
    h, w = frame.shape[:2]
    hud_lines = [
        f"CodeAlpha Task 4 — Object Detection & Tracking",
        f"Model: YOLOv8n  |  Conf: {CONF_THRESH}  |  FPS: {fps:.1f}",
        f"Frame: {frame_count}  |  Active tracks: {n_tracks}",
        "Press Q to quit  |  S to save screenshot",
    ]
    y = 22
    for line in hud_lines:
        (tw, th), _ = cv2.getTextSize(line, FONT, 0.48, 1)
        cv2.rectangle(frame, (8, y - th - 4), (8 + tw + 6, y + 4),
                      (20, 20, 20), -1)
        cv2.putText(frame, line, (11, y), FONT, 0.48,
                    (200, 230, 255), 1, cv2.LINE_AA)
        y += th + 10


def run_detection(source, save_output: bool = False):
    if not CV2_OK or not YOLO_OK:
        print("Missing dependencies. See errors above.")
        return

    # Load model (downloads automatically on first run)
    print(f"[*] Loading {MODEL_NAME} …")
    model = YOLO(MODEL_NAME)
    print(f"[✓] Model loaded. Classes: {len(model.names)}")

    # Open source
    is_image = False
    if isinstance(source, str) and Path(source).suffix.lower() in (
            ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"):
        is_image = True
        frame_orig = cv2.imread(source)
        if frame_orig is None:
            print(f"❌ Cannot open image: {source}")
            return
        cap = None
    else:
        cap = cv2.VideoCapture(0 if source == "0" else source)
        if not cap.isOpened():
            print(f"❌ Cannot open source: {source}")
            return

    # Video writer
    writer = None
    if save_output and not is_image:
        out_path = "output_tracked.mp4"
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps_cap = cap.get(cv2.CAP_PROP_FPS) or 30
        writer = cv2.VideoWriter(out_path,
                                 cv2.VideoWriter_fourcc(*"mp4v"),
                                 fps_cap, (w, h))
        print(f"[✓] Saving output to {out_path}")

    # Tracking state
    track_history = defaultdict(list)   # track_id → list of (cx, cy) centroids
    frame_count = 0
    fps = 0.0
    fps_timer = time.time()
    screenshot_count = 0

    print("[*] Starting detection & tracking. Press Q to quit, S to screenshot.")

    # ── Image mode ─────────────────────────────────────────────────────────────
    if is_image:
        results = model(frame_orig, conf=CONF_THRESH, iou=IOU_THRESH,
                        imgsz=IMG_SIZE, verbose=False)
        frame = frame_orig.copy()
        boxes = results[0].boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf  = float(box.conf[0])
                cls   = int(box.cls[0])
                name  = model.names[cls]
                label = f"{name} {conf:.0%}"
                color = PALETTE[cls % len(PALETTE)]
                draw_box(frame, x1, y1, x2, y2, label, color)

        cv2.putText(frame,
                    f"CodeAlpha Task 4 — {len(boxes) if boxes else 0} objects detected",
                    (10, 28), FONT, 0.65, (0, 230, 100), 2, cv2.LINE_AA)
        out_img = "output_detected.jpg"
        cv2.imwrite(out_img, frame)
        print(f"[✓] Saved: {out_img}")
        cv2.imshow("CodeAlpha — Object Detection", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # ── Video / webcam mode ────────────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[*] Stream ended.")
            break

        frame_count += 1

        # FPS calculation
        if frame_count % 15 == 0:
            elapsed = time.time() - fps_timer
            fps = 15 / max(elapsed, 1e-6)
            fps_timer = time.time()

        # Run YOLOv8 tracking (ByteTrack built-in)
        results = model.track(frame,
                              conf=CONF_THRESH,
                              iou=IOU_THRESH,
                              imgsz=IMG_SIZE,
                              tracker="bytetrack.yaml",
                              persist=True,
                              verbose=False)

        active_ids = set()

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes  = results[0].boxes.xyxy.cpu().numpy()
            ids    = results[0].boxes.id.cpu().numpy().astype(int)
            confs  = results[0].boxes.conf.cpu().numpy()
            clses  = results[0].boxes.cls.cpu().numpy().astype(int)

            for box, tid, conf, cls in zip(boxes, ids, confs, clses):
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                name   = model.names[cls]
                label  = f"#{tid} {name} {conf:.0%}"
                color  = track_color(tid)

                # Update trail
                history = track_history[tid]
                history.append((cx, cy))
                if len(history) > TRACK_HIST:
                    history.pop(0)

                draw_trail(frame, history, color)
                draw_box(frame, x1, y1, x2, y2, label, color, tid)
                active_ids.add(tid)

        # Prune stale track histories
        for tid in list(track_history.keys()):
            if tid not in active_ids:
                del track_history[tid]

        draw_hud(frame, frame_count, fps, len(active_ids))

        if writer:
            writer.write(frame)

        cv2.imshow("CodeAlpha — Object Detection & Tracking", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("[*] Quit by user.")
            break
        elif key == ord("s"):
            screenshot_count += 1
            fname = f"screenshot_{screenshot_count:03d}.jpg"
            cv2.imwrite(fname, frame)
            print(f"[✓] Screenshot saved: {fname}")

    cap.release()
    if writer:
        writer.release()
        print(f"[✓] Output video saved.")
    cv2.destroyAllWindows()
    print(f"[*] Processed {frame_count} frames total.")


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="CodeAlpha Task 4 — Real-time Object Detection & Tracking")
    parser.add_argument("--source", type=str, default="0",
                        help="0=webcam, path to video file, or path to image")
    parser.add_argument("--save", action="store_true",
                        help="Save output video to output_tracked.mp4")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  CodeAlpha AI Internship — Task 4")
    print("  Object Detection & Tracking (YOLOv8 + ByteTrack)")
    print("="*60 + "\n")

    run_detection(args.source, save_output=args.save)


if __name__ == "__main__":
    main()
