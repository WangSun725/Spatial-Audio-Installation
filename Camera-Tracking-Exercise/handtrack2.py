
import cv2
import mediapipe as mp
from pythonosc.udp_client import SimpleUDPClient


OSC_IP   = "127.0.0.1"
OSC_PORT = 9011
OSC_ADDR_AZ = "/StereoEncoder/azimuth"
OSC_ADDR_EL = "/StereoEncoder/elevation"


POINT_ID = 8


mp_hands = mp.solutions.hands
osc = SimpleUDPClient(OSC_IP, OSC_PORT)

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

with mp_hands.Hands(
    model_complexity=0,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = hands.process(rgb)

            if res.multi_hand_landmarks:
                lm = res.multi_hand_landmarks[0].landmark[POINT_ID]


                x_px = int(lm.x * w);  x_px = clamp(x_px, 0, w - 1)
                y_px = int(lm.y * h);  y_px = clamp(y_px, 0, h - 1)


                x_c = x_px - cx
                y_c = cy - y_px


                half_w, half_h = w / 2.0, h / 2.0
                az = clamp((x_c / half_w) * 180.0, -180.0, 180.0)   # -180..+180
                el = clamp((y_c / half_h) * 180.0,  -180.0,   180.0)   #  -90..+90


                osc.send_message(OSC_ADDR_AZ, float(az))
                osc.send_message(OSC_ADDR_EL, float(el))


                cv2.circle(frame, (x_px, y_px), 6, (255, 255, 255), -1)
                cv2.putText(frame, f"center=({x_c},{y_c})  az={az:.1f}  el={el:.1f}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            cv2.imshow("IEM StereoEncoder OSC Control", frame)
            if cv2.waitKey(1) & 0xFF in (27, ord('q')):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
