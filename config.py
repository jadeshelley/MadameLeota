#!/usr/bin/env python3
"""
Configuration settings for Madame Leota AI Fortune Teller
"""

import os
from pathlib import Path

class Config:
    """Configuration class for Madame Leota"""
    
    def __init__(self):
        # Project paths
        self.PROJECT_ROOT = Path(__file__).parent
        self.ASSETS_DIR = self.PROJECT_ROOT / "assets"
        self.VIDEOS_DIR = self.ASSETS_DIR / "videos"
        self.AUDIO_DIR = self.ASSETS_DIR / "audio"
        self.MODELS_DIR = self.PROJECT_ROOT / "models"
        self.LOGS_DIR = self.PROJECT_ROOT / "logs"
        
        # Create directories if they don't exist
        for directory in [self.ASSETS_DIR, self.VIDEOS_DIR, self.AUDIO_DIR, 
                         self.MODELS_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # AI Configuration
        self.AI_CONFIG = {
            "model_type": "local",  # "local" or "api"
            "local_model": "llama-2-7b-chat.gguf",
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "max_tokens": 150,
            "temperature": 0.8,
            "top_p": 0.9
        }
        
        # Madame Leota Personality
        self.MADAME_LEOTA_PERSONALITY = {
            "name": "Madame Leota",
            "style": "mystical fortune teller",
            "tone": "mysterious, wise, slightly dramatic",
            "greetings": [
                "Welcome, seeker of the unknown... I am Madame Leota, and I sense you have questions about your future.",
                "Ah, the crystal ball reveals a visitor... Come closer, let me read your destiny.",
                "Greetings, child of fate... I am Madame Leota, and I shall peer into the mists of time for you."
            ],
            "farewells": [
                "The mists are clearing... Your fortune has been revealed. Return when you seek more answers.",
                "The crystal ball grows dim... Your destiny awaits. Farewell, seeker of truth.",
                "The spirits bid you farewell... Remember, the future is not set in stone. Goodbye, dear one."
            ],
            "fortune_templates": {
                "love": "I see love in your future... {details}",
                "career": "The stars align for your career... {details}",
                "wealth": "Fortune smiles upon your financial path... {details}",
                "general": "The crystal ball shows... {details}"
            }
        }
        
        # Audio Configuration
        self.AUDIO_CONFIG = {
            "sample_rate": 16000,
            "chunk_size": 1024,
            "channels": 1,
            "format": "int16",
            "language": "en-US",
            "voice_speed": 0.9,
            "voice_volume": 0.8
        }
        
        # Video Configuration
        self.VIDEO_CONFIG = {
            "projection_width": 1920,
            "projection_height": 1080,
            "fps": 30,
            "video_loop": True,
            "animation_smoothness": 0.8,
            "face_detection": True,
            "overlay_opacity": 0.9
        }
        
        # Projection Configuration
        self.PROJECTION_CONFIG = {
            "display_mode": "fullscreen",  # "fullscreen" or "windowed"
            "aspect_ratio": "16:9",
            "brightness": 1.0,
            "contrast": 1.0,
            "gamma": 1.0
        }
        
        # System Configuration
        self.SYSTEM_CONFIG = {
            "debug_mode": False,
            "log_level": "INFO",
            "auto_start": False,
            "idle_timeout": 300,  # 5 minutes
            "max_session_time": 1800,  # 30 minutes
            "save_conversations": True,
            "conversation_log": self.LOGS_DIR / "conversations.log"
        }
        
        # Raspberry Pi specific optimizations
        self.PI_CONFIG = {
            "cpu_throttle_temp": 80,  # Celsius
            "gpu_mem": 128,  # MB
            "overclock": False,
            "hdmi_force_hotplug": True,
            "hdmi_group": 1,  # CEA
            "hdmi_mode": 16,  # 1080p 60Hz
            "audio_output": "hdmi"  # "hdmi" or "analog"
        }
    
    def get_ai_config(self):
        """Get AI configuration"""
        return self.AI_CONFIG
    
    def get_personality(self):
        """Get Madame Leota's personality settings"""
        return self.MADAME_LEOTA_PERSONALITY
    
    def get_audio_config(self):
        """Get audio configuration"""
        return self.AUDIO_CONFIG
    
    def get_video_config(self):
        """Get video configuration"""
        return self.VIDEO_CONFIG
    
    def get_projection_config(self):
        """Get projection configuration"""
        return self.PROJECTION_CONFIG
    
    def get_system_config(self):
        """Get system configuration"""
        return self.SYSTEM_CONFIG
    
    def get_pi_config(self):
        """Get Raspberry Pi specific configuration"""
        return self.PI_CONFIG
    
    def update_config(self, section, key, value):
        """Update a configuration value"""
        if hasattr(self, section.upper() + "_CONFIG"):
            config_dict = getattr(self, section.upper() + "_CONFIG")
            if key in config_dict:
                config_dict[key] = value
                return True
        return False
