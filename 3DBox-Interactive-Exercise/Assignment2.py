import cv2
import mediapipe as mp
from pythonosc.udp_client import SimpleUDPClient

# OSC setup — change ip/port to match your Pure Data netreceive.
ip = "127.0.0.1"
port = 9000
client = SimpleUDPClient(ip, port)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Open webcam 
cap = cv2.VideoCapture(0)

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Mirror for natural interaction
        frame = cv2.flip(frame, 1)

        # Convert to RGB 
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        h, w, _ = frame.shape  # image dimensions

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Convert landmarks to pixel coordinates
                x_coords = [int(lm.x * w) for lm in hand_landmarks.landmark]
                y_coords = [int(lm.y * h) for lm in hand_landmarks.landmark]

                # Bounding box
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)

                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cx, cy = int((x_min + x_max) / 2), int((y_min + y_max) / 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                # Normalized values
                x_center = cx / w
                y_center = cy / h
                box_width = (x_max - x_min) / w
                box_height = (y_max - y_min) / h

                # Send OSC: [x_center, y_center, width, height]
                client.send_message("/hand/pos", 
                                    [float(x_center), float(y_center), 
                                     float(box_width), float(box_height)])

                print(f"Hand -> x: {x_center:.3f}, y: {y_center:.3f}, "
                      f"w: {box_width:.3f}, h: {box_height:.3f}")

        cv2.imshow("Hand Tracking (center + size -> OSC)", frame)
        if cv2.waitKey(1) & 0xFF in [27, ord('q')]:  # ESC or q to quit
            print("Quitting...")
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
