import cv2
import pytesseract
import imutils
import numpy as np
import argparse
import os
import pandas as pd
from datetime import timedelta

# If Tesseract not in PATH, uncomment and set path:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    return gray, edged

def find_plate_contour(edged):
    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:40]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            return approx
    return None

def extract_plate(image, plate_cnt):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [plate_cnt], -1, 255, -1)
    x, y, w, h = cv2.boundingRect(plate_cnt)
    plate_img = image[y:y+h, x:x+w]
    return plate_img, (x, y, w, h)

def ocr_plate(plate_img):
    if plate_img is None or plate_img.size == 0:
        return ""
    plate_gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    plate_gray = cv2.resize(plate_gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, plate_thresh = cv2.threshold(plate_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    plate_thresh = cv2.morphologyEx(plate_thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
    text = pytesseract.image_to_string(plate_thresh, config=custom_config)
    text = text.strip()
    text = "".join(ch for ch in text if ch.isalnum() or ch == '-')
    return text

def process_video(video_path, out_csv="detections.csv", skip_frames=5, debug=False, min_confidence_count=2):
    if not os.path.exists(video_path):
        raise FileNotFoundError("Video not found: " + video_path)

    cap = cv2.VideoCapture('sample.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    detections = []  # list of dicts
    last_text = None
    text_counter = {}  # track same-text consecutive counts to reduce false positives

    frame_idx = 0
    printed = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        if frame_idx % skip_frames != 0:
            continue

        # resize for speed
        frame = imutils.resize(frame, width=900)
        gray, edged = preprocess(frame)
        plate_cnt = find_plate_contour(edged)

        detected_text = ""
        bbox = None
        if plate_cnt is not None:
            plate_img, bbox = extract_plate(frame, plate_cnt)
            detected_text = ocr_plate(plate_img)

        # fallback: scanning rectangular contours by area/aspect ratio if no quad found
        if not detected_text and plate_cnt is None:
            cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            best = None
            best_score = 0
            for c in cnts:
                x,y,w,h = cv2.boundingRect(c)
                ar = w / float(h) if h>0 else 0
                area = cv2.contourArea(c)
                if 200 < area < 50000 and 2.0 < ar < 6.0:
                    if area > best_score:
                        best_score = area
                        best = (x,y,w,h)
            if best:
                x,y,w,h = best
                plate_img = frame[y:y+h, x:x+w]
                detected_text = ocr_plate(plate_img)
                bbox = (x,y,w,h)

        # simple stabilization: only accept a text after it appears min_confidence_count times
        if detected_text:
            count = text_counter.get(detected_text, 0) + 1
            text_counter[detected_text] = count
            # decay other counters to avoid memory growth
            for k in list(text_counter.keys()):
                if k != detected_text:
                    text_counter[k] = max(0, text_counter[k] - 1)
        else:
            # decay all counters
            for k in list(text_counter.keys()):
                text_counter[k] = max(0, text_counter[k] - 1)

        # if a text has reached the confidence threshold and wasn't logged recently, log it
        for text, cnt in list(text_counter.items()):
            if cnt >= min_confidence_count and text:
                # avoid logging duplicates many times: check last_text
                if text != last_text:
                    time_sec = frame_idx / fps
                    detections.append({
                        "frame": frame_idx,
                        "time_seconds": round(time_sec, 3),
                        "text": text
                    })
                    print(f"[{str(timedelta(seconds=int(time_sec)))}] Frame {frame_idx}: {text}")
                    last_text = text
                # reduce counter so we don't repeatedly log the same text multiple times
                text_counter[text] = 0

        if debug and bbox is not None and detected_text:
            x,y,w,h = bbox
            disp = frame.copy()
            cv2.rectangle(disp, (x,y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(disp, detected_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)
            cv2.imshow("Debug", disp)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if debug:
        cv2.destroyAllWindows()

    # save CSV
    if detections:
        df = pd.DataFrame(detections)
        df.to_csv(out_csv, index=False)
        print(f"\nSaved {len(detections)} detections to {out_csv}")
    else:
        print("\nNo detections found.")

    return detections

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Read license plates from a recorded video file.")
    p.add_argument("--video", "-v", required=True, help="Path to input video file")
    p.add_argument("--out", "-o", default="detections.csv", help="Output CSV file")
    p.add_argument("--skip", "-s", type=int, default=5, help="Process every Nth frame (default 5)")
    p.add_argument("--debug", "-d", action="store_true", help="Show debug overlay windows")
    p.add_argument("--mincount", type=int, default=2, help="Number of repeated frames required to accept a detection (default 2)")
    args = p.parse_args()

    process_video(args.video, out_csv=args.out, skip_frames=args.skip, debug=args.debug, min_confidence_count=args.mincount)
