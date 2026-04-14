import os
# Desactivar MSMF (Media Foundation) para evitar el error -2147483638 en Windows
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

import tkinter as tk
import customtkinter as ctk
import cv2
import threading
import time
import numpy as np
from PIL import Image, ImageTk
from src.core.face_engine import FaceEngine
from src.core.camera_manager import CameraManager
from src.database.usuario_dao import UsuarioDAO
from src.database.logs_dao import AccessLogDAO

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BioPass DAO - Security Suite")
        self.geometry("1100x700")
        
        # Engine & Data
        self.engine = FaceEngine()
        self.known_encodings = []
        self.known_names = []
        self.load_users()
        
        # State
        self.running = True
        self.current_frame = None
        self.lock = threading.Lock()
        
        # UI State
        self.active_view = "home"
        self.liveness_target = None # None, "LEFT", "RIGHT"
        self.liveness_success = False
        
        self.setup_layout()
        
        # Camera Discovery - Probing for working indices & backends
        self.cap = CameraManager.find_working_camera()
        
        # UI Throttle state
        self.frame_count = 0
        
        if self.cap:
            print("✅ Threaded Camera Initialized.")
        else:
            print("🛑 CRITICAL: No camera found.")
            # We'll handle visual feedback in create_home_view and update_gui
        
        self.update_gui()

    def load_users(self):
        users = UsuarioDAO.obtener_todos()
        self.known_encodings = []
        self.known_names = []
        for u in users:
            # u = (id, nombre, foto_cara)
            img_cv2 = cv2.imdecode(np.frombuffer(u[2], np.uint8), cv2.IMREAD_COLOR)
            if img_cv2 is not None:
                face_data = self.engine.detect_face(img_cv2)
                if face_data is not None:
                    enc = self.engine.get_encoding(img_cv2, face_data)
                    self.known_encodings.append(enc)
                    self.known_names.append(u[1])

    def setup_layout(self):
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        logo = ctk.CTkLabel(self.sidebar, text="BIOPASS", font=ctk.CTkFont(size=24, weight="bold"))
        logo.pack(pady=30)

        self.btn_home = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.show_view("home"))
        self.btn_home.pack(pady=10, padx=20)

        self.btn_users = ctk.CTkButton(self.sidebar, text="Usuarios", command=lambda: self.show_view("users"))
        self.btn_users.pack(pady=10, padx=20)

        self.btn_logs = ctk.CTkButton(self.sidebar, text="Historial", command=lambda: self.show_view("logs"))
        self.btn_logs.pack(pady=10, padx=20)

        # Content Area
        self.container = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.show_view("home")

    def show_view(self, view_name):
        for widget in self.container.winfo_children():
            widget.destroy()
        
        if view_name == "home": self.create_home_view()
        elif view_name == "users": self.create_users_view()
        elif view_name == "logs": self.create_logs_view()

    def create_home_view(self):
        title = ctk.CTkLabel(self.container, text="Control de Acceso Biométrico", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=(0, 20))

        # Camera Frame
        self.cam_label = ctk.CTkLabel(self.container, text="", width=640, height=480, fg_color="black", corner_radius=10)
        self.cam_label.pack()

        # Input and Buttons
        controls = ctk.CTkFrame(self.container, fg_color="transparent")
        controls.pack(pady=20, fill="x")

        self.entry_name = ctk.CTkEntry(controls, placeholder_text="Nombre para registro...", width=250)
        self.entry_name.pack(side="left", padx=10)

        btn_reg = ctk.CTkButton(controls, text="Registrar", fg_color="green", hover_color="#006400", command=self.handle_register)
        btn_reg.pack(side="left", padx=10)

        btn_login = ctk.CTkButton(controls, text="Iniciar Reconocimiento", command=self.start_liveness_challenge)
        btn_login.pack(side="right", padx=10)

        self.status_label = ctk.CTkLabel(self.container, text="Sistema Listo", font=ctk.CTkFont(size=14))
        self.status_label.pack()

    def create_users_view(self):
        title = ctk.CTkLabel(self.container, text="Gestión de Usuarios", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=(0, 20))

        self.scroll_users = ctk.CTkScrollableFrame(self.container, width=800, height=500)
        self.scroll_users.pack(fill="both", expand=True)
        self.refresh_users_list()

    def refresh_users_list(self):
        for widget in self.scroll_users.winfo_children():
            widget.destroy()
        
        users = UsuarioDAO.obtener_todos()
        for u in users:
            row = ctk.CTkFrame(self.scroll_users, fg_color=("gray90", "gray15"))
            row.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(row, text=f"ID: {u[0]}", width=50).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=u[1], font=ctk.CTkFont(weight="bold"), width=200).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=u[3] if len(u)>3 else "N/A", width=150).pack(side="left", padx=10)
            
            btn_del = ctk.CTkButton(row, text="Eliminar", fg_color="#8B0000", hover_color="#550000", width=80, 
                                     command=lambda uid=u[0]: self.delete_user(uid))
            btn_del.pack(side="right", padx=10)

    def delete_user(self, uid):
        if UsuarioDAO.eliminar_usuario(uid):
            self.load_users()
            self.refresh_users_list()

    def create_logs_view(self):
        title = ctk.CTkLabel(self.container, text="Historial de Accesos", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=(0, 20))
        
        logs_frame = ctk.CTkScrollableFrame(self.container, width=800, height=500)
        logs_frame.pack(fill="both", expand=True)
        
        logs = AccessLogDAO.obtener_logs()
        for l in logs:
            color = "green" if l[2] == "SUCCESS" else "red"
            row = ctk.CTkFrame(logs_frame, fg_color=("gray90", "gray15"))
            row.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(row, text=l[3], width=180).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=l[1], width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            status_lbl = ctk.CTkLabel(row, text=l[2], width=120, text_color=color)
            status_lbl.pack(side="right", padx=10)

    def update_gui(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.current_frame = frame
                self.frame_count += 1
                
                # Optimized display processing: resize FIRST if frame is too big
                # (although CameraManager now sets 640x480)
                h, w = frame.shape[:2]
                if w > 640:
                    display_frame = cv2.resize(frame, (640, 480))
                else:
                    display_frame = frame.copy()

                # Process for display
                display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                
                # Liveness Overlay
                if hasattr(self, 'cam_label') and self.cam_label.winfo_exists():
                    if self.liveness_target:
                        cv2.putText(display_frame, f"RETO: MIRA A LA {self.liveness_target}", (40, 40), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                        
                        # THROTTLE: Only detect face every 3rd frame to save CPU
                        if self.frame_count % 3 == 0:
                            face_data = self.engine.detect_face(frame)
                            if face_data is not None:
                                curr_orient = self.engine.check_liveness(face_data)
                                if curr_orient == self.liveness_target:
                                    self.liveness_success = True
                                    self.liveness_target = None
                                    self.after(0, self.finish_login, face_data, frame)

                    img_pil = Image.fromarray(display_frame)
                    ctk_photo = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(640, 480))
                    self.cam_label.configure(image=ctk_photo)
                    self.cam_label.image = ctk_photo 
            else:
                # No frame available yet or read failed
                if not hasattr(self, '_last_fail_time') or time.time() - self._last_fail_time > 2:
                    if hasattr(self, 'cam_label') and self.cam_label.winfo_exists():
                         self.cam_label.configure(text="⌛ Esperando señal de cámara...", text_color="orange")
                    self._last_fail_time = time.time()
        else:
            if hasattr(self, 'cam_label') and self.cam_label.winfo_exists():
                self.cam_label.configure(text="⚠️ CÁMARA NO DETECTADA\nRevise conexión o drivers.", text_color="red")

        if self.running:
            # Throttle UI update to ~30 FPS (33ms) instead of 15ms
            self.after(33, self.update_gui)

    def start_liveness_challenge(self):
        import random
        self.liveness_target = random.choice(["LEFT", "RIGHT"])
        self.liveness_success = False
        self.status_label.configure(text=f"🔄 Reto: Gira la cabeza a la {self.liveness_target}", text_color="yellow")

    def finish_login(self, face_data, frame):
        encoding = self.engine.get_encoding(frame, face_data)
        idx, score = self.engine.compare_faces(self.known_encodings, encoding)
        
        if idx != -1:
            name = self.known_names[idx]
            self.status_label.configure(text=f"✅ Bienvenido, {name}!", text_color="green")
            AccessLogDAO.registrar_acceso(name, "SUCCESS")
        else:
            self.status_label.configure(text="❌ Acceso Denegado: Desconocido", text_color="red")
            AccessLogDAO.registrar_acceso("Desconocido", "DENIED")

    def handle_register(self):
        name = self.entry_name.get().strip()
        if not name:
            self.status_label.configure(text="⚠️ Error: Ingrese un nombre", text_color="orange")
            return

        with self.lock:
            if self.current_frame is None: return
            frame = self.current_frame.copy()
        
        face_data = self.engine.detect_face(frame)
        if face_data is not None:
            face_img = self.engine.crop_face(frame, face_data)
            success, buffer = cv2.imencode(".jpg", face_img)
            if success:
                if UsuarioDAO.registrar_usuario(name, buffer.tobytes()):
                    self.load_users()
                    self.status_label.configure(text=f"✅ Usuario {name} registrado!", text_color="green")
                    self.entry_name.delete(0, tk.END)
                else:
                    self.status_label.configure(text="❌ Error en BD", text_color="red")
        else:
            self.status_label.configure(text="❌ No se detectó rostro", text_color="red")

if __name__ == "__main__":
    app = AppUI()
    app.mainloop()
