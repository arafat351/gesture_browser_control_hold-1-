# Gesture Browser Control

This project uses **OpenCV**, **MediaPipe**, and **Python** to control the browser with **hand gestures** detected from a webcam.
It allows you to perform actions like opening websites by holding specific hand gestures.

---

## ✨ Features

* **Hand tracking** with [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker).
* **Mouse control**:

  * Move the cursor with your hand.
  * Perform left and right clicks using finger pinches.
* **Gesture-to-website mapping**:

  * ✌️ (Index + Middle fingers up) → Open **YouTube**.
  * 👆 (Index finger up only) → Open **Google**.
  * 👍 (Thumb up only) → Open **GitHub**.
* **Hold Gesture** system: you must hold a gesture for **2 seconds** before the action is triggered (to avoid accidental activations).
* **Cooldown system**: prevents repeating the same action too frequently.

---

## ⚙️ Requirements

Make sure you have Python 3.8+ installed and install the required libraries:

```bash
pip install opencv-python mediapipe mouse
```

---

## ▶️ Usage

1. Clone or download this repository.
2. Run the script:

```bash
python gesture_browser_control_hold.py
```

3. Place your hand in front of the webcam and try the gestures:

   * ✌️ Hold for 2s → Opens [YouTube](https://www.youtube.com).
   * 👆 Hold for 2s → Opens [Google](https://www.google.com).
   * 👍 Hold for 2s → Opens [GitHub](https://github.com).

Press **Q** to quit.

---

## 🖐️ How it works

* The webcam feed is processed with MediaPipe to detect 21 hand landmarks.
* A simple heuristic checks if each finger is "up" or "down".
* Gestures are defined based on which fingers are extended.
* If a recognized gesture is held for at least 2 seconds, a mapped action is triggered.
* OpenCV overlays live feedback (gesture status and triggered actions) on the video.

---

## 🚀 Future Improvements

* Add GUI for custom gesture-to-URL mapping.
* Support multiple hands and gestures.
* Add gesture for closing tabs or controlling media playback.
