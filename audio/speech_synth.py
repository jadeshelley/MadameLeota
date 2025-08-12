#!/usr/bin/env python3
"""
Speech Synthesis for Madame Leota
Handles text-to-speech conversion
"""

import logging
import time
import threading
from typing import Optional

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from gtts import gTTS
    import pygame.mixer
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

class SpeechSynthesizer:
    """Speech synthesis system for Madame Leota"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.engine = None
        self.audio_config = config.get_audio_config()
        self._speaking = False
        self.speech_thread = None
        
        if PYTTSX3_AVAILABLE:
            self._initialize_pyttsx3()
        elif GTTS_AVAILABLE:
            self._initialize_gtts()
        else:
            self.logger.warning("No speech synthesis available")
    
    def _initialize_pyttsx3(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice properties
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find a female voice
                female_voice = None
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        female_voice = voice
                        break
                
                if female_voice:
                    self.engine.setProperty('voice', female_voice.id)
                    self.logger.info(f"✓ Using voice: {female_voice.name}")
                else:
                    self.engine.setProperty('voice', voices[0].id)
                    self.logger.info(f"✓ Using voice: {voices[0].name}")
            
            # Set properties
            self.engine.setProperty('rate', int(200 * self.audio_config["voice_speed"]))
            self.engine.setProperty('volume', self.audio_config["voice_volume"])
            
            self.logger.info("✓ pyttsx3 speech synthesis initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3: {e}")
            self.engine = None
    
    def _initialize_gtts(self):
        """Initialize gTTS and pygame mixer"""
        try:
            pygame.mixer.init()
            self.logger.info("✓ gTTS speech synthesis initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize gTTS: {e}")
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """Convert text to speech and play it"""
        if not text:
            return False
        
        try:
            if self.engine and PYTTSX3_AVAILABLE:
                return self._speak_pyttsx3(text, blocking)
            elif GTTS_AVAILABLE:
                return self._speak_gtts(text, blocking)
            else:
                self.logger.warning("No speech synthesis available")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in speech synthesis: {e}")
            return False
    
    def _speak_pyttsx3(self, text: str, blocking: bool) -> bool:
        """Speak using pyttsx3"""
        try:
            if blocking:
                self._speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self._speaking = False
                return True
            else:
                # Non-blocking speech
                self._speaking = True
                
                def speak_thread():
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    finally:
                        self._speaking = False
                
                self.speech_thread = threading.Thread(target=speak_thread, daemon=True)
                self.speech_thread.start()
                return True
                
        except Exception as e:
            self.logger.error(f"pyttsx3 speech error: {e}")
            self._speaking = False
            return False
    
    def _speak_gtts(self, text: str, blocking: bool) -> bool:
        """Speak using gTTS"""
        try:
            # Create temporary audio file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            tts = gTTS(text=text, lang=self.audio_config["language"][:2])
            tts.save(temp_path)
            
            # Play audio
            if blocking:
                self._speaking = True
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                self._speaking = False
                
                # Clean up
                pygame.mixer.music.unload()
                os.unlink(temp_path)
                return True
            else:
                # Non-blocking speech
                self._speaking = True
                
                def play_thread():
                    try:
                        pygame.mixer.music.load(temp_path)
                        pygame.mixer.music.play()
                        
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                        
                        # Clean up
                        pygame.mixer.music.unload()
                        os.unlink(temp_path)
                    finally:
                        self._speaking = False
                
                self.speech_thread = threading.Thread(target=play_thread, daemon=True)
                self.speech_thread.start()
                return True
                
        except Exception as e:
            self.logger.error(f"gTTS speech error: {e}")
            self._speaking = False
            return False
    
    def stop_speech(self):
        """Stop current speech"""
        try:
            if self.engine and PYTTSX3_AVAILABLE:
                self.engine.stop()
            elif GTTS_AVAILABLE:
                pygame.mixer.music.stop()
            
            self._speaking = False
            
            if self.speech_thread and self.speech_thread.is_alive():
                self.speech_thread.join(timeout=1)
            
            self.logger.info("✓ Speech stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping speech: {e}")
    
    def pause_speech(self):
        """Pause current speech"""
        try:
            if GTTS_AVAILABLE:
                pygame.mixer.music.pause()
                self.logger.info("✓ Speech paused")
            else:
                self.logger.warning("Pause not supported with current speech engine")
                
        except Exception as e:
            self.logger.error(f"Error pausing speech: {e}")
    
    def resume_speech(self):
        """Resume paused speech"""
        try:
            if GTTS_AVAILABLE:
                pygame.mixer.music.unpause()
                self.logger.info("✓ Speech resumed")
            else:
                self.logger.warning("Resume not supported with current speech engine")
                
        except Exception as e:
            self.logger.error(f"Error resuming speech: {e}")
    
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self._speaking  # Changed from self.is_speaking to self._speaking
    
    def set_voice_speed(self, speed: float):
        """Set voice speed (0.5 to 2.0)"""
        try:
            if self.engine and PYTTSX3_AVAILABLE:
                self.engine.setProperty('rate', int(200 * speed))
                self.audio_config["voice_speed"] = speed
                self.logger.info(f"✓ Voice speed set to {speed}")
            else:
                self.logger.warning("Voice speed control not available")
                
        except Exception as e:
            self.logger.error(f"Error setting voice speed: {e}")
    
    def set_voice_volume(self, volume: float):
        """Set voice volume (0.0 to 1.0)"""
        try:
            if self.engine and PYTTSX3_AVAILABLE:
                self.engine.setProperty('volume', volume)
                self.audio_config["voice_volume"] = volume
                self.logger.info(f"✓ Voice volume set to {volume}")
            else:
                self.logger.warning("Voice volume control not available")
                
        except Exception as e:
            self.logger.error(f"Error setting voice volume: {e}")
    
    def test_speech(self, text: str = "Hello, I am Madame Leota") -> bool:
        """Test speech synthesis"""
        try:
            self.logger.info("Testing speech synthesis...")
            result = self.speak(text, blocking=True)
            
            if result:
                self.logger.info("✓ Speech synthesis test successful")
            else:
                self.logger.error("✗ Speech synthesis test failed")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Speech synthesis test error: {e}")
            return False


class FallbackSpeechSynthesizer:
    """Fallback speech synthesizer when main system fails"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_speaking = False
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """Fallback method - just prints text"""
        self.logger.warning(f"Fallback speech synthesizer: {text}")
        return True
    
    def stop_speech(self):
        """Fallback method"""
        pass
    
    def is_speaking(self) -> bool:
        """Fallback method"""
        return False
