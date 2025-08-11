# Madame Leota - Deployment Guide

This guide explains how to deploy the Madame Leota AI Fortune Teller system to your Raspberry Pi.

## Prerequisites

- Raspberry Pi 4 (recommended) with Raspberry Pi OS
- Internet connection for initial setup
- USB microphone
- Speakers or HDMI audio output
- Short-throw projector
- Fortune teller video file

## Deployment Options

### Option 1: Git Clone (Recommended)

1. **On your Raspberry Pi, clone the repository:**
   ```bash
   git clone <your-repository-url> MadameLeota
   cd MadameLeota
   ```

2. **Run the setup script:**
   ```bash
   python3 setup.py
   ```

3. **Test the system:**
   ```bash
   python3 test_system.py
   ```

4. **Run Madame Leota:**
   ```bash
   python3 main.py
   ```

### Option 2: Manual Setup

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv git
   sudo apt install -y libopencv-dev python3-opencv
   sudo apt install -y portaudio19-dev python3-pyaudio
   sudo apt install -y libespeak-ng1 espeak-ng-data
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Raspberry Pi settings:**
   ```bash
   sudo raspi-config
   # Navigate to: Display Options > HDMI > Force HDMI hotplug
   # Navigate to: Performance Options > GPU Memory > 128
   # Navigate to: System Options > Audio > HDMI
   ```

## Configuration

### Video File Setup

1. **Place your fortune teller video in the assets/videos directory:**
   ```bash
   mkdir -p assets/videos
   # Copy your video file to assets/videos/
   ```

2. **Supported video formats:**
   - MP4 (recommended)
   - AVI
   - MOV
   - MKV

### Audio Setup

1. **Test microphone:**
   ```bash
   python3 -c "
   from audio.speech_rec import SpeechRecognizer
   from config import Config
   config = Config()
   rec = SpeechRecognizer(config)
   rec.test_microphone()
   "
   ```

2. **Test speakers:**
   ```bash
   python3 -c "
   from audio.speech_synth import SpeechSynthesizer
   from config import Config
   config = Config()
   synth = SpeechSynthesizer(config)
   synth.test_speech()
   "
   ```

### Display Setup

1. **Test projection:**
   ```bash
   python3 -c "
   from video.projection import ProjectionManager
   from config import Config
   config = Config()
   proj = ProjectionManager(config)
   proj.test_projection()
   "
   ```

## Auto-Start Setup

### Systemd Service

1. **Create service file:**
   ```bash
   sudo nano /etc/systemd/system/madame-leota.service
   ```

2. **Add service content:**
   ```ini
   [Unit]
   Description=Madame Leota AI Fortune Teller
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/MadameLeota
   Environment=PATH=/home/pi/MadameLeota/venv/bin
   ExecStart=/home/pi/MadameLeota/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable madame-leota
   sudo systemctl start madame-leota
   ```

4. **Check service status:**
   ```bash
   sudo systemctl status madame-leota
   ```

### Manual Auto-Start

Add to `/home/pi/.bashrc`:
```bash
# Auto-start Madame Leota
if [ -f /home/pi/MadameLeota/main.py ]; then
    cd /home/pi/MadameLeota
    source venv/bin/activate
    python main.py &
fi
```

## Troubleshooting

### Common Issues

1. **Audio not working:**
   - Check HDMI audio output in raspi-config
   - Test with: `speaker-test -t wav -c 2`

2. **Video not displaying:**
   - Check HDMI connection
   - Verify display resolution in config.py
   - Test with: `tvservice -s`

3. **Speech recognition issues:**
   - Check microphone permissions
   - Test microphone: `arecord -d 5 test.wav`

4. **Performance issues:**
   - Reduce video frame count in animation.py
   - Lower display resolution
   - Close unnecessary applications

### Logs

Check logs in the `logs/` directory:
```bash
tail -f logs/madame_leota.log
```

### System Resources

Monitor system resources:
```bash
htop
free -h
df -h
```

## Updates

To update the system:

1. **Pull latest changes:**
   ```bash
   git pull origin master
   ```

2. **Reinstall dependencies if needed:**
   ```bash
   python3 setup.py
   ```

3. **Restart service:**
   ```bash
   sudo systemctl restart madame-leota
   ```

## Security Notes

- The system runs with user permissions
- No sensitive data is stored
- Consider firewall rules if exposing to network
- Keep system updated regularly

## Support

For issues:
1. Check the logs in `logs/` directory
2. Run `python3 test_system.py` to identify problems
3. Check system resources with `htop`
4. Verify hardware connections

## Next Steps

After successful deployment:
1. Customize Madame Leota's personality in `config.py`
2. Add your own fortune teller video
3. Adjust audio/video settings for your environment
4. Set up auto-start for production use
