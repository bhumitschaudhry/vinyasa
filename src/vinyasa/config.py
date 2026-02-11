from pydantic import BaseModel, Field
from pathlib import Path
import logging
from typing import ClassVar

logger = logging.getLogger(__name__)

class Config(BaseModel):
    # Model settings
    MODEL_PATH: Path = Path("model/keras_model.h5")
    LABELS_PATH: Path = Path("model/labels.txt")
    INPUT_SIZE: tuple[int, int] = (224, 224)
    CONFIDENCE_THRESHOLD: float = Field(default=0.8, ge=0.0, le=1.0)
    
    # Mouse settings
    INITIAL_SENSITIVITY: int = Field(default=10, ge=1)
    LINES_PER_SECOND: int = Field(default=1, ge=1)
    CURSOR_SIZE: int = Field(default=1, ge=1)
    DEFAULT_PAUSE: float = 0.0
    FAILSAFE: bool = True
    
    # Camera settings
    CAMERA_ID: int = 0
    FPS: int = 60
    
    # UI settings
    WINDOW_TITLE: str = "Vinyasa"
    WINDOW_SIZE: str = "1000x600"

    # Internal
    CONFIG_FILE: Path = Path("config.json")

    def save(self):
        try:
            # We exclude CONFIG_FILE from saving if we want, but pydantic handles it
            with open(self.CONFIG_FILE, "w") as f:
                f.write(self.model_dump_json(indent=4))
            logger.info("Config saved to file")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    @classmethod
    def load(cls) -> "Config":
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return cls.model_validate_json(f.read())
            except Exception as e:
                logger.error(f"Failed to load config, using defaults: {e}")
        return cls()
