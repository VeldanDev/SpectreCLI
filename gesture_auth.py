import cv2
import mediapipe as mp
import time
import sys

# === KONFIGURASI ===
SECRET_GESTURE = [3, 1, 4]
TIME_LIMIT = 15

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
draw = mp.solutions.drawing_utils


def count_fingers(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # ibu jari (horizontal)
    fingers.append(
        hand_landmarks.landmark[tips[0]].x >
        hand_landmarks.landmark[tips[0] - 1].x
    )

    for i in range(1, 5):
        fingers.append(
            hand_landmarks.landmark[tips[i]].y <
            hand_landmarks.landmark[tips[i] - 2].y
        )

    return fingers.count(True)


def authenticate_gesture():
    cap = cv2.VideoCapture(0)
    detected = []

    start_time = time.time()
    last_value = None
    stable_since = None
    STABLE_TIME = 0.8  # detik harus stabil

    print("[INFO] Verifikasi gestur tangan dimulai...")
    print(f"[TARGET] Urutan angka: {SECRET_GESTURE}")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
                fingers = count_fingers(hand)

                cv2.putText(
                    frame, f"Detected: {fingers}",
                    (40, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (0, 255, 0), 3
                )

                now = time.time()

                if fingers == last_value:
                    if stable_since and (now - stable_since >= STABLE_TIME):
                        if not detected or detected[-1] != fingers:
                            detected.append(fingers)
                            print("[LOCKED]", detected)
                            stable_since = None
                else:
                    last_value = fingers
                    stable_since = now

        cv2.imshow("Gesture Authentication - Hold Numbers", frame)

        if detected == SECRET_GESTURE:
            print("[ACCESS GRANTED] Gestur valid.")
            cap.release()
            cv2.destroyAllWindows()
            return True

        if time.time() - start_time > TIME_LIMIT:
            print("[ACCESS DENIED] Waktu habis.")
            break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    sys.exit(1)
