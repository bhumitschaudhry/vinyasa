# Vinyasa - Head Tracking Mouse

Vinyasa is a production-grade computer vision application that translates head movements into mouse pointer control. It uses a machine learning model for precise head position detection and PyAutoGUI for smooth system-level mouse interaction.

## Features

- **Professional Interface**: Production-grade, high-DPI aware, dark-themed dashboard built with `customtkinter`. Features a sidebar navigation and real-time telemetry.
- **Cross-Platform Compatibility**: Supports Windows, macOS, and Linux with automated hardware backend selection.
- **Smooth Mouse Control**: Optimized PyAutoGUI integration with zero-latency movement and custom acceleration curves.
- **Production Architecture**: Modularized Python package structure for high maintainability and scalability.
- **Calibration Wizard**: Interactive tool to adjust sensitivity and movement range to your personal comfort.
- **Hotkeys**: Quick toggle tracking with `F10`.
- **Persistent Settings**: Your configuration and calibration profiles are automatically saved using Pydantic validation.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/bhumitschaudhry/vinyasa.git
    cd vinyasa
    ```

2.  **Install dependencies**:
    ```bash
    pip install tensorflow opencv-python pyautogui pillow pydantic customtkinter darkdetect
    ```

### System Requirements

#### macOS
- **Permissions**: You must grant **Accessibility** permissions to your Terminal or IDE (System Settings > Privacy & Security > Accessibility) to allow mouse control.
- **Camera**: Grant camera access when prompted.

#### Linux
- **X11 vs Wayland**: Mouse control is most stable on **X11**. If using Wayland, you may need to switch to an X11 session for full functionality.
- **Dependencies**:
  ```bash
  sudo apt-get install python3-tk python3-dev
  ```

## Usage

1.  **Run the application**:
    ```bash
    python src/main.py
    ```
2.  **Start Tracking**: Click the "START TRACKING" button or press `F10`.
3.  **Calibrate**: Use the "CALIBRATE" button to open the wizard and adjust sensitivity.

## Technical Details

- **Hardware Backends**: Automatically selects `CAP_DSHOW` (Windows), `CAP_AVFOUNDATION` (macOS), or `CAP_V4L2` (Linux) for the camera.
- **Smoothing**: Uses a 3-frame prediction history buffer to eliminate tracking jitter.
- **Acceleration**: Dynamically increases mouse speed during sustained movement.
- **Threading**: Decouples camera capture from model inference for consistent high performance.

## License

MIT License
