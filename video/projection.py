#!/usr/bin/env python3
"""
Projection Manager for Madame Leota
Handles display setup and projection mapping
"""

import logging
import os
import platform
import subprocess
from typing import Optional, Tuple

try:
    import pygame
    import cv2
    import numpy as np
    PYGAME_AVAILABLE = True
    OPENCV_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    OPENCV_AVAILABLE = False

class ProjectionManager:
    """Manages display and projection for Madame Leota"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.screen = None
        self.display_info = None
        self.projection_config = config.get_projection_config()
        self.pi_config = config.get_pi_config()
        
        if PYGAME_AVAILABLE:
            self._initialize_display()
        else:
            self.logger.warning("Pygame not available - projection disabled")
    
    def _initialize_display(self):
        """Initialize the display system"""
        try:
            pygame.init()
            
            # Configure for Raspberry Pi if detected
            if platform.system() == "Linux":
                self._configure_pi_display()
            
            # Get display info
            self.display_info = pygame.display.Info()
            self.logger.info(f"Display: {self.display_info.current_w}x{self.display_info.current_h}")
            
            # Set up display mode
            if self.projection_config["display_mode"] == "fullscreen":
                self.screen = pygame.display.set_mode(
                    (0, 0), 
                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                )
                self.logger.info("✓ Fullscreen display initialized")
            else:
                width = self.projection_config.get("projection_width", 1920)
                height = self.projection_config.get("projection_height", 1080)
                self.screen = pygame.display.set_mode((width, height))
                self.logger.info(f"✓ Windowed display initialized: {width}x{height}")
            
            # Set window title
            pygame.display.set_caption("Madame Leota - Fortune Teller")
            
            # Clear display
            self.clear_display()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize display: {e}")
            self.screen = None
    
    def _configure_pi_display(self):
        """Configure Raspberry Pi specific display settings"""
        try:
            self.logger.info("Configuring Raspberry Pi display...")
            
            # HDMI force hotplug
            if self.pi_config["hdmi_force_hotplug"]:
                subprocess.run([
                    "sudo", "raspi-config", "nonint", "do_hdmi_force_hotplug", "1"
                ], capture_output=True)
            
            # Set HDMI group and mode
            subprocess.run([
                "sudo", "raspi-config", "nonint", "do_hdmi_group", 
                str(self.pi_config["hdmi_group"])
            ], capture_output=True)
            
            subprocess.run([
                "sudo", "raspi-config", "nonint", "do_hdmi_mode", 
                str(self.pi_config["hdmi_mode"])
            ], capture_output=True)
            
            # Set GPU memory split
            subprocess.run([
                "sudo", "raspi-config", "nonint", "do_gpu_mem", 
                str(self.pi_config["gpu_mem"])
            ], capture_output=True)
            
            # Set audio output
            if self.pi_config["audio_output"] == "hdmi":
                subprocess.run([
                    "sudo", "raspi-config", "nonint", "do_audio_out", "2"
                ], capture_output=True)
            else:
                subprocess.run([
                    "sudo", "raspi-config", "nonint", "do_audio_out", "1"
                ], capture_output=True)
            
            self.logger.info("✓ Raspberry Pi display configured")
            
        except Exception as e:
            self.logger.error(f"Failed to configure Pi display: {e}")
    
    def show_video_frame(self, frame):
        """Display a video frame on the projection surface"""
        if not self.screen or not OPENCV_AVAILABLE:
            return False
        
        try:
            # Convert OpenCV frame to Pygame surface
            if len(frame.shape) == 3:
                # BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame
            
            # Convert to Pygame surface
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            
            # Scale to fit display
            display_rect = self.screen.get_rect()
            scaled_surface = pygame.transform.scale(frame_surface, display_rect.size)
            
            # Display frame
            self.screen.blit(scaled_surface, (0, 0))
            pygame.display.flip()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error displaying video frame: {e}")
            return False
    
    def show_image(self, image_path: str):
        """Display an image on the projection surface"""
        if not self.screen:
            return False
        
        try:
            # Load image
            image = pygame.image.load(image_path)
            
            # Scale to fit display
            display_rect = self.screen.get_rect()
            scaled_image = pygame.transform.scale(image, display_rect.size)
            
            # Display image
            self.screen.blit(scaled_image, (0, 0))
            pygame.display.flip()
            
            self.logger.info(f"✓ Image displayed: {image_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error displaying image: {e}")
            return False
    
    def clear_display(self):
        """Clear the display"""
        if not self.screen:
            return False
        
        try:
            # Fill with black
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            
            self.logger.info("✓ Display cleared")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing display: {e}")
            return False
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if not self.screen:
            return False
        
        try:
            current_flags = self.screen.get_flags()
            
            if current_flags & pygame.FULLSCREEN:
                # Switch to windowed
                width = self.projection_config.get("projection_width", 1920)
                height = self.projection_config.get("projection_height", 1080)
                self.screen = pygame.display.set_mode((width, height))
                self.projection_config["display_mode"] = "windowed"
                self.logger.info("✓ Switched to windowed mode")
            else:
                # Switch to fullscreen
                self.screen = pygame.display.set_mode(
                    (0, 0), 
                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                )
                self.projection_config["display_mode"] = "fullscreen"
                self.logger.info("✓ Switched to fullscreen mode")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error toggling fullscreen: {e}")
            return False
    
    def set_display_resolution(self, width: int, height: int):
        """Set display resolution"""
        if not self.screen:
            return False
        
        try:
            if self.projection_config["display_mode"] == "fullscreen":
                self.screen = pygame.display.set_mode(
                    (0, 0), 
                    pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
                )
            else:
                self.screen = pygame.display.set_mode((width, height))
            
            self.projection_config["projection_width"] = width
            self.projection_config["projection_height"] = height
            
            self.logger.info(f"✓ Display resolution set to {width}x{height}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting display resolution: {e}")
            return False
    
    def apply_visual_effects(self, brightness: float = 1.0, contrast: float = 1.0, gamma: float = 1.0):
        """Apply visual effects for projection"""
        if not self.screen:
            return False
        
        try:
            # Get current display surface
            current_surface = self.screen.copy()
            
            # Apply effects using OpenCV if available
            if OPENCV_AVAILABLE:
                # Convert to numpy array
                surface_array = pygame.surfarray.array3d(current_surface)
                
                # Apply brightness and contrast
                surface_array = cv2.convertScaleAbs(
                    surface_array, 
                    alpha=contrast, 
                    beta=(brightness - 1.0) * 255
                )
                
                # Apply gamma correction
                if gamma != 1.0:
                    gamma_table = np.array([
                        ((i / 255.0) ** (1.0 / gamma)) * 255 
                        for i in np.arange(0, 256)
                    ]).astype("uint8")
                    surface_array = cv2.LUT(surface_array, gamma_table)
                
                # Convert back to Pygame surface
                modified_surface = pygame.surfarray.make_surface(surface_array.swapaxes(0, 1))
                
                # Display modified surface
                self.screen.blit(modified_surface, (0, 0))
                pygame.display.flip()
                
                self.logger.info("✓ Visual effects applied")
                return True
            else:
                self.logger.warning("OpenCV not available - visual effects disabled")
                return False
                
        except Exception as e:
            self.logger.error(f"Error applying visual effects: {e}")
            return False
    
    def test_projection(self):
        """Test projection system"""
        if not self.screen:
            return False
        
        try:
            self.logger.info("Testing projection system...")
            
            # Test colors
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
            
            for color in colors:
                self.screen.fill(color)
                pygame.display.flip()
                pygame.time.wait(1000)  # Wait 1 second
            
            # Return to black
            self.clear_display()
            
            self.logger.info("✓ Projection test completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Projection test failed: {e}")
            return False
    
    def get_display_info(self) -> dict:
        """Get current display information"""
        if not self.screen:
            return {}
        
        try:
            return {
                "width": self.screen.get_width(),
                "height": self.screen.get_height(),
                "flags": self.screen.get_flags(),
                "fullscreen": bool(self.screen.get_flags() & pygame.FULLSCREEN),
                "refresh_rate": self.display_info.refresh_rate if self.display_info else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting display info: {e}")
            return {}
    
    def cleanup(self):
        """Clean up projection resources"""
        try:
            if self.screen:
                pygame.display.quit()
                self.logger.info("✓ Projection system cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up projection: {e}")


class FallbackProjectionManager:
    """Fallback projection manager when main system fails"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def show_video_frame(self, frame):
        """Fallback method"""
        self.logger.warning("Using fallback projection manager - no display available")
        return False
    
    def clear_display(self):
        """Fallback method"""
        return False
    
    def test_projection(self):
        """Fallback method"""
        return False
