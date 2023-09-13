#  The Recording Light
#### Microphone Monitor

This is a simple tool that allows users to monitor the volume level of a chosen microphone. The tool can provide visual feedback on whether the microphone is currently picking up sound, active or disabled.

## Why Use It?

This tool can quickly let you know if your microphone
is currently transmitting sound.
This is especially useful if you're concerned
about background noises or if you're muting and
unmuting frequently.


## Installation

### Prerequisites

Before you can run the application, ensure that you have Python installed on your machine along with the following libraries:

- sounddevice
- numpy
- tkinter

### Installation Steps:

#### Windows:

1. Install Python:
    - Download the Python installer from the [official website](https://www.python.org/downloads/).
    - Install Python and make sure to tick the "Add Python to PATH" option during installation.
  
2. Install required libraries:
    ```bash
    pip install sounddevice numpy
    ```

3. Save the provided code in a file named `mic_monitor.py`.

4. Run the tool:
    ```bash
    python mic_monitor.py
    ```

#### Linux:


1. Install required libraries:
    ```bash
    pip3 install sounddevice numpy
    sudo apt-get install portaudio19-dev
    ```

2. Run the tool:
    ```bash
    python3 mic_monitor.py
    ```

## Usage

1. When the tool starts, select your desired microphone from the dropdown list.
2. Click the "Start Monitoring" button.
3. The tool will display a small window. 
    - **Green with "OFF" label**: Indicates the microphone is not picking up any sound.
    - **Red with "ON AIR" label**: Indicates the microphone is currently active and picking up sound.

That's it! Now you can easily monitor your microphone's activity.
