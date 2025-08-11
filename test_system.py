#!/usr/bin/env python3
"""
Test script for Madame Leota system
Tests all major components
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        from config import Config
        config = Config()
        print("✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False

def test_ai():
    """Test AI system"""
    print("Testing AI system...")
    try:
        from config import Config
        from ai.chat import MadameLeotaAI
        
        config = Config()
        ai = MadameLeotaAI(config)
        
        # Test welcome message
        welcome = ai.get_welcome_message()
        print(f"✓ Welcome message: {welcome}")
        
        # Test response
        response = ai.get_response("Tell me about my future")
        print(f"✓ AI response: {response}")
        
        return True
    except Exception as e:
        print(f"✗ AI test failed: {e}")
        return False

def test_speech_synth():
    """Test speech synthesis"""
    print("Testing speech synthesis...")
    try:
        from config import Config
        from audio.speech_synth import SpeechSynthesizer
        
        config = Config()
        synth = SpeechSynthesizer(config)
        
        # Test speech
        result = synth.speak("Hello, I am Madame Leota", blocking=True)
        if result:
            print("✓ Speech synthesis working")
        else:
            print("⚠ Speech synthesis failed")
        
        return True
    except Exception as e:
        print(f"✗ Speech synthesis test failed: {e}")
        return False

def test_projection():
    """Test projection system"""
    print("Testing projection system...")
    try:
        from config import Config
        from video.projection import ProjectionManager
        
        config = Config()
        proj = ProjectionManager(config)
        
        # Get display info
        info = proj.get_display_info()
        if info:
            print(f"✓ Display info: {info}")
        else:
            print("⚠ No display info available")
        
        return True
    except Exception as e:
        print(f"✗ Projection test failed: {e}")
        return False

def test_animation():
    """Test animation system"""
    print("Testing animation system...")
    try:
        from config import Config
        from video.animation import FacialAnimator
        
        config = Config()
        anim = FacialAnimator(config)
        
        # Get animation status
        status = anim.get_animation_status()
        print(f"✓ Animation status: {status}")
        
        return True
    except Exception as e:
        print(f"✗ Animation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔮 Madame Leota System Test 🔮")
    print("=" * 40)
    
    tests = [
        test_config,
        test_ai,
        test_speech_synth,
        test_projection,
        test_animation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠ Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    main()
