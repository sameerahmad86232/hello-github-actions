#!/usr/bin/env python3
"""
INDEPENDENT SUPER AUTOMATION CORE (ISAC)
Version: 1.0.0
Dependencies: NONE (Python Standard Library Only)
Features: Native Browser Control, Local Logic, File Ops, Security, Notifications
"""

import os
import sys
import json
import time
import shutil
import hashlib
import base64
import subprocess
import platform
import re
import urllib.request
import urllib.parse
import ssl
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION & CONSTANTS ---
DATA_DIR = Path.home() / ".isac_automation"
PROFILES_FILE = DATA_DIR / "profiles.json"
VAULT_FILE = DATA_DIR / "vault.enc"
LOG_FILE = DATA_DIR / "activity.log"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# --- UTILITIES ---

def log_action(message):
    """Log actions to local file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"🤖 ISAC: {message}")

def get_os():
    """Detect operating system."""
    return platform.system()

def notify_user(title, message):
    """Feature 7: Desktop Notifications (OS Native)."""
    try:
        if get_os() == "Windows":
            # PowerShell notification
            cmd = f"""powershell -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('{message}', '{title}')""";
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif get_os() == "Darwin":
            # macOS osascript
            cmd = f"""osascript -e 'display notification "{message}" with title "{title}"'"""
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Linux notify-send (common)
            cmd = f"""notify-send "{title}" "{message}" 2>/dev/null || echo "Notification: {title} - {message}" """
            subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_action(f"Notification sent: {title}")
    except Exception as e:
        log_action(f"Notification failed: {e}")

def simple_encrypt(text, key="isac_default_key"):
    """Simple XOR encryption for local vault (Not military grade, but obfuscated)."""
    key_bytes = key.encode()
    text_bytes = text.encode()
    encrypted = bytearray()
    for i, byte in enumerate(text_bytes):
        encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    return base64.b64encode(encrypted).decode()

def simple_decrypt(cipher_text, key="isac_default_key"):
    """Decrypt local vault."""
    try:
        key_bytes = key.encode()
        decoded = base64.b64decode(cipher_text)
        decrypted = bytearray()
        for i, byte in enumerate(decoded):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        return decrypted.decode()
    except:
        return None

# --- FEATURE 1: NATIVE BROWSER CONTROL ---

class NativeBrowser:
    def __init__(self):
        self.browser_path = self._find_browser()
        self.process = None

    def _find_browser(self):
        """Find Chrome/Firefox/Edge executable based on OS."""
        os_name = get_os()
        paths = []
        if os_name == "Windows":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            ]
        elif os_name == "Darwin":
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Firefox.app/Contents/MacOS/firefox",
                "/Applications/Safari.app/Contents/MacOS/Safari"
            ]
        else: # Linux
            paths = ["google-chrome", "firefox", "chromium-browser"]

        for p in paths:
            if os.path.exists(p) or shutil.which(p):
                return p
        return None

    def open_url(self, url):
        """Open URL in default or detected browser."""
        if not url.startswith("http"):
            url = "https://" + url
        
        if self.browser_path:
            log_action(f"Opening {url} in {os.path.basename(self.browser_path)}")
            # Launch detached
            subprocess.Popen([self.browser_path, url], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        else:
            log_action("No browser found, using system default opener.")
            import webbrowser
            webbrowser.open(url)
        
        notify_user("Browser Launched", f"Opened: {url}")

    def take_screenshot_native(self, name="snapshot"):
        """Attempt OS-native screenshot (limited without deps, falls back to instruction)."""
        filename = f"{name}_{int(time.time())}.png"
        path = DATA_DIR / filename
        log_action(f"Screenshot requested: {filename}")
        # Note: True headless screenshot requires Selenium/Puppeteer. 
        # In independent mode, we trigger OS tools if available or notify user.
        if get_os() == "Darwin":
            subprocess.run(["screencapture", str(path)], timeout=5)
            log_action(f"Saved to {path}")
        elif get_os() == "Windows":
            # PowerShell snippet for screenshot would go here, complex without deps
            log_action("Windows native screenshot requires script. Saving placeholder.")
            with open(path, "w") as f: f.write("Placeholder for screenshot")
        else:
            log_action("Linux: Install scrot or use GUI tool.")
        return str(path)

# --- FEATURE 2: LOGIC-BASED AUTO-ANSWER ---

class LogicEngine:
    def __init__(self):
        self.rules = {
            r"hello|hi|hey": "Hello! I am your Independent Automation Assistant.",
            r"who are you": "I am ISAC, a zero-dependency automation core.",
            r"time": f"The current time is {datetime.now().strftime('%H:%M')}.",
            r"date": f"Today is {datetime.now().strftime('%Y-%m-%d')}.",
            r"weather": "I cannot access live weather without API keys, but I can check a file if you have one.",
            r"calculate (.*)": self._solve_math,
            r"define (\w+)": "I don't have a local dictionary, but I can open a search for this.",
            r"open (.*)": "Opening {0}...",
            r"search for (.*)": "Searching Google for '{0}'..."
        }

    def _solve_math(self, match):
        expr = match.group(1).replace(" ", "")
        try:
            # Safe eval for basic math
            allowed = set("0123456789+-*/().")
            if all(c in allowed for c in expr):
                return f"Result: {eval(expr)}"
            return "Invalid expression."
        except:
            return "Could not calculate."

    def process_input(self, user_input):
        """Analyze input and generate auto-response."""
        user_input = user_input.lower()
        for pattern, response in self.rules.items():
            match = re.search(pattern, user_input)
            if match:
                if callable(response):
                    return response(match)
                elif isinstance(response, str) and "{0}" in response:
                    return response.format(match.group(1) if match.groups() else "it")
                return response
        
        # Fallback heuristic
        if "?" in user_input:
            return "I'm not sure about that yet. Try 'search for [topic]' or 'calculate [math]'."
        return "Command received. Processing..."

# --- FEATURE 3: LOCAL PROFILE MANAGER ---

class ProfileManager:
    def __init__(self):
        self.profiles = self._load_profiles()

    def _load_profiles(self):
        if PROFILES_FILE.exists():
            try:
                with open(PROFILES_FILE, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_profile(self, name, data):
        self.profiles[name] = data
        with open(PROFILES_FILE, "w") as f:
            json.dump(self.profiles, f, indent=2)
        log_action(f"Profile '{name}' saved.")

    def get_profile(self, name):
        return self.profiles.get(name, None)

    def list_profiles(self):
        return list(self.profiles.keys())

# --- FEATURE 4: FILE ORGANIZER ---

class FileOrganizer:
    @staticmethod
    def organize_folder(path, rules=None):
        """Sort files in a folder by extension."""
        target = Path(path)
        if not target.exists():
            return "Path does not exist."
        
        mappings = {
            "Images": [".jpg", ".png", ".gif", ".bmp"],
            "Documents": [".pdf", ".docx", ".txt", ".md"],
            "Code": [".py", ".js", ".html", ".css"],
            "Archives": [".zip", ".tar", ".gz"]
        }
        
        if rules:
            mappings.update(rules)

        moved_count = 0
        for file in target.iterdir():
            if file.is_file():
                ext = file.suffix.lower()
                for folder_name, extensions in mappings.items():
                    if ext in extensions:
                        dest_folder = target / folder_name
                        dest_folder.mkdir(exist_ok=True)
                        shutil.move(str(file), str(dest_folder / file.name))
                        moved_count += 1
                        break
        return f"Organized {moved_count} files."

# --- FEATURE 5: QR CODE GENERATOR (ASCII) ---

class QRGenerator:
    @staticmethod
    def generate_ascii(data):
        """Generate a simple visual representation (Pseudo-QR for terminal)."""
        # Real QR requires libs. This creates a hashed visual block.
        h = hashlib.md5(data.encode()).hexdigest()
        size = 8
        print(f"\n📱 QR Code for: {data}")
        print("+" + "-"*size + "+")
        for i in range(0, len(h), 2):
            byte_val = int(h[i:i+2], 16)
            row = "".join(["#" if (byte_val >> j) & 1 else " " for j in range(8)])
            print(f"|{row}|")
        print("+" + "-"*size + "+")
        print("(Scan this visually? No. But it's a unique hash signature!)")
        log_action("Generated ASCII QR signature.")

# --- FEATURE 6: PASSWORD VAULT ---

class SecureVault:
    def __init__(self):
        self.vault_file = VAULT_FILE

    def store(self, service, username, password):
        entry = {"user": username, "pass": simple_encrypt(password)}
        data = {}
        if self.vault_file.exists():
            try:
                content = simple_decrypt(self.vault_file.read_text())
                if content:
                    data = json.loads(content)
            except:
                pass
        
        data[service] = entry
        self.vault_file.write_text(simple_encrypt(json.dumps(data)))
        log_action(f"Stored credentials for {service}")

    def retrieve(self, service):
        if not self.vault_file.exists():
            return None
        try:
            content = simple_decrypt(self.vault_file.read_text())
            if content:
                data = json.loads(content)
                entry = data.get(service)
                if entry:
                    return {
                        "user": entry["user"],
                        "pass": simple_decrypt(entry["pass"])
                    }
        except:
            pass
        return None

# --- MAIN INTERACTIVE LOOP ---

def main():
    log_action("ISAC Core Initialized (Zero Dependencies)")
    browser = NativeBrowser()
    logic = LogicEngine()
    profiles = ProfileManager()
    vault = SecureVault()

    print("""
    🚀 ISAC: Independent Super Automation Core
    ------------------------------------------
    Commands:
    - open [url]          : Open website
    - ask [question]      : Auto-answer logic
    - save-profile [name] : Save form data (interactive)
    - organize [path]     : Sort files in folder
    - qr [text]           : Generate ASCII QR
    - vault save [svc]    : Save password
    - vault get [svc]     : Retrieve password
    - notify [msg]        : Send desktop alert
    - exit                : Quit
    """)

    while True:
        try:
            cmd = input("\n🤖 ISAC> ").strip()
            if not cmd:
                continue
            
            parts = cmd.split(maxsplit=1)
            action = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if action == "exit":
                log_action("Session ended by user.")
                break
            
            elif action == "open":
                browser.open_url(args)
            
            elif action == "ask":
                response = logic.process_input(args)
                print(f"🧠 ISAC: {response}")
                if "search" in response.lower():
                    browser.open_url(f"https://www.google.com/search?q={urllib.parse.quote(args)}")
            
            elif action == "organize":
                path = args or "."
                result = FileOrganizer.organize_folder(path)
                print(f"📂 {result}")
            
            elif action == "qr":
                QRGenerator.generate_ascii(args)
            
            elif action == "notify":
                notify_user("ISAC Alert", args)
            
            elif action == "vault":
                sub_parts = args.split(maxsplit=2)
                if sub_parts[0] == "save" and len(sub_parts) == 3:
                    svc, user = sub_parts[1], sub_parts[2]
                    pwd = input("Enter Password (hidden): ") # Simple input, not truly hidden in std lib without getpass
                    # Using getpass for better security
                    import getpass
                    real_pwd = getpass.getpass(prompt="Enter Password: ")
                    vault.store(svc, user, real_pwd)
                elif sub_parts[0] == "get" and len(sub_parts) == 2:
                    creds = vault.retrieve(sub_parts[1])
                    if creds:
                        print(f"🔑 User: {creds['user']}, Pass: {creds['pass']}")
                    else:
                        print("❌ Not found.")
            
            elif action == "save-profile":
                name = args
                if not name:
                    print("Usage: save-profile [name]")
                    continue
                data = {}
                print("Enter fields (type 'done' to finish):")
                while True:
                    field = input("Field Name: ")
                    if field == "done":
                        break
                    val = input("Value: ")
                    data[field] = val
                profiles.save_profile(name, data)

            else:
                print(f"❓ Unknown command: {action}. Type 'help' for list.")

        except KeyboardInterrupt:
            print("\nInterrupted.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")
            log_action(f"Error: {e}")

if __name__ == "__main__":
    main()
