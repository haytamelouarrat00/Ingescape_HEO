# Whiteboard Speech Agent

This project is a speech recognition agent that interacts with a whiteboard service. It can recognize simple voice commands to perform various actions on the whiteboard, such as adding transcription, clearing the board, hiding/showing labels, and adding images.

## Features

- Start and stop voice recognition
- Clear the whiteboard
- Hide and show labels on the whiteboard
- Add images to the whiteboard
- Send chat messages to the whiteboard

## Requirements

- Python 3.6+
- `ingescape`
- `pip` (Python package installer)
- `portaudio` (for `pyaudio`)

```bash
pip install SpeechRecognition
pip install pyttsx3
pip install pyaudio
pip install ingescape
```

### Usage:
```bash
cd /path/to/src
python main.py
```

## Interactive commands:
The system takes multiples commands:
- "Stop Listening"
- "Clear board"
- "Show Labels"
- "Hide Labels"
- "Add image"

### Issues:

- Audio recognition stops after first command is passed. Requires system restart after each execution.
- Adding image not working properly.

