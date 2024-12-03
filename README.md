# WaveOff Server
WaveOff Server is a project designed to integrate Python and Kotlin functionalities, featuring gesture recognition, server management, and MediaPipe utilities. The project also incorporates a full-stack engineering workflow, providing seamless interaction between a mobile application and server-side processing for gesture-based call management.

## Overview
This project enables advanced gesture recognition and real-time processing for Android applications. Leveraging the CameraX API, Flask server, and Web Socket communication, the system processes gestures to automate call management actions such as accepting or rejecting incoming calls. It also explores experimental Kotlin-Python interoperability for further extensibility.

## Features
- **Gesture Recognition**: Advanced hand gesture recognition using MediaPipe and AI techniques.
- **Real-Time Processing**: Captures and processes camera frames using the CameraX API and transmits data efficiently over WebSocket.
- **Server Management**: Flask server for processing and managing gesture recognition results.
- **Python-Kotlin Integration**: Scripts for experimenting with Python and Kotlin interoperability.
- **Call Handling Automation**: Integrates with Android's TelecomManager and TelephonyManager for gesture-based call control.
- **Logging and Debugging**: Includes logging utilities (`terminal_output.log`) for debugging.
- **Extensible Utilities**: Modular design with helpers and utility scripts.

## Installation
1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd waveoff_server
    ```
2. Ensure your Python and Kotlin environments are correctly set up.

## Usage
### End-to-End Process
1. **Application Initialization**:
   - Launch the Android application to initialize the camera using the CameraX API.
   - Frames captured in YUV format are converted to BGR color format and sent as Base64-encoded strings via WebSocket.
2. **Server-Side Processing**:
   - Flask server decodes the Base64 strings and processes the images for gesture recognition.
   - Recognized gestures are broadcast as JSON responses to observers.
3. **Gesture-Based Call Management**:
   - The application parses the gesture results (e.g., "Accept" or "Reject") and interacts with the TelecomManager to manage calls accordingly.
   - A ForegroundService monitors call states via the TelephonyManager.

### Running the Server
To run the main server:
```bash
python server.py
```
### Exploring Python-Kotlin Interoperability
```bash
python Kotlin\ Python\ Call\ Experiment.py
```
### Running the App
You can directly run the android application, provided that you have connected an Android phone with Developer Options enabled, by going into the `waveoff_app` folder.

## Folder Structure Of Server Codebase
```plaintext
waveoff_server/
├── helper/                # Helper scripts for various tasks
├── mediapipe_helpers/     # MediaPipe-related functionalities
├── model/                 # Data models or pretrained models
├── utils/                 # Utility functions
├── main.py                # Main entry point for the server
├── constants.py           # Constants for the project
├── server.py              # Core server script
├── LICENSE                # License information
├── README.md              # Documentation (this file)
└── terminal_output.log    # Debugging logs
```

## Contributing
We welcome contributions! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add a new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License
This project is licensed under **Apache 2.0**.
