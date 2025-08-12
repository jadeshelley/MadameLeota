#!/usr/bin/env python3
"""
Facial Animation for Madame Leota
Handles video-based facial animation and effects
"""

import logging
import time
import threading
from typing import Optional, List
from pathlib import Path

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

class FacialAnimator:
    """Handles facial animation for Madame Leota"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.video_config = config.get_video_config()
        self.video_capture = None
        self.video_frames = []
        self.current_frame = 0
        self.animation_running = False
        self.animation_thread = None
        self.video_path = None
        
        # Load default video if available
        self._load_default_video()
    
    def _load_default_video(self):
        """Load default fortune teller video"""
        try:
            # Look for video files in assets/videos directory
            videos_dir = self.config.VIDEOS_DIR
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
            
            for ext in video_extensions:
                video_files = list(videos_dir.glob(f'*{ext}'))
                if video_files:
                    self.load_video(str(video_files[0]))
                    self.logger.info(f"✓ Loaded default video: {video_files[0].name}")
                    break
            else:
                self.logger.info("No default video found - animation will be disabled")
                
        except Exception as e:
            self.logger.error(f"Error loading default video: {e}")
    
    def load_video(self, video_path: str) -> bool:
        """Load a video file for animation"""
        try:
            if not OPENCV_AVAILABLE:
                self.logger.warning("OpenCV not available - video loading disabled")
                return False
            
            # Close existing video
            if self.video_capture:
                self.video_capture.release()
            
            # Load new video
            self.video_capture = cv2.VideoCapture(video_path)
            
            if not self.video_capture.isOpened():
                self.logger.error(f"Failed to open video: {video_path}")
                return False
            
            self.video_path = video_path
            self.logger.info(f"✓ Video loaded: {video_path}")
            
            # Pre-load frames for smoother animation (especially on Pi)
            self._load_video_frames()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading video: {e}")
            return False
    
    def _load_video_frames(self):
        """Pre-load video frames into memory for smoother animation"""
        try:
            if not self.video_capture:
                return
            
            self.logger.info("Pre-loading video frames...")
            self.video_frames = []
            
            frame_count = 0
            while True:
                ret, frame = self.video_capture.read()
                if not ret:
                    break
                
                self.video_frames.append(frame)
                frame_count += 1
                
                # Limit memory usage on Pi
                if frame_count > 300:  # About 10 seconds at 30fps
                    self.logger.warning("Video too long - only loading first 300 frames")
                    break
            
            self.logger.info(f"✓ Loaded {len(self.video_frames)} frames")
            
            # Reset video capture to beginning
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
        except Exception as e:
            self.logger.error(f"Error pre-loading frames: {e}")
            self.video_frames = []
    
    def animate_speech(self, duration: float):
        """Animate facial expressions during speech"""
        if not self.video_frames:
            self.logger.warning("No video frames available for animation")
            return False
        
        try:
            if self.animation_running:
                self.stop_animation()
            
            self.animation_running = True
            self.current_frame = 0
            
            # Calculate frame rate
            fps = self.video_config.get("fps", 30)
            frame_delay = 1.0 / fps
            
            # Calculate total frames needed
            total_frames = int(duration * fps)
            
            def animation_loop():
                try:
                    frame_count = 0
                    while self.animation_running and frame_count < total_frames:
                        if self.video_frames:
                            # Get current frame
                            frame = self.video_frames[self.current_frame % len(self.video_frames)]
                            
                            # Apply face overlay if enabled
                            if self.video_config.get("face_detection", True):
                                frame = self.apply_face_overlay(frame)
                            
                            # Display frame
                            if hasattr(self, 'projection_manager'):
                                self.projection_manager.show_video_frame(frame)
                            
                            # Move to next frame
                            self.current_frame += 1
                            frame_count += 1
                            
                            # Wait for next frame
                            time.sleep(frame_delay)
                        else:
                            break
                    
                    # Stop animation when done
                    self.animation_running = False
                    
                except Exception as e:
                    self.logger.error(f"Error in animation loop: {e}")
                    self.animation_running = False
            
            # Start animation in background thread
            self.animation_thread = threading.Thread(target=animation_loop, daemon=True)
            self.animation_thread.start()
            
            self.logger.info(f"✓ Animation started for {duration:.2f} seconds")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting animation: {e}")
            self.animation_running = False
            return False
    
    def stop_animation(self):
        """Stop current animation"""
        try:
            self.animation_running = False
            
            if self.animation_thread and self.animation_thread.is_alive():
                self.animation_thread.join(timeout=1)
            
            self.logger.info("✓ Animation stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping animation: {e}")
    
    def apply_face_overlay(self, frame):
        """Apply face overlay effects"""
        try:
            if not self.video_config.get("face_detection", True):
                return frame
            
            # Try to detect face region
            face_region = self._detect_face_region(frame)
            
            if face_region:
                # Apply mystical effects to face region
                frame = self._apply_mystical_effects(frame, face_region)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error applying face overlay: {e}")
            return frame
    
    def _detect_face_region(self, frame):
        """Detect face region in frame"""
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                # Convert numpy array to list and find largest face
                faces_list = faces.tolist()
                largest_face = max(faces_list, key=lambda x: x[2] * x[3])
                return largest_face
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting face: {e}")
            return None
    
    def _apply_mystical_effects(self, frame, face_region):
        """Apply mystical effects to face region"""
        try:
            x, y, w, h = face_region
            
            # Create mystical overlay
            overlay = self._create_mystical_overlay(w, h)
            
            # Blend overlay with face region
            frame = self._blend_frames(frame, overlay, x, y)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error applying mystical effects: {e}")
            return frame
    
    def _create_mystical_overlay(self, width: int, height: int):
        """Create mystical visual effects overlay"""
        try:
            # Create a colorful, mystical overlay
            overlay = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add some mystical colors and patterns
            for i in range(height):
                for j in range(width):
                    # Create rainbow-like effect
                    hue = (i + j) % 360
                    saturation = 100
                    value = 100
                    
                    # Convert HSV to BGR
                    hsv = np.array([[[hue, saturation, value]]], dtype=np.uint8)
                    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                    
                    overlay[i, j] = bgr[0, 0]
            
            # Apply some transparency
            overlay = cv2.addWeighted(overlay, 0.3, np.zeros_like(overlay), 0.7, 0)
            
            return overlay
            
        except Exception as e:
            self.logger.error(f"Error creating mystical overlay: {e}")
            return np.zeros((height, width, 3), dtype=np.uint8)
    
    def _blend_frames(self, base_frame, overlay, x: int, y: int):
        """Blend overlay frame with base frame"""
        try:
            # Get dimensions
            h, w = overlay.shape[:2]
            frame_h, frame_w = base_frame.shape[:2]
            
            # Ensure overlay fits within frame bounds
            if x + w > frame_w:
                w = frame_w - x
            if y + h > frame_h:
                h = frame_h - y
            
            if w <= 0 or h <= 0:
                return base_frame
            
            # Crop overlay to fit
            overlay_cropped = overlay[:h, :w]
            
            # Blend using alpha blending
            alpha = self.video_config.get("overlay_opacity", 0.9)
            beta = 1.0 - alpha
            
            base_frame[y:y+h, x:x+w] = cv2.addWeighted(
                base_frame[y:y+h, x:x+w], beta,
                overlay_cropped, alpha, 0
            )
            
            return base_frame
            
        except Exception as e:
            self.logger.error(f"Error blending frames: {e}")
            return base_frame
    
    def create_mystical_effects(self, frame):
        """Create general mystical effects for the entire frame"""
        try:
            if not OPENCV_AVAILABLE:
                return frame
            
            # Apply some mystical color effects
            frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Enhance saturation
            frame_hsv[:, :, 1] = cv2.multiply(frame_hsv[:, :, 1], 1.2)
            
            # Add slight purple tint
            frame_hsv[:, :, 0] = cv2.add(frame_hsv[:, :, 0], 10)
            
            # Convert back to BGR
            frame_mystical = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)
            
            # Blend with original frame
            alpha = 0.7
            frame = cv2.addWeighted(frame, 1-alpha, frame_mystical, alpha, 0)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error creating mystical effects: {e}")
            return frame
    
    def get_animation_status(self) -> dict:
        """Get current animation status"""
        return {
            "running": self.animation_running,
            "current_frame": self.current_frame,
            "total_frames": len(self.video_frames),
            "video_loaded": self.video_capture is not None,
            "video_path": self.video_path
        }
    
    def test_animation(self) -> bool:
        """Test animation system"""
        try:
            if not self.video_frames:
                self.logger.warning("No video frames available for testing")
                return False
            
            self.logger.info("Testing animation system...")
            
            # Test with a short animation
            success = self.animate_speech(2.0)  # 2 seconds
            
            if success:
                # Wait for animation to complete
                time.sleep(2.5)
                self.logger.info("✓ Animation test completed")
                return True
            else:
                self.logger.error("✗ Animation test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Animation test error: {e}")
            return False
    
    def cleanup(self):
        """Clean up animation resources"""
        try:
            self.stop_animation()
            
            if self.video_capture:
                self.video_capture.release()
            
            self.video_frames.clear()
            self.logger.info("✓ Animation system cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up animation: {e}")


class FallbackFacialAnimator:
    """Fallback facial animator when main system fails"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def animate_speech(self, duration: float):
        """Fallback method"""
        self.logger.warning("Using fallback facial animator - no animation available")
        return False
    
    def stop_animation(self):
        """Fallback method"""
        pass
    
    def get_animation_status(self) -> dict:
        """Fallback method"""
        return {
            "running": False,
            "current_frame": 0,
            "total_frames": 0,
            "video_loaded": False,
            "video_path": None
        }
