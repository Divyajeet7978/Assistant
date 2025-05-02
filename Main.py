import asyncio
import logging
import os
import platform
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Callable, Any

import pyttsx3
import requests
import speech_recognition as sr
import wikipedia
import webbrowser
from dotenv import load_dotenv
import tkinter as tk
from tkinter import scrolledtext, ttk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Voice Assistant")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Set up graceful window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize assistant
        self.assistant = UltimateVoiceAssistant(self)
        
        # UI Elements
        self.create_widgets()
        
        # Start assistant in a separate thread
        self.assistant_thread = threading.Thread(target=self.start_assistant, daemon=True)
        self.assistant_thread.start()

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Ultimate Voice Assistant", 
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(
            status_frame, 
            text="Ready", 
            foreground="green"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Mic button
        self.mic_button = ttk.Button(
            status_frame, 
            text="🎤", 
            command=self.toggle_listening,
            width=3
        )
        self.mic_button.pack(side=tk.RIGHT)
        
        # Conversation display
        self.conversation_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=('Helvetica', 10)
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        self.conversation_text.configure(state='disabled')
        
        # Command buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Quick command buttons
        commands = [
            ("Wikipedia Search", self.assistant.handle_wikipedia),
            ("Open YouTube", self.assistant.open_youtube),
            ("Open Google", self.assistant.open_google),
            ("Weather", self.assistant.fetch_weather),
            ("Exit", self.assistant.exit_assistant)
        ]
        
        for text, command in commands:
            button = ttk.Button(
                buttons_frame,
                text=text,
                command=lambda cmd=command: self.execute_command(cmd)
            )
            button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def toggle_listening(self):
        """Toggle listening state"""
        if self.assistant.is_listening:
            self.assistant.stop_listening()
            self.mic_button.config(text="🎤")
            self.update_status("Ready", "green")
        else:
            self.assistant.start_listening()
            self.mic_button.config(text="🔴")
            self.update_status("Listening...", "blue")

    def execute_command(self, command):
        """Execute a command from button"""
        self.add_to_conversation("You: Button command")
        if asyncio.iscoroutinefunction(command):
            asyncio.run_coroutine_threadsafe(command(""), self.assistant.loop)
        else:
            command("")

    def start_assistant(self):
        """Start the assistant in a separate thread"""
        try:
            self.assistant.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.assistant.loop)
            self.assistant.loop.run_until_complete(self.assistant.run())
        except Exception as e:
            logger.error(f"Assistant thread failed: {e}")
            self.update_status("Error in assistant", "red")

    def add_to_conversation(self, text):
        """Add text to conversation display"""
        self.conversation_text.configure(state='normal')
        self.conversation_text.insert(tk.END, text + "\n")
        self.conversation_text.configure(state='disabled')
        self.conversation_text.see(tk.END)

    def update_status(self, text, color):
        """Update status label"""
        self.status_label.config(text=text, foreground=color)

    def on_closing(self):
        """Handle window closing"""
        self.assistant.stop_listening()
        if hasattr(self.assistant, 'loop') and self.assistant.loop.is_running():
            self.assistant.loop.stop()
        self.root.destroy()

