# Programmed by Arafat Waleed (modified)
# Developed: add gesture-to-open-website + cooldown + gesture hold detection
import cv2
import mediapipe as mp
import math as m
import mouse
import time
import webbrowser

cap = cv2.VideoCapture(0)

# state for clicks & movement
lclicked = False
rclicked = False
sensitivity = 3
smoothTime = 0.25
moveDir = [0,0]
deadzone = 1
prev_x, prev_y = None, None
fx, fy = None, None
smoothed_x, smoothed_y = 0,0

# screen size (tune to your screen)
screen_w, screen_h = 1920,1080

# cooldowns to avoid repeating actions too fast (seconds)
ACTION_COOLDOWN = 3.0
last_action_time = {
    "open_youtube": 0,
    "open_google": 0,
    "open_github": 0
}

# gesture hold detection
gesture_start_time = None
current_gesture = None
HOLD_TIME = 2.0  # seconds to hold gesture

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands = 1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def lerp(a, b, t):
    return a + (b - a) * t

def is_cooldown_over(action_name):
    return (time.time() - last_action_time.get(action_name, 0)) >= ACTION_COOLDOWN

def trigger_action(action_name, url=None):
    """Trigger action with cooldown; if url provided, open it in default browser."""
    if not is_cooldown_over(action_name):
        return False
    last_action_time[action_name] = time.time()
    if url:
        try:
            webbrowser.open(url, new=2)  # new=2 -> open in new tab if possible
        except Exception as e:
            print("Failed to open URL:", e)
    return True

def fingers_up(hand_landmarks, img_w, img_h):
    """
    Return list of booleans for [thumb, index, middle, ring, pinky] whether each finger is 'up' (extended).
    Heuristic:
      - For index/middle/ring/pinky: tip.y < pip.y  (remember: y=0 at top)
      - For thumb: compare tip.x and ip.x (because of horizontal orientation and flip)
    """
    lm = hand_landmarks.landmark
    tips_ids = [4, 8, 12, 16, 20]
    pip_ids = [3, 6, 10, 14, 18]  # approximate PIP / lower joint indices
    status = []
    for tip, pip in zip(tips_ids, pip_ids):
        tip_x = lm[tip].x * img_w
        tip_y = lm[tip].y * img_h
        pip_x = lm[pip].x * img_w
        pip_y = lm[pip].y * img_h
        if tip == 4:  # thumb heuristic
            status.append(abs(tip_x - pip_x) > 15 and ((tip_x - pip_x) < 0))  # tweak sign if needed
        else:
            status.append(tip_y < pip_y - 5)  # small offset to avoid noise
    return status  # [thumb, index, middle, ring, pinky]

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, c = frame.shape
    results = hands.process(rgb)
    action_text = ""

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            # draw skeleton
            for connection in mp_hands.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                x1, y1 = int(hand_landmarks.landmark[start_idx].x * w), int(hand_landmarks.landmark[start_idx].y * h)
                x2, y2 = int(hand_landmarks.landmark[end_idx].x * w), int(hand_landmarks.landmark[end_idx].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
            for hand_landmark in hand_landmarks.landmark:
                cx, cy = int(hand_landmark.x * w),int(hand_landmark.y*h)
                cv2.circle(frame,(cx,cy),1,(255,255,255),2)

            # landmarks
            control = hand_landmarks.landmark[0]
            index = hand_landmarks.landmark[8]
            thumb = hand_landmarks.landmark[4]
            middle = hand_landmarks.landmark[12]

            control_x = int(control.x * w)
            control_y = int(control.y * h)
            thumb_x = int(thumb.x * w)
            thumb_y = int(thumb.y * h)
            middle_x = int(middle.x * w)
            middle_y = int(middle.y * h)
            index_x = int(index.x * w)
            index_y = int(index.y * h)

            cursor_x = int(control.x* screen_w)
            cursor_y = int(control.y* screen_h)

            # distances for click
            cv2.line(frame, (middle_x,middle_y), (thumb_x,thumb_y),(0,255,255),2)
            cv2.line(frame, (index_x,index_y), (thumb_x,thumb_y),(0,255,255),2)
            thumbMiddleDistance = m.dist((thumb_x,thumb_y), (middle_x,middle_y))
            leftDistance = m.dist((thumb_x,thumb_y), (index_x,index_y))

            cv2.putText(frame,str(round(thumbMiddleDistance,2)),(int((thumb_x + control_x)/2) + 20,int((thumb_y + control_y) / 2)),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)

            # click logic
            clickThreshold = 25
            if leftDistance <= clickThreshold:
                if not lclicked:
                    mouse.press("left")
                    lclicked = True
            else:
                if lclicked:
                    mouse.release("left")
                    lclicked = False

            if thumbMiddleDistance <= clickThreshold:
                if not rclicked:
                    mouse.press("right")
                    rclicked = True
            else:
                if rclicked:
                    mouse.release("right")
                    rclicked = False

            # movement smoothing + relative move
            smoothed_x, smoothed_y = lerp(smoothed_x,cursor_x,smoothTime),lerp(smoothed_y,cursor_y,smoothTime)
            if prev_x is not None and prev_y is not None:
                dx = (smoothed_x - prev_x) * sensitivity
                dy = (smoothed_y - prev_y) * sensitivity
                if fx is not None and fy is not None:
                    dxx = (smoothed_x - fx)
                    dyy = (smoothed_y - fy)
                    mag = m.sqrt(pow(abs(dxx),2) + pow(abs(dyy),2))
                    if mag > deadzone:
                        moveDir = [dx,dy]
                    mouse.move(int(moveDir[0]), int(moveDir[1]), absolute=False)
                    moveDir = [0,0]
            prev_x, prev_y = smoothed_x, smoothed_y
            fx, fy = smoothed_x, smoothed_y

            # --- NEW: gesture detection ---
            up = fingers_up(hand_landmarks, w, h)
            thumb_up, index_up, middle_up, ring_up, pinky_up = up

            new_gesture = None
            if index_up and middle_up and not ring_up and not pinky_up and not thumb_up:
                new_gesture = "youtube"

        
            elif index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
                new_gesture = "google"
            elif thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
                new_gesture = "github"
    
            if new_gesture != current_gesture:
                current_gesture = new_gesture
                gesture_start_time = time.time()
            else:
                if current_gesture and (time.time() - gesture_start_time) >= HOLD_TIME:
                    if current_gesture == "youtube":
                        if trigger_action("open_youtube", "https://www.youtube.com"):
                            action_text = "Opened YouTube"
                    elif current_gesture == "google":
                        if trigger_action("open_google", "https://www.google.com"):
                            action_text = "Opened Google"
                    elif current_gesture == "github":
                        if trigger_action("open_github", "https://github.com"):
                            action_text = "Opened GitHub"
                    # reset after action
                    current_gesture = None
                    gesture_start_time = None

            # draw finger status
            status_str = f"T:{int(thumb_up)} I:{int(index_up)} M:{int(middle_up)} R:{int(ring_up)} P:{int(pinky_up)}"
            cv2.putText(frame, status_str, (10, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,0), 2)

    if action_text:
        cv2.putText(frame, action_text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,200,0), 2)

    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
