import cv2
import threading
import time
import logging
import sys
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, camera_id: int = 0, fps: int = 60):
        self.camera_id = camera_id
        self.fps = fps
        
        # Select best backend based on platform
        backend = cv2.CAP_ANY
        if sys.platform == "win32":
            backend = cv2.CAP_DSHOW
        elif sys.platform == "darwin":
            backend = cv2.CAP_AVFOUNDATION
        elif sys.platform == "linux":
            backend = cv2.CAP_V4L2
            
        self.cap = cv2.VideoCapture(self.camera_id, backend)
        
        # Fallback if specific backend fails
        if not self.cap.isOpened():
            logger.warning(f"Failed to open camera with {sys.platform} backend, falling back to CAP_ANY")
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_ANY)
            
        self.ret = False
        self.frame: Optional[np.ndarray] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        if not self.cap.isOpened():
            logger.error(f"Could not open camera {camera_id}")
            
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        
    def _update(self):
        while self.running:
            self.ret, self.frame = self.cap.read()
            if not self.ret:
                logger.warning("Camera frame capture failed. Attempting to reconnect...")
                self.cap.release()
                time.sleep(2)
                self.cap = cv2.VideoCapture(self.camera_id)
            else:
                time.sleep(1/self.fps)
            
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.frame is not None:
            return self.ret, self.frame.copy()
        return False, None
        
    def release(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.cap.release()
