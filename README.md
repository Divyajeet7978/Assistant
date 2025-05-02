# 🌟 Ultimate Voice Assistant

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/Version-2.0-orange.svg)

A sophisticated voice assistant with natural language processing, weather forecasting, media control, and more - featuring a beautiful graphical interface.


## ✨ Features

- **🎙️ Voice Recognition** - Natural speech processing with noise cancellation
- **🌦️ Weather Forecasts** - Real-time weather data from WeatherAPI.com
- **📚 Wikipedia Search** - Instant knowledge lookup
- **🎵 Media Control** - Launch Spotify with voice commands
- **🌐 Web Integration** - Open YouTube/Google with custom browser paths
- **💬 Interactive UI** - Beautiful Tkinter interface with conversation history
- **⚙️ Cross-Platform** - Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Microphone
- Internet connection

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/ultimate-voice-assistant.git
cd ultimate-voice-assistant

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from example)
cp .env.example .env
```

### Configuration
Edit the `.env` file:
```env
# WeatherAPI.com Key (get from https://www.weatherapi.com/)
WEATHERAPI_KEY=your_api_key_here

# Personalization
ASSISTANT_USER_NAME=YourName

# Optional Path Overrides
BROWSER_PATH=default
SPOTIFY_PATH=default
```

### Running the Assistant
```bash
python assistant.py
```

## 🛠️ Command Reference

| Command | Examples | Action |
|---------|----------|--------|
| **Weather** | "What's the weather in London?", "Weather forecast for Paris" | Get current weather conditions |
| **Wikipedia** | "Search Wikipedia for Python", "Tell me about machine learning" | Get summarized Wikipedia information |
| **Media** | "Open Spotify", "Play music" | Launch Spotify player |
| **Web** | "Open YouTube", "Search Google for cats" | Open web services |
| **System** | "Exit", "Goodbye" | Close the application |

## 🧩 Project Structure

```
ultimate-voice-assistant/
├── assistant.py          # Main application
├── .env                  # Configuration file
├── .env.example          # Example configuration
├── requirements.txt      # Dependencies
├── README.md             # This file
└── assets/               # Optional media files
    └── icons/            # Application icons
```

