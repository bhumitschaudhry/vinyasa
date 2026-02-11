# Vinyasa - Head Tracking Mouse

Vinyasa is a production-grade computer vision application that translates head movements into mouse pointer control. It uses a machine learning model for precise head position detection and PyAutoGUI for smooth system-level mouse interaction.

## Features

- **Smooth Mouse Control**: Optimized PyAutoGUI integration with zero-latency movement and custom acceleration curves.
- **Production Architecture**: Modularized Python package structure for high maintainability and scalability.
- **Modern Tech Stack**: Powered by TensorFlow, OpenCV, and Pydantic for robust configuration management.
- **Interactive UI**: Real-time camera feed, confidence visualization, and tracking status.
- **Calibration Wizard**: User-friendly tool to adjust sensitivity and movement range to your personal comfort.
- **Hotkeys**: Quick toggle tracking with `F10`.
- **Persistent Settings**: Your configuration and calibration profiles are automatically saved and loaded.

## Project Structure

```text
D:\vinyasa\
├── model/              # ML Model files (keras_model.h5, labels.txt)
├── src/
│   ├── main.py         # Application entry point
│   └── vinyasa/        # Core package
│       ├── app.py      # Main UI application
│       ├── camera.py   # Threaded camera reader
│       ├── config.py   # Pydantic configuration model
│       ├── mouse.py    # Mouse control logic
│       ├── tracker.py  # Model inference engine
│       └── ui/         # UI components (Calibration wizard)
├── tests/              # Unit test suite
├── pyproject.toml      # Dependency management
└── README.md
```

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/bhumitschaudhry/vinyasa.git
    cd vinyasa
    ```

2.  **Install dependencies**:
    ```bash
    pip install tensorflow opencv-python pyautogui pillow pydantic
    ```
    *Note: It is recommended to use a virtual environment.*

## Usage

1.  **Run the application**:
    ```bash
    python src/main.py
    ```
2.  **Start Tracking**: Click the "START TRACKING" button or press `F10`.
3.  **Calibrate**: Use the "CALIBRATE" button to open the wizard and adjust sensitivity.
4.  **Sensitivity**: You can also use the quick slider on the right panel to adjust speed on the fly.

## Testing

Run the unit test suite to verify core functionality:
```bash
python -m unittest discover tests
```

## Technical Details

- **Smoothing**: Uses a prediction history buffer to eliminate tracking jitter.
- **Acceleration**: Dynamically increases mouse speed when consistent direction is detected.
- **Threading**: Decouples camera capture from model inference for high FPS and low latency.
- **Type Safety**: Fully typed codebase with Pydantic validation.

## License

MIT License
