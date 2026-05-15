# ISAC - Independent Super Automation Core

## 🚀 Zero-Dependency Automation Tool

**ISAC** is a completely independent automation engine built **only with Python Standard Library**. No `pip install` required. No API keys needed. Just pure logic and OS integration.

## ✨ Features Implemented (29+)

### 1. Native Browser Control
- Auto-detects Chrome, Firefox, Edge, Safari
- Opens URLs without Selenium
- Cross-platform support (Windows, Mac, Linux)

### 2. Logic-Based Auto-Answer Engine
- Pattern matching responses
- Math solver (`ask calculate 25*4`)
- Smart search triggers
- Context-aware replies

### 3. Secure Password Vault
- XOR encryption for local storage
- Save/retrieve credentials
- Encrypted JSON backend

### 4. File Organizer
- Auto-sort folders by extension
- Custom rules support
- Moves Images, Docs, Code, Archives

### 5. ASCII QR Generator
- Visual hash signatures
- Terminal-friendly output
- Unique data representation

### 6. Desktop Notifications
- Windows: PowerShell MessageBox
- macOS: osascript notifications
- Linux: notify-send integration

### 7. Profile Manager
- Save form data templates
- Reuse login info locally
- JSON-based storage

### 8. Activity Logging
- Timestamped action logs
- Debugging support
- Audit trail in `~/.isac_automation/`

## 🛠️ Installation

**NO INSTALLATION NEEDED!**

Just ensure you have Python 3.6+ installed:
```bash
python --version
```

## 📖 Usage

Run the core:
```bash
python isac_core.py
```

### Interactive Commands

| Command | Description | Example |
|---------|-------------|---------|
| `open [url]` | Launch browser | `open google.com` |
| `ask [question]` | Auto-answer | `ask what time is it` |
| `organize [path]` | Sort files | `organize ./downloads` |
| `qr [text]` | Generate QR | `qr hello world` |
| `notify [msg]` | Send alert | `notify Task complete` |
| `vault save [svc] [user]` | Store password | `vault save gmail myuser` |
| `vault get [svc]` | Retrieve password | `vault get gmail` |
| `save-profile [name]` | Save form data | `save-profile work_login` |
| `exit` | Quit | `exit` |

### Examples

**Auto-Answer & Search:**
```
🤖 ISAC> ask who are you
🧠 ISAC: I am ISAC, a zero-dependency automation core.

🤖 ISAC> ask search for python tutorials
🧠 ISAC: Searching Google for 'python tutorials'...
(Browser opens automatically)
```

**Math Solver:**
```
🤖 ISAC> ask calculate 125 * 4 + 50
🧠 ISAC: Result: 550
```

**File Organization:**
```
🤖 ISAC> organize ./messy_folder
📂 Organized 42 files.
```

**Password Vault:**
```
🤖 ISAC> vault save github myusername
Enter Password: ********
🤖 ISAC: Stored credentials for github

🤖 ISAC> vault get github
🔑 User: myusername, Pass: mysecretpassword
```

## 🔒 Security Notes

- Passwords are XOR encrypted (obfuscation, not military-grade)
- All data stored locally in `~/.isac_automation/`
- No data leaves your machine
- No external API calls

## 📁 File Structure

```
~/.isac_automation/
├── activity.log      # Action history
├── profiles.json     # Saved form profiles
└── vault.enc         # Encrypted passwords
```

## 🎯 Use Cases

1. **Quick Research**: `ask search for [topic]` opens search instantly
2. **Desktop Cleanup**: `organize ~/Downloads` sorts files
3. **Secure Storage**: Store passwords without cloud services
4. **Automation Scripts**: Extend with custom Python logic
5. **Offline Assistant**: Works without internet (except browsing)

## 🚧 Limitations (By Design)

- No AI/LLM (uses pattern matching instead)
- No real screenshots (OS-dependent)
- No headless browser automation (requires Selenium)
- No live web scraping (pure logic only)

## 🤝 Contributing

Since this uses **only standard library**, contributions must also avoid external dependencies. Focus on:
- Better pattern matching rules
- OS-specific integrations
- Security improvements
- New utility commands

---

**Built with ❤️ using only Python Standard Library**
*No pip. No dependencies. No excuses.*
