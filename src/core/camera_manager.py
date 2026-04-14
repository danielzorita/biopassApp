import cv2
import time
import threading

class ThreadedCamera:
    """
    Dedicated class to read frames in a background thread to prevent UI blocking.
    """
    def __init__(self, index, backend):
        self.cap = cv2.VideoCapture(index + backend)
        
        # Standardize for stability and speed
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # Force MJPG to avoid rainbow distortion on some Windows drivers
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        self.ret = False
        self.frame = None
        self.running = True
        
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                with self.lock:
                    self.ret = ret
                    self.frame = frame
            else:
                time.sleep(0.1)
            time.sleep(0.01) # Small sleep to prevent CPU saturation

    def read(self):
        with self.lock:
            # Return a copy to avoid race conditions if needed, 
            # but usually just returning the reference is fine for single-consumer display
            return self.ret, self.frame

    def isOpened(self):
        return self.cap.isOpened()

    def release(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        self.cap.release()

class CameraManager:
    """
    Handles robust camera discovery and initialization across different hardware.
    """
    
    @staticmethod
    def find_working_camera():
        """
        Iterates through possible indices and backends to find a camera that actually 
        returns valid frames.
        
        Returns:
            ThreadedCamera: The threaded capture object, or None if no camera was found.
        """
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        indices = [0, 1, 2]
        
        print("🔍 Searching for working camera...")
        
        for index in indices:
            for backend in backends:
                backend_name = CameraManager._get_backend_name(backend)
                print(f"   - Testing Index {index} with {backend_name}...")
                
                try:
                    # Temporary test capture
                    test_cap = cv2.VideoCapture(index + backend)
                    
                    if not test_cap.isOpened():
                        test_cap.release()
                        continue
                    
                    # Force standard resolution for probe
                    test_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    test_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    
                    time.sleep(0.5)
                    ret, frame = test_cap.read()
                    
                    if ret and frame is not None and frame.size > 0:
                        # Validation for black frames
                        if frame.mean() > 0.1:
                            print(f"✅ Camera found! Index: {index}, Backend: {backend_name}")
                            test_cap.release()
                            # Return the threaded version for the UI
                            return ThreadedCamera(index, backend)
                    
                    test_cap.release()
                except Exception as e:
                    print(f"   ❌ Error probing index {index}/{backend_name}: {e}")
                    
        print("❌ No working camera detected after full probe.")
        return None

    @staticmethod
    def _get_backend_name(backend):
        if backend == cv2.CAP_DSHOW: return "DSHOW"
        if backend == cv2.CAP_MSMF: return "MSMF"
        return "ANY/OTHER"
