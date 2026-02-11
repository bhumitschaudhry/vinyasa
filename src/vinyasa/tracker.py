import cv2
import numpy as np
import logging
from pathlib import Path
from typing import Tuple, List, Optional

logger = logging.getLogger(__name__)

try:
    import tensorflow as tf
except ImportError:
    tf = None
    logger.warning("TensorFlow not found. HeadTracker will not work.")

class HeadTracker:
    def __init__(self, model_path: Path, labels_path: Path):
        if tf is None:
            raise ImportError("TensorFlow is required to use HeadTracker")
        
        self.model_path = Path(model_path)
        try:
            # Modernize: Check for .keras first or load .h5
            # In a real scenario, we might want to migrate .h5 to .keras here
            self.model = tf.keras.models.load_model(self.model_path, compile=False)
            logger.info(f"Model loaded from {self.model_path}")
            
            self.labels = self._load_labels(Path(labels_path))
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def _load_labels(self, path: Path) -> List[str]:
        labels = []
        with open(path, "r") as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) > 1:
                    labels.append(parts[1])
                else:
                    labels.append(parts[0])
        return labels

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        img = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        img = np.asarray(img, dtype=np.float32).reshape(1, 224, 224, 3)
        img = (img / 127.5) - 1
        return img

    def predict(self, image: np.ndarray) -> Tuple[str, float]:
        processed_img = self.preprocess(image)
        prediction = self.model(processed_img, training=False).numpy()
        index = np.argmax(prediction)
        confidence = prediction[0][index]
        return self.labels[index], float(confidence)
