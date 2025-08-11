#!/usr/bin/env python3
"""
Madame Leota - AI Fortune Teller
Main application entry point
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
try:
    from ai.chat import MadameLeotaAI
    from audio.speech_rec import SpeechRecognizer
    from audio.speech_synth import SpeechSynthesizer
    from video.projection import ProjectionManager
    from video.animation import FacialAnimator
    from config import Config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run 'python setup.py' first to install dependencies")
    sys.exit(1)

class MadameLeotaFortuneTeller:
    """Main fortune teller application"""
    
    def __init__(self):
        self.config = Config()
        self.ai = None
        self.speech_rec = None
        self.speech_synth = None
        self.projection = None
        self.animator = None
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/madame_leota.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_components(self):
        """Initialize all system components"""
        try:
            self.logger.info("Initializing Madame Leota system...")
            
            # Initialize AI
            self.ai = MadameLeotaAI(self.config)
            self.logger.info("✓ AI system initialized")
            
            # Initialize speech recognition
            self.speech_rec = SpeechRecognizer(self.config)
            self.logger.info("✓ Speech recognition initialized")
            
            # Initialize speech synthesis
            self.speech_synth = SpeechSynthesizer(self.config)
            self.logger.info("✓ Speech synthesis initialized")
            
            # Initialize projection system
            self.projection = ProjectionManager(self.config)
            self.logger.info("✓ Projection system initialized")
            
            # Initialize facial animation
            self.animator = FacialAnimator(self.config)
            self.logger.info("✓ Facial animation initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False
    
    def start_session(self):
        """Start a new fortune telling session"""
        self.logger.info("Starting new fortune telling session...")
        
        # Welcome message
        welcome_msg = self.ai.get_welcome_message()
        self.logger.info(f"Welcome message: {welcome_msg}")
        
        # Speak and animate welcome
        self.speak_and_animate(welcome_msg)
        
        self.running = True
        self.logger.info("Session started successfully")
    
    def conversation_loop(self):
        """Main conversation loop"""
        self.logger.info("Entering conversation loop...")
        
        while self.running:
            try:
                # Listen for user input
                self.logger.info("Listening for user input...")
                user_input = self.speech_rec.listen_for_speech()
                
                if user_input:
                    self.logger.info(f"User said: {user_input}")
                    
                    # Generate AI response
                    response = self.ai.get_response(user_input)
                    self.logger.info(f"AI response: {response}")
                    
                    # Speak and animate response
                    self.speak_and_animate(response)
                    
                    # Check for exit commands
                    if any(word in user_input.lower() for word in ['goodbye', 'bye', 'exit', 'quit', 'stop']):
                        self.logger.info("User requested to end session")
                        break
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in conversation loop: {e}")
                break
    
    def speak_and_animate(self, text):
        """Speak text while animating facial expressions"""
        try:
            # Start speech synthesis
            self.speech_synth.speak(text, blocking=False)
            
            # Start facial animation
            self.animator.animate_speech(len(text) * 0.1)  # Rough timing estimate
            
            # Wait for speech to complete
            while self.speech_synth.is_speaking():
                time.sleep(0.1)
            
            # Stop animation
            self.animator.stop_animation()
            
        except Exception as e:
            self.logger.error(f"Error in speak_and_animate: {e}")
    
    def end_session(self):
        """End the current session"""
        self.logger.info("Ending fortune telling session...")
        
        # Farewell message
        farewell_msg = self.ai.get_farewell_message()
        self.logger.info(f"Farewell message: {farewell_msg}")
        
        # Speak and animate farewell
        self.speak_and_animate(farewell_msg)
        
        self.running = False
        self.logger.info("Session ended")
    
    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up resources...")
        
        if self.speech_synth:
            self.speech_synth.stop_speech()
        
        if self.projection:
            self.projection.clear_display()
        
        self.logger.info("Cleanup completed")
    
    def run(self):
        """Main run method"""
        try:
            if not self.initialize_components():
                self.logger.error("Failed to initialize components")
                return False
            
            self.start_session()
            self.conversation_loop()
            self.end_session()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error in main run loop: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    print("🔮 Madame Leota - AI Fortune Teller 🔮")
    print("=" * 40)
    
    fortune_teller = MadameLeotaFortuneTeller()
    
    try:
        success = fortune_teller.run()
        if success:
            print("\n✨ Fortune telling session completed successfully! ✨")
        else:
            print("\n❌ Session ended with errors. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Madame Leota bids you farewell...")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("Check logs for more details.")

if __name__ == "__main__":
    main()
