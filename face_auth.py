import cv2
import face_recognition
import pickle
import os
import sys
import time

DATA_FILE = "owner_face.pkl"

def authenticate_face():
    if not os.path.exists(DATA_FILE):
        print("[FATAL] Data wajah owner tidak ditemukan!")
        sys.exit(1)

    with open(DATA_FILE, "rb") as f:
        owner_encodings = pickle.load(f)  # ✅ LIST of encodings

    cap = cv2.VideoCapture(0)
    print("[INFO] Verifikasi wajah dimulai...")
    
    start_time = time.time()
    verified = False

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        for enc in encodings:
            matches = face_recognition.compare_faces(
                owner_encodings,
                enc,
                tolerance=0.5
            )

            if True in matches:
                verified = True
                break

        cv2.imshow("Face Authentication - Tekan Q", frame)

        if verified:
            print("[ACCESS GRANTED] Wajah valid.")
            break

        if time.time() - start_time > 12:
            print("[ACCESS DENIED] Wajah tidak dikenali.")
            break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not verified:
        sys.exit(1)