class UltimateVoiceAssistant:
    def __init__(self, app):
        self.app = app
        self.loop = None
        self.is_listening = False
        self.setup()
        
        # Command mappings with descriptions
        self.commands: Dict[str, Dict[str, Any]] = {
            'wikipedia': {
                'handler': self.handle_wikipedia,
                'description': 'Search Wikipedia for information'
            },
            'open youtube': {
                'handler': self.open_youtube,
                'description': 'Open YouTube in browser'
            },
            'open google': {
                'handler': self.open_google,
                'description': 'Open Google in browser'
            },
            'open spotify': {
                'handler': self.open_spotify,
                'description': 'Launch Spotify application'
            },
            'weather': {
                'handler': self.fetch_weather,
                'description': 'Get weather information for a city'
            },
            'goodbye': {
                'handler': self.exit_assistant,
                'description': 'Exit the voice assistant'
            },
            'exit': {
                'handler': self.exit_assistant,
                'description': 'Exit the voice assistant'
            },
            'quit': {
                'handler': self.exit_assistant,
                'description': 'Exit the voice assistant'
            },
            'help': {
                'handler': self.show_help,
                'description': 'Show available commands'
            }
        }

    def setup(self):
        """Initialize all components"""
        try:
            self.engine = self.init_tts_engine()
            self.recognizer = sr.Recognizer()
            self.browser_path = self.get_browser_path()
            self.spotify_path = self.get_spotify_path()
            self.user_name = self.get_user_name()
            self.weather_api_key = os.getenv('WEATHER_API_KEY')
            
            # Configure microphone
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
            logger.info("Voice assistant initialized successfully")
            self.check_configuration()
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    def check_configuration(self):
        """Validate required configuration"""
        if not self.weather_api_key:
            logger.warning("Weather API key not configured")
        if self.spotify_path is not None and not os.path.exists(self.spotify_path):
            logger.warning(f"Spotify path not found: {self.spotify_path}")

    def init_tts_engine(self):
        """Initialize and configure the text-to-speech engine."""
        try:
            engine = pyttsx3.init()
            rate = engine.getProperty('rate')
            engine.setProperty('rate', max(100, rate - 40))  # Ensure rate doesn't go too low
            voices = engine.getProperty('voices')
            
            # Try to select a more natural sounding voice if available
            preferred_voices = [
                'english-us', 'english', 'Microsoft David Desktop'
            ]
            for voice in voices:
                if any(pref.lower() in voice.name.lower() for pref in preferred_voices):
                    engine.setProperty('voice', voice.id)
                    break
            else:
                engine.setProperty('voice', voices[0].id)
                
            return engine
        except Exception as e:
            logger.error(f"TTS engine initialization failed: {e}")
            raise

    def get_browser_path(self) -> str:
        """Get the path to the default browser with cross-platform support."""
        system = platform.system()
        if system == 'Windows':
            return "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s"
        elif system == 'Darwin':  # macOS
            return "open -a /Applications/Safari.app %s"
        else:  # Linux
            return "xdg-open %s"

    def get_spotify_path(self) -> Optional[str]:
        """Get the path to Spotify executable with cross-platform support."""
        system = platform.system()
        try:
            if system == 'Windows':
                username = os.getenv('USERNAME')
                path = f"C:/Users/{username}/AppData/Roaming/Spotify/Spotify.exe"
                return path if os.path.exists(path) else None
            elif system == 'Darwin':  # macOS
                path = "/Applications/Spotify.app/Contents/MacOS/Spotify"
                return path if os.path.exists(path) else None
            else:  # Linux
                try:
                    subprocess.run(["which", "spotify"], check=True)
                    return "spotify"
                except subprocess.CalledProcessError:
                    return None
        except Exception as e:
            logger.warning(f"Couldn't get Spotify path: {e}")
            return None

    def get_user_name(self) -> str:
        """Get the current user's name with cross-platform support."""
        try:
            name = os.getenv('ASSISTANT_USER_NAME')
            if name:
                return name
                
            system = platform.system()
            if system == 'Windows':
                return os.getenv('USERNAME', 'User')
            else:  # macOS/Linux
                return os.getenv('USER', 'User')
        except Exception as e:
            logger.warning(f"Couldn't get user name: {e}")
            return "User"

    def speak(self, text: str) -> None:
        """Convert text to speech and update UI."""
        logger.info(f"Speaking: {text}")
        self.app.add_to_conversation(f"Assistant: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}")
            self.app.add_to_conversation("[Speech synthesis failed]")

    def start_listening(self):
        """Start continuous listening."""
        self.is_listening = True
        self.app.update_status("Listening...", "blue")

    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
        self.app.update_status("Ready", "green")

    async def listen(self) -> Optional[str]:
        """Listen for and recognize speech input."""
        if not self.is_listening:
            return None
            
        with sr.Microphone() as source:
            self.app.update_status("Listening...", "blue")
            logger.info("Listening...")
            
            try:
                audio = self.recognizer.listen(
                    source, 
                    timeout=5, 
                    phrase_time_limit=8
                )
                self.app.update_status("Recognizing...", "orange")
                logger.info("Recognizing...")
                
                query = self.recognizer.recognize_google(
                    audio, 
                    language='en-in'
                ).lower()
                
                logger.info(f"Recognized: {query}")
                self.app.add_to_conversation(f"You: {query}")
                return query
                
            except sr.WaitTimeoutError:
                logger.info("Listening timed out (no speech detected)")
                return None
            except sr.UnknownValueError:
                self.speak("I didn't catch that. Could you please repeat?")
                logger.warning("Speech recognition could not understand audio")
                return None
            except sr.RequestError as e:
                self.speak("Sorry, I'm having trouble accessing the speech recognition service.")
                logger.error(f"Could not request results from speech recognition service: {e}")
                return None
            except Exception as e:
                logger.error(f"Error in recognition: {e}")
                self.speak("Sorry, I encountered an error. Please try again.")
                return None
            finally:
                if self.is_listening:
                    self.app.update_status("Listening...", "blue")
                else:
                    self.app.update_status("Ready", "green")

    def greet(self) -> None:
        """Greet the user based on time of day."""
        hour = datetime.now().hour
        if 0 <= hour < 12:
            greeting = f"Good morning {self.user_name}!"
        elif 12 <= hour < 18:
            greeting = f"Good afternoon {self.user_name}!"
        else:
            greeting = f"Good evening {self.user_name}!"
        
        self.speak(greeting)
        self.speak("How can I help you today?")

    def handle_wikipedia(self, query: str) -> None:
        """Handle Wikipedia search requests."""
        try:
            search_query = query.replace("wikipedia", "").strip()
            if not search_query:
                self.speak("What would you like me to search on Wikipedia?")
                return
                
            self.speak(f"Searching Wikipedia for {search_query}")
            
            # Set language for Wikipedia
            wikipedia.set_lang("en")
            
            try:
                results = wikipedia.summary(
                    search_query, 
                    sentences=2,
                    auto_suggest=True
                )
                self.speak("According to Wikipedia")
                self.speak(results)
            except wikipedia.exceptions.DisambiguationError as e:
                options = e.options[:3]  # Get first 3 options
                self.speak(f"There are multiple options for {search_query}. Did you mean: {', '.join(options)}?")
            except wikipedia.exceptions.PageError:
                self.speak(f"Sorry, I couldn't find any information about {search_query}.")
            except Exception as e:
                logger.error(f"Wikipedia search error: {e}")
                self.speak("Sorry, I encountered an error while searching Wikipedia.")
                
        except Exception as e:
            logger.error(f"Wikipedia error: {e}")
            self.speak("Sorry, I couldn't access Wikipedia right now.")

    def open_youtube(self, _: str = None) -> None:
        """Open YouTube in the default browser."""
        self.speak("Opening YouTube")
        try:
            webbrowser.get(self.browser_path).open("https://youtube.com")
        except webbrowser.Error as e:
            logger.error(f"Failed to open browser: {e}")
            self.speak("Sorry, I couldn't open the web browser.")
        except Exception as e:
            logger.error(f"Failed to open YouTube: {e}")
            self.speak("Sorry, I couldn't open YouTube.")

    def open_google(self, _: str = None) -> None:
        """Open Google in the default browser."""
        self.speak("Opening Google")
        try:
            webbrowser.get(self.browser_path).open("https://google.com")
        except webbrowser.Error as e:
            logger.error(f"Failed to open browser: {e}")
            self.speak("Sorry, I couldn't open the web browser.")
        except Exception as e:
            logger.error(f"Failed to open Google: {e}")
            self.speak("Sorry, I couldn't open Google.")

    def open_spotify(self, _: str = None) -> None:
        """Open Spotify application."""
        if self.spotify_path is None:
            self.speak("Spotify is not configured on this system.")
            return
            
        self.speak("Opening Spotify")
        try:
            if platform.system() == 'Windows':
                os.startfile(self.spotify_path)
            else:
                subprocess.Popen(self.spotify_path)
        except Exception as e:
            logger.error(f"Failed to open Spotify: {e}")
            self.speak("Sorry, I couldn't open Spotify.")

    async def fetch_weather(self, query: str = None) -> None:
        """Fetch and announce weather information using WeatherAPI.com"""
        try:
            # Get API key from environment variables
            api_key = os.getenv("WEATHERAPI_KEY")
            if not api_key:
                self.speak("Weather service is not properly configured.")
                logger.error("WeatherAPI key missing from environment variables")
                return

            city = None
            
            # Extract city name from query if present
            if query:
                parts = query.split()
                for i, part in enumerate(parts):
                    if part in ['for', 'in', 'of'] and i < len(parts) - 1:
                        city = parts[i+1]
                        break
            
            # If no city found in query, ask user
            if not city:
                self.speak("Which city's weather would you like to know?")
                city_response = await self.listen()
                if city_response:
                    city = city_response
                else:
                    return

            weather_url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no'
            
            # Make API request
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                requests.get, 
                weather_url
            )
            
            weather_info = response.json()

            if response.status_code == 200:
                current = weather_info['current']
                location = weather_info['location']
                
                temp = current['temp_c']
                feels_like = current['feelslike_c']
                humidity = current['humidity']
                wind_speed = current['wind_kph']
                condition = current['condition']['text']
                
                weather_report = (
                    f"Current weather in {location['name']}: "
                    f"Condition: {condition}. "
                    f"Temperature: {temp}°C, "
                    f"Feels like: {feels_like}°C. "
                    f"Humidity: {humidity}%. "
                    f"Wind speed: {wind_speed} km/h."
                )
                self.speak(weather_report)
            else:
                error_msg = weather_info.get('error', {}).get('message', 'Unknown error')
                logger.error(f"Weather API error: {error_msg}")
                self.speak(f"Sorry, I couldn't find weather information for {city}.")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            self.speak("Sorry, I'm having trouble accessing the weather service.")
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
            self.speak("Sorry, I received unexpected weather data format.")
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            self.speak("Sorry, I encountered an error while fetching weather information.")

    def show_help(self, _: str = None) -> None:
        """Show available commands."""
        help_text = "Here's what I can do:\n"
        for command, info in self.commands.items():
            help_text += f"- {command}: {info['description']}\n"
        self.speak(help_text)

    def exit_assistant(self, _: str = None) -> bool:
        """Handle exit commands."""
        self.speak(f"Goodbye {self.user_name}, have a nice day!")
        self.app.root.after(1000, self.app.root.destroy)
        return True

    async def process_command(self, command: str) -> bool:
        """Process recognized commands."""
        if not command:
            return False
            
        # Check for exact matches first
        for cmd, info in self.commands.items():
            if cmd in command:
                handler = info['handler']
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(command)
                    else:
                        handler(command)
                    
                    if cmd in ['exit', 'quit', 'goodbye']:
                        return True
                    return False
                except Exception as e:
                    logger.error(f"Error executing command {cmd}: {e}")
                    self.speak("Sorry, I had trouble executing that command.")
                    return False
        
        # If no exact match, check for partial matches
        for cmd, info in self.commands.items():
            if any(word in command for word in cmd.split()):
                handler = info['handler']
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(command)
                    else:
                        handler(command)
                    return False
                except Exception as e:
                    logger.error(f"Error executing command {cmd}: {e}")
                    self.speak("Sorry, I had trouble executing that command.")
                    return False
        
        self.speak("I didn't understand that command. Say 'help' for available commands.")
        return False

    async def run(self):
        """Main execution loop for the voice assistant."""
        self.greet()
        
        while True:
            if self.is_listening:
                command = await self.listen()
                if command and await self.process_command(command):
                    break
            await asyncio.sleep(0.1)

def main():
    """Main entry point for the application."""
    try:
        root = tk.Tk()
        app = VoiceAssistantApp(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
