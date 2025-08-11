#!/usr/bin/env python3
"""
Speech Recognition for Madame Leota
Handles listening to user input
"""

import logging
import time
from typing import Optional

try:
    import speech_recognition as sr
    SPEECH_REC_AVAILABLE = True
except ImportError:
    SPEECH_REC_AVAILABLE = False

class SpeechRecognizer:
    """Speech recognition system for Madame Leota"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.recognizer = None
        self.microphone = None
        self.audio_config = config.get_audio_config()
        
        if SPEECH_REC_AVAILABLE:
            self._initialize_speech_recognition()
        else:
            self.logger.warning("Speech recognition not available")
    
    def _initialize_speech_recognition(self):
        """Initialize speech recognition components"""
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Get microphone
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("✓ Speech recognition initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize speech recognition: {e}")
    
    def listen_for_speech(self, timeout: int = 5) -> Optional[str]:
        """Listen for speech input and return transcribed text"""
        if not self.recognizer or not self.microphone:
            self.logger.warning("Speech recognition not available")
            return None
        
        try:
            self.logger.info("Listening for speech...")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout)
            
            self.logger.info("Audio captured, transcribing...")
            text = self._transcribe_audio(audio)
            
            if text:
                self.logger.info(f"Transcribed: {text}")
                return text
            else:
                self.logger.info("No speech detected")
                return None
                
        except sr.WaitTimeoutError:
            self.logger.info("No speech detected within timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {e}")
            return None
    
    def _transcribe_audio(self, audio) -> Optional[str]:
        """Transcribe audio to text"""
        try:
            # Try Google Speech Recognition first
            text = self.recognizer.recognize_google(
                audio,
                language=self.audio_config["language"]
            )
            return text
            
        except sr.UnknownValueError:
            self.logger.info("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.warning(f"Google Speech Recognition service error: {e}")
            
            # Fallback to Sphinx (offline)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except Exception as sphinx_error:
                self.logger.error(f"Sphinx recognition failed: {sphinx_error}")
                return None
    
    def start_continuous_listening(self, callback):
        """Start continuous listening for speech"""
        if not self.recognizer or not self.microphone:
            self.logger.warning("Speech recognition not available")
            return False
        
        try:
            self.logger.info("Starting continuous listening...")
            
            def listen_loop():
                while True:
                    try:
                        with self.microphone as source:
                            audio = self.recognizer.listen(source)
                        
                        text = self._transcribe_audio(audio)
                        if text:
                            callback(text)
                            
                    except Exception as e:
                        self.logger.error(f"Error in continuous listening: {e}")
                        time.sleep(1)
            
            # Start in background thread
            import threading
            thread = threading.Thread(target=listen_loop, daemon=True)
            thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start continuous listening: {e}")
            return False
    
    def adjust_for_noise(self):
        """Adjust microphone for ambient noise"""
        if not self.recognizer or not self.microphone:
            return False
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self.logger.info("✓ Microphone adjusted for ambient noise")
            return True
        except Exception as e:
            self.logger.error(f"Failed to adjust for noise: {e}")
            return False
    
    def get_available_microphones(self):
        """Get list of available microphones"""
        try:
            return sr.Microphone.list_microphone_names()
        except Exception as e:
            self.logger.error(f"Failed to get microphone list: {e}")
            return []
    
    def test_microphone(self):
        """Test microphone functionality"""
        if not self.recognizer or not self.microphone:
            return False
        
        try:
            self.logger.info("Testing microphone...")
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("✓ Microphone test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False


class FallbackSpeechRecognizer:
    """Fallback speech recognizer when main system fails"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def listen_for_speech(self, timeout: int = 5) -> Optional[str]:
        """Fallback method - returns None"""
        self.logger.warning("Using fallback speech recognizer - no speech input available")
        return None
    
    def test_microphone(self):
        """Test method - always returns False"""
        return False
