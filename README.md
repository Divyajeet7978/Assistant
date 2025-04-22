# Voice Assistant

A simple Python-based voice assistant that can perform various tasks like web browsing, fetching weather information, searching Wikipedia, and more using voice commands.

## Features

- **Voice Interaction**: Speak commands and get responses
- **Web Browsing**: Open YouTube, Google, and other websites
- **Weather Information**: Get current weather for any city
- **Wikipedia Search**: Fetch summaries from Wikipedia
- **Application Launch**: Launch applications like Spotify
- **Time-based Greetings**: Greets you based on time of day

## Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.x
- Required Python packages (install via `pip install -r requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd voice-assistant

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the assistant by executing:
```bash
python voice_assistant.py
```

## Configuration

The script requires some configuration:

1. **Edge Browser Path**: Update `edge_path` variable if Edge is installed in a different location
2. **Spotify Path**: The script automatically detects Spotify path for the current user
3. **Weather API Key**: Requires OpenWeatherMap API key (currently using a test key)

## Dependencies

- pyttsx3
- SpeechRecognition
- wikipedia
- webbrowser
- requests
- datetime

## Limitations

- Currently only works on Windows
- Voice recognition accuracy may vary
- Requires internet connection for most features
