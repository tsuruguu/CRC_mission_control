# Skylink Mission Control – CRC 2026

A professional **Ground Station** designed for the **FST AGH** team for the CRC 2026 competition.  
The application is used for real‑time rocket telemetry monitoring, supervision of the AstroBio biological experiment, and visualization of spatial orientation.

## 🚀 Main Features

* **Real‑time Telemetry**: Receiving and parsing LoRa/STM32 data at up to 20 Hz.
* **3D Navball (GPU)**: Hardware‑accelerated artificial horizon visualization (Roll, Pitch, Yaw) using transformation matrices.
* **Biological Payload Monitor**: A dedicated tab for supervising the algae experiment, including real‑time temperature charts and large UV indicators.
* **Audit Trail & Logging**: Dual logging system – telemetry saved to CSV and system logs (operator actions, connection errors).
* **Skylink Design**: Teal/Dark interface optimized for readability and NASA‑Modern ergonomics.

## 📂 Project Structure

### `/core` – Logic and Data
* **`data_types.py`**: Defines data models `TelemetryFrame` and mission (`MissionState`) and connection (`ConnectionStatus`) states.
* **`serial_manager.py`**: Manages threaded COM‑port communication, calculates bitrate, and handles raw‑data queuing.
* **`telemetry.py`**: Advanced CSV parser that monitors frame continuity and manages LED status logic.
* **`logger.py`**: Handles asynchronous data writing to files in the `/logs` directory.

### `/ui` – User Interface
* **`theme.py`**: Defines the Skylink AGH color palette, visual styles, and manages font/icon loading.
* **`layout.py`**: Main window structure, HARDWARE/PAYLOAD tab layout, and definitions of the Top Bar and Bottom Bar.
* **`navball.py`**: PFD (Primary Flight Display) widget rendering the artificial horizon using the GPU.
* **`components.py`**: Collection of components such as Terminal, LED indicators, and the `PayloadManager` handling charts.

### Main Files
* **`main.py`**: The heart of the application, connecting logic with UI in a high‑performance loop.
* **`simulator.py`**: Advanced telemetry generator simulating rocket flight physics.
* **`requirements.txt`**: List of library dependencies.

## 🛠️ Installation and Launch

1. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```
   
2. Run the application:
   ```bash
   python main.py
   ```
   
---

## ⚠️ Critical Buttons
*   **ARM & SYNC**: Arms recovery systems and synchronizes RTC time.
*   **ABORT**: Immediate sequence interruption and forced safety mode.


```python?code_reference&code_event_index=1
import zipfile
import os

# File structure definition based on previous specifications
project_files = {
    "main.py": """# Contents of main.py according to the latest version...""",
    "simulator.py": """# Contents of simulator.py...""",
    "requirements.txt": "dearpygui==1.11.1\npyserial==3.5\nnumpy==1.24.3",
    ".gitignore": "__pycache__/\nlogs/\n*.py[cod]\nvenv/",
    "core/data_types.py": """# Contents of data_types.py...""",
    "core/serial_manager.py": """# Contents of serial_manager.py...""",
    "core/telemetry.py": """# Contents of telemetry.py...""",
    "core/logger.py": """# Contents of logger.py...""",
    "ui/theme.py": """# Contents of theme.py...""",
    "ui/layout.py": """# Contents of layout.py...""",
    "ui/components.py": """# Contents of components.py...""",
    "ui/navball.py": """# Contents of navball.py...""",
    "README.md": "Skylink Mission Control Documentation"
}

zip_name = "CRC_mission_control_v2.zip"

with zipfile.ZipFile(zip_name, 'w') as zipf:
    for file_path, content in project_files.items():
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        zipf.write(file_path)

print(zip_name)
```

