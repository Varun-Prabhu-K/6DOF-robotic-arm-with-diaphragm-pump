# 6-DOF Robotic Arm Control System

## Project Overview

This project implements a web-based control system for a six-degree-of-freedom robotic arm. It combines an Arduino Uno, a PCA9685 servo controller, Python Flask, and a browser-based user interface.

The application allows users to control individual joints, move joints to specified angles, center the arm, and operate the suction pump.

## Features

- Web-based interface for six joint controls.
- Adjustable joint angles from 0° to 180°.
- Serial communication between the Flask backend and Arduino Uno.
- Center/home positioning commands.
- Suction pump ON/OFF control.
- Python unit tests for command validation and formatting.
- Selenium IDE functional tests for the web interface.
- Apache JMeter performance testing of the Flask web server.

## Technology Stack

| Technology | Purpose |
|---|---|
| Arduino Uno and C++ | Robotic arm firmware |
| PCA9685 | Servo control |
| Python | Backend logic and command validation |
| Flask | Web server and API |
| HTML, CSS and JavaScript | Browser-based control interface |
| pySerial | USB serial communication |
| Selenium IDE | Browser functional testing |
| Apache JMeter | HTTP performance testing |
| StarUML | UML modelling |

## System Architecture

The browser sends user commands to the Flask application. Flask validates and formats the commands, then transmits them through USB serial communication to the Arduino Uno. The Arduino firmware controls the servo controller and suction pump.

**Data flow:** Browser → Flask backend → USB serial → Arduino Uno → PCA9685 / servos and pump.

## Requirements

- Python 3
- Flask
- pySerial
- Arduino IDE for uploading the firmware
- Arduino Uno and compatible robotic arm hardware
- PCA9685 servo controller and connected servos
- Chrome or another compatible browser

## Setup and Execution

### 1. Upload the firmware

Open `firmware/RoboticArmController.ino` in Arduino IDE. Select the correct Arduino board and COM port, then upload the firmware.

### 2. Install Python dependencies

From the project root, run:

`python -m pip install -r requirements.txt`

### 3. Start the web application

Run:

`python app.py`

### 4. Open the interface

Navigate to:

`http://127.0.0.1:5000`

Select the Arduino's COM port and connect. Use the joint controls and action buttons to operate the arm.

Ensure the hardware is powered correctly and the arm's movement area is clear before sending commands.

## Testing

### Python Unit Testing

Run:

`python -m unittest discover -s tests -v`

Eight command-validation unit tests passed during testing.

### Selenium IDE

Selenium IDE was used to verify that the web application opens and that its page title matches the expected value. Slider playback was not consistently reliable, so it should not be reported as a fully automated slider test.

### Apache JMeter

A test plan was used to send HTTP GET requests to the Flask home page at `http://127.0.0.1:5000/`.

Recorded run configuration:
- Virtual users: 5
- Ramp-up period: 2 seconds
- Loop count: 5
- Total samples: 25

Recorded results:
- Average response time: 3 ms
- Minimum response time: 2 ms
- Maximum response time: 6 ms
- Error rate: 0%
- Throughput: 15.5 requests/second

These measurements describe the local Flask web server under this test configuration; they do not measure physical robotic arm performance.

## Project Structure

- `app.py`: Flask application and serial communication.
- `src/arm_commands.py`: Command validation and formatting.
- `src/arm_gui.py`: Auxiliary desktop interface.
- `templates/index.html`: Web user interface.
- `tests/test_arm_commands.py`: Python unit tests.
- `tests/Thread Group.jmx`: JMeter test plan.
- `firmware/RoboticArmController.ino`: Arduino firmware.
- `docs/`: UML and design files.
- `screenshots/`: Testing and application evidence.

## Limitations and Future Enhancements

Potential enhancements include improved hardware feedback, automated integration testing, more detailed communication error handling, and expanded performance testing under higher loads.

## Author and Project Information

Academic Software Engineering project.

**Note:** Confirm that all referenced files are included in the repository before submitting.
