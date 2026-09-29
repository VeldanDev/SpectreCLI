import cv2
import face_recognition
import pickle
import os
import time

DATA_FILE = "owner_face.pkl"
MAX_SAMPLES = 10   # jumlah encoding yang dikumpulkan

def register_face():
    print("[INFO] Membuka kamera untuk registrasi wajah...")
    print("[INFO] Hadapkan wajah, sedikit gerakkan kepala (kiri/kanan), tekan Q jika cukup")
    cap = cv2.VideoCapture(0)

    encodings = []
    last_capture = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Kamera gagal dibuka")
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        face_encs = face_recognition.face_encodings(rgb, boxes)

        # Tangkap wajah max 1 per jeda waktu
        if boxes and len(encodings) < MAX_SAMPLES:
            now = time.time()
            if now - last_capture > 0.6:  # jeda supaya encoding tidak identik
                encodings.append(face_encs[0])
                last_capture = now
                print(f"[INFO] Capture sample {len(encodings)}/{MAX_SAMPLES}")

        # Overlay status
        cv2.putText(
            frame,
            f"Samples: {len(encodings)}/{MAX_SAMPLES}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("Face Registration - Tekan Q untuk simpan", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if len(encodings) >= MAX_SAMPLES:
            break

    cap.release()
    cv2.destroyAllWindows()

    if encodings:
        with open(DATA_FILE, "wb") as f:
            pickle.dump(encodings, f)
        print(f"[SUCCESS] {len(encodings)} data wajah berhasil diregistrasi!")
    else:
        print("[FAIL] Tidak ada wajah yang tersimpan!")

if __name__ == "__main__":
    register_face()
