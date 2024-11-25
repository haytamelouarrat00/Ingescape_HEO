# whiteboard_speech_agent.py

import ingescape as igs
import speech_recognition as sr
import pyttsx3
import threading
from pathlib import Path
import time
import tkinter as tk
from tkinter import filedialog
from src.util import add_Image_From_URL

from src.util import hide_Labels, clearWhitboard


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class WhiteboardSpeechAgent(metaclass=Singleton):
    def __init__(self):
        # Speech recognition components
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.is_listening = False
        self.listen_thread = None
        self.current_thread_id = None

        # Configure recognizer
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 4000  # Increased from default
        self.recognizer.pause_threshold = 0.8  # Time of silence needed to consider the phrase complete
        self.recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking needed to consider the phrase started
        self.recognizer.non_speaking_duration = 0.5  # How long before we consider a phrase complete

        # Input/Output state
        self.last_transcription = ""
        self.last_command = ""
        self.last_response = ""

        # Create inputs and outputs
        self._create_ios()

    def _create_ios(self):
        """Create all inputs and outputs for the agent"""
        # Inputs
        igs.input_create("start_listening", igs.IMPULSION_T, None)
        igs.input_create("stop_listening", igs.IMPULSION_T, None)
        igs.input_create("command_text", igs.STRING_T, None)

        # Outputs
        igs.output_create("speech_transcription", igs.STRING_T, None)
        igs.output_create("command_processed", igs.STRING_T, None)
        igs.output_create("system_status", igs.STRING_T, None)

        igs.output_create("clear_whiteboard", igs.IMPULSION_T, None)
        igs.output_create("hide_labels", igs.IMPULSION_T, None)
        igs.output_create("show_labels", igs.IMPULSION_T, None)
        igs.output_create("add_image", igs.IMPULSION_T, None)

        # Initialize status
        self._update_status("Agent initialized")

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            if not self.listen_thread or not self.listen_thread.is_alive():
                self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
                self.listen_thread.start()
            self._update_status("Listening active")
            self.speak("Voice recognition activated")
        else:
            self._update_status("Already listening")

    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False
            if self.listen_thread and self.listen_thread.is_alive():
                try:
                    self.listen_thread.join(timeout=2)
                except RuntimeError:
                    self._update_status("Failed to cleanly join the listening thread")
            self._update_status("Listening inactive")
            self.speak("Voice recognition deactivated")
        else:
            self._update_status("Already stopped")

    def speak(self, text):
        """Convert text to speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self._update_status(f"Speech synthesis error: {str(e)}")

    def _listen_loop(self):
        """Main speech recognition loop"""
        with sr.Microphone() as source:
            try:
                self._update_status("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self._update_status("Ambient noise adjustment complete")
            except Exception as e:
                self._update_status(f"Failed to adjust for ambient noise: {str(e)}")

            while self.is_listening:
                try:
                    self._update_status("Actively listening for speech...")
                    audio = self.recognizer.listen(source, phrase_time_limit=10)

                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        self._update_status("Speech detected, processing...")
                        self._handle_speech(text)  # Continue processing
                    except sr.UnknownValueError:
                        # No speech detected, continue listening
                        pass
                    except sr.RequestError as e:
                        self._update_status(f"Speech recognition error: {str(e)}")
                        time.sleep(1)  # Short wait before retrying

                except Exception as e:
                    if not self.is_listening:  # Expected exception when stopping
                        break
                    self._update_status(f"Microphone error: {str(e)}")
                    time.sleep(1)  # Wait before retrying
                    continue

    def _handle_speech(self, text):
        """Process recognized speech"""
        # Update transcription output
        self.last_transcription = text
        igs.output_set_string("speech_transcription", text)
        self._update_status(f"Processing speech: '{text}'")

        # Check for stop command first
        if self._is_stop_command(text):
            self._update_status("Stop command received")
            self.stop_listening()
            return

        # Process other commands
        command = self._parse_command(text)
        if command:
            self.last_command = command
            igs.output_set_string("command_processed", command)
            self._update_status(f"Command executed: {command}")
        else:
            self._update_status("No command detected, sending to chat")
            # Send to whiteboard chat
            igs.service_call("Whiteboard", "chat", text, "")

    def _is_stop_command(self, text):
        """Check if the text contains a stop command"""
        stop_phrases = [
            "stop listening",
            "stop recognition",
            "stop voice recognition",
            "deactivate voice",
            "turn off voice",
            "end listening"
        ]
        return any(phrase in text.lower() for phrase in stop_phrases)

    def _parse_command(self, text):
        """Parse speech text for commands"""
        commands = {
            "add text": lambda t: self._handle_add_text(t),
            "clear board": lambda _: self._handle_clear(),
            "hide labels": lambda _: self._handle_hide_labels(),
            "show labels": lambda _: self._handle_show_labels(),
            "add image": lambda _: self._handle_add_image(),
        }

        for cmd, handler in commands.items():
            if cmd in text:
                return handler(text)
        return None

    def _handle_add_text(self, text):
        """Handle 'add text' command"""
        content = text.replace("add text", "").strip()
        if content:
            igs.service_call("Whiteboard", "addText", (content, 100, 100, "black"), "")
            self.speak(f"Added text: {content}")
            return f"Added text: {content}"
        return None

    def _handle_clear(self):
        """Handle 'clear board' command"""
        try:
            igs.service_call("Whiteboard", "clear", "", "")
            igs.output_set_impulsion("clear_whiteboard")
            self.speak("Whiteboard cleared")
            return "Cleared whiteboard"
        except Exception as e:
            self._update_status(f"Failed to clear whiteboard: {str(e)}")
            return None

    def _handle_hide_labels(self):
        """Handle 'hide labels' command"""
        try:
            igs.service_call("Whiteboard", "hideLabels", "", "")
            igs.output_set_impulsion("hide_labels")
            self.speak("Labels hidden")
            return "Hidden labels"
        except Exception as e:
            self._update_status(f"Failed to hide labels: {str(e)}")
            return None

    def _handle_show_labels(self):
        """Handle 'show labels' command"""
        try:
            igs.service_call("Whiteboard", "showLabels", "", "")
            igs.output_set_impulsion("show_labels")
            self.speak("Labels shown")
            return "Shown labels"
        except Exception as e:
            self._update_status(f"Failed to show labels: {str(e)}")
            return None

    def _handle_add_image(self):
        """Handle 'add image' command"""
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)

            file_path = filedialog.askopenfilename(
                title="Select an Image",
                filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
            )

            if file_path:
                element_id = add_Image_From_URL(file_path, 100, 100)
                if element_id:
                    self.speak("Image added to the whiteboard.")
                    return f"Image added: {file_path}"
                else:
                    self._update_status("Failed to add image.")
            else:
                self._update_status("No file selected.")
                self.speak("No image was selected.")
        except Exception as e:
            self._update_status(f"Failed to handle 'add image': {e}")
            return None


    def _update_status(self, status):
        """Update system status output"""
        print(f"Status: {status}")
        igs.output_set_string("system_status", status)

    def cleanup(self):
        """Cleanup resources"""
        self.stop_listening()
        self._update_status("Agent shutting down")
        if self.engine:
            self.engine.stop()