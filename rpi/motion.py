#!/usr/bin/env python3
"""
Low‑quality motion‑activated video recorder for Raspberry Pi Camera.

Features
--------
* Camera runs at 5 fps, 320 × 240 (tiny bandwidth & CPU)
* Simple frame‑difference motion detector
* When motion exceeds a threshold, records a 10‑second clip
* Continuous loop – after each clip the script goes back to monitoring
"""

import time
import numpy as np
import cv2
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder

# ----------------------------------------------------------------------
# Configuration – tweak these values to suit your environment
# ----------------------------------------------------------------------
RESOLUTION      = (320, 240)   # Small window (width, height)
FRAMERATE       = 5            # Low fps → low quality / low CPU
MOTION_THRESH   = 250000   # Pixel‑difference sum that counts as motion
RECORD_SECONDS  = 10           # Length of the saved video
OUTPUT_PREFIX   = "motion_"    # Files will be motion_001.mp4, motion_002.mp4, …
# ----------------------------------------------------------------------


def diff_score(frame_a: np.ndarray, frame_b: np.ndarray) -> int:
    """
    Compute a cheap “how much changed?” metric.
    We convert to grayscale, take absolute difference,
    then sum all pixel values.
    """
    gray_a = cv2.cvtColor(frame_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(frame_b, cv2.COLOR_BGR2GRAY)
    diff   = cv2.absdiff(gray_a, gray_b)
    return int(np.sum(diff))


def main():
    # Initialise the camera
    cam = Picamera2()
    low_video_cfg = cam.create_video_configuration(
        main={"size": RESOLUTION},
        controls={"FrameRate": FRAMERATE}
    )
    cam.configure(low_video_cfg)
    record_video_cfg = cam.create_video_configuration()
    encoder = H264Encoder(bitrate=1000000)

    # Optional preview (requires a connected monitor)
    # cam.start_preview(Preview.QTGL)

    cam.start()
    print("Camera started – waiting for motion...")

    # Grab the first frame to seed the motion detector
    last_frame = cam.capture_array()
    frame_counter = 0

    while True:
        # Grab next frame (non‑blocking)
        cur_frame = cam.capture_array()
        score = diff_score(last_frame, cur_frame)

        if score > MOTION_THRESH:
            # Motion detected – start a short recording
            frame_counter += 1
            out_name = f"{OUTPUT_PREFIX}{frame_counter:03d}.h264"
            print(f"\n⚡ Motion detected! (score={score}) → Recording {out_name}...")
            cam.stop()
            cam.configure(record_video_cfg)
            cam.start_recording(encoder, out_name)
            time.sleep(RECORD_SECONDS)
            # start = time.time()

            # while time.time() - start < RECORD_SECONDS:
            #     # Keep feeding the camera so the encoder stays alive
            #     cam.capture_array()   # discard frames while recording
            #     time.sleep(0.01)      # tiny sleep to avoid busy‑loop
            cam.stop_recording()
            cam.configure(low_video_cfg)
            print("✅ Recording finished.\nReturning to motion watch…")
            cam.start() 
            # Reset baseline after a motion event – helps avoid immediate retriggers
            last_frame = cam.capture_array()
            continue

        # No motion – keep the latest frame as baseline
        last_frame = cur_frame

        # Sleep just enough to respect the target fps (avoid hogging CPU)
        time.sleep(1.0 / FRAMERATE)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exiting – goodbye!")