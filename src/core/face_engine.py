import cv2
import numpy as np
import os
import requests
import time

class FaceEngine:
    # Model URLs
    YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/master/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
    SFACE_URL = "https://github.com/opencv/opencv_zoo/raw/master/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    
    def __init__(self):
        self.detector = None
        self.recognizer = None
        self._ensure_models_exist()
        self.initialize_models()
        
        # Liveness state
        self.liveness_state = "IDLE" # IDLE, CHALLENGE_LEFT, CHALLENGE_RIGHT, SUCCESS, FAILED
        self.liveness_start_time = 0
        self.liveness_threshold = 2.0 # Seconds to complete challenge

    def _ensure_models_exist(self):
        if not os.path.exists(self.MODELS_DIR):
            os.makedirs(self.MODELS_DIR)
        
        for name, url in [("face_detection_yunet_2023mar.onnx", self.YUNET_URL), 
                         ("face_recognition_sface_2021dec.onnx", self.SFACE_URL)]:
            path = os.path.join(self.MODELS_DIR, name)
            if not os.path.exists(path):
                print(f"📥 Descargando modelo: {name}...")
                response = requests.get(url, stream=True)
                with open(path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ {name} descargado.")

    def initialize_models(self):
        det_path = os.path.join(self.MODELS_DIR, "face_detection_yunet_2023mar.onnx")
        rec_path = os.path.join(self.MODELS_DIR, "face_recognition_sface_2021dec.onnx")
        
        self.detector = cv2.FaceDetectorYN.create(det_path, "", (320, 320), 0.9, 0.3, 5000)
        self.recognizer = cv2.FaceRecognizerSF.create(rec_path, "")

    def detect_face(self, frame):
        h, w, _ = frame.shape
        self.detector.setInputSize((w, h))
        _, faces = self.detector.detect(frame)
        return faces[0] if faces is not None and len(faces) > 0 else None

    def get_encoding(self, frame, face_data):
        aligned_face = self.recognizer.alignCrop(frame, face_data)
        return self.recognizer.feature(aligned_face)

    def compare_faces(self, known_encodings, target_encoding, threshold=0.363):
        if not known_encodings: return -1, 0
        
        best_score = -1.0
        best_idx = -1
        
        for i, known_enc in enumerate(known_encodings):
            score = self.recognizer.match(known_enc, target_encoding, cv2.FaceRecognizerSF_FR_COSINE)
            if score > best_score:
                best_score = score
                best_idx = i
                
        if best_score >= threshold:
            return best_idx, best_score
        return -1, best_score

    def check_liveness(self, face_data):
        """
        Simple head orientation check using landmarks.
        face_data format: [x, y, w, h, x_re, y_re, x_le, y_le, x_nt, y_nt, x_rm, y_rm, x_lm, y_lm, score]
        """
        if face_data is None: return False
        
        # Extract landmarks
        x_re, y_re = face_data[4:6]  # Right eye
        x_le, y_le = face_data[6:8]  # Left eye
        x_nt, y_nt = face_data[8:10] # Nose tip
        
        # Calculate eye distance and nose position relative to eyes
        eye_dist = abs(x_re - x_le)
        if eye_dist == 0: return False
        
        # Relative horizontal position of nose (0.5 is centered)
        # Looking RIGHT (from user perspective) makes nose closer to LEFT eye in camera frame (if not flipped)
        # In OpenCV frames, x increases to the right.
        # Ratio: (nose_x - left_eye_x) / (right_eye_x - left_eye_x)
        # However, YuNet labels re/le based on face, not frame.
        # Let's use absolute min/max to be safe.
        min_eye_x = min(x_re, x_le)
        max_eye_x = max(x_re, x_le)
        if max_eye_x == min_eye_x: return False
        
        ratio = (x_nt - min_eye_x) / (max_eye_x - min_eye_x)
        
        # Thresholds for "looking aside"
        if ratio < 0.35: orientation = "LEFT"
        elif ratio > 0.65: orientation = "RIGHT"
        else: orientation = "CENTER"
        
        return orientation

    @staticmethod
    def bytes_to_cv2(imagen_bytes):
        nparr = np.frombuffer(imagen_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    @staticmethod
    def crop_face(frame, face_data):
        x, y, w, h = map(int, face_data[:4])
        # Margin
        h_img, w_img, _ = frame.shape
        x, y = max(0, x), max(0, y)
        w, h = min(w, w_img - x), min(h, h_img - y)
        return frame[y:y+h, x:x+w]
