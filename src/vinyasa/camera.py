"""
Camera management module.
Provides a threaded camera reader to decouple frame capture from the main UI thread.
"""

import cv2
import threading
import time
import logging
import sys
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class Camera:
    """
    Manages camera hardware and provides a constant stream of frames via a background thread.
    """
    def __init__(self, camera_id: int = 0, fps: int = 60):
        """
        Initialize the camera with platform-specific backends.
        
        Args:
            camera_id: System index for the camera.
            fps: Desired capture frame rate.
        """
        self.camera_id = camera_id
        self.fps = fps
        
        # Select best backend based on platform for stability
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
        """Starts the background capture thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True, name="CameraThread")
        self.thread.start()
        
    def _update(self):
        """Background loop to continuously read frames from the camera."""
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
        """
        Returns the most recent frame captured by the background thread.
        
        Returns:
            A tuple of (success_bool, frame_ndarray).
        """
        if self.frame is not None:
            return self.ret, self.frame.copy()
        return False, None
        
    def release(self):
        """Stops the capture thread and releases camera resources."""
        self.running = False
        if self.thread:
            self.thread.join()
        self.cap.release()
        logger.info("Camera resources released")
