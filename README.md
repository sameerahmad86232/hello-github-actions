# Browser Automation Tool

A powerful browser automation tool that automates user tasks via natural language prompts. Built with Python and Selenium, it allows you to control a web browser using simple English commands.

## Features

- **Natural Language Processing**: Understands commands like "go to google.com", "click login", "fill username with john"
- **Interactive Mode**: Real-time command execution with immediate feedback
- **Batch Mode**: Execute multiple commands from command line or file
- **Headless Support**: Run without visible browser for automation scripts
- **Multiple Browsers**: Supports Chrome and Firefox
- **Screenshot Capability**: Capture pages during automation
- **Smart Element Detection**: Tries multiple selector strategies automatically

## Installation

### Prerequisites

- Python 3.8+
- pip package manager
- Chrome or Firefox browser (optional, will use headless mode)

### Install Dependencies

```bash
pip install selenium
```

## Usage

### Interactive Mode

Run the tool in interactive mode to enter commands one by one:

```bash
python browser_automation.py
```

Example session:
```
🌐 Browser Automation Tool - Interactive Mode
============================================================

Available commands:
  - 'go to <url>' - Navigate to a website
  - 'click <element>' - Click on an element
  - 'fill <field> with <text>' - Fill a form field
  - 'search for <query>' - Search on Google
  - 'take screenshot' - Capture current page
  - 'scroll to <element>' - Scroll to an element
  - 'wait for <element>' - Wait for element to appear
  - 'get text from <element>' - Extract text
  - 'quit' or 'exit' - Close browser and exit
  - 'help' - Show this help message
============================================================

🤖 Enter command: go to google.com
✓ Navigated to: https://google.com

🤖 Enter command: search for python tutorial
✓ Navigated to: https://www.google.com/search?q=python+tutorial

🤖 Enter command: take screenshot
✓ Screenshot saved: screenshot_1234567890.png

🤖 Enter command: quit
👋 Closing browser...
```

### Batch Mode (Command Line)

Execute multiple commands directly from the command line:

```bash
python browser_automation.py --commands "go to google.com" "search for python" "take screenshot"
```

### Batch Mode (From File)

Create a file with one command per line:

```bash
# commands.txt
go to github.com
search for python projects
take screenshot
```

Then run:

```bash
python browser_automation.py --file commands.txt
```

### Visible Browser Mode

To see the browser window during automation:

```bash
python browser_automation.py --no-headless
```

Or with commands:

```bash
python browser_automation.py --no-headless --commands "go to example.com" "take screenshot"
```

## Supported Commands

### Navigation
- `go to <url>` - Navigate to a website
- `navigate to <url>` - Navigate to a website
- `open <url>` - Open a website
- `visit <url>` - Visit a website
- `browse <url>` - Browse to a website

### Interaction
- `click <element>` - Click on an element
- `click on <element>` - Click on an element
- `press <element>` - Press a button
- `tap <element>` - Tap an element (mobile-like)

### Form Filling
- `fill <field> with <text>` - Fill a form field
- `enter <text> into <field>` - Enter text into a field
- `type <text> in <field>` - Type text in a field
- `input <text> in <field>` - Input text in a field

### Search
- `search for <query>` - Search on Google
- `look for <query>` - Look for something
- `find <query>` - Find something

### Utilities
- `take screenshot` - Capture current page
- `capture screenshot` - Capture current page
- `save screenshot` - Save current page as image
- `scroll to <element>` - Scroll to an element
- `scroll down to <element>` - Scroll down to an element
- `wait for <element>` - Wait for element to appear
- `pause until <element>` - Wait for element
- `get text from <element>` - Extract text from element
- `read <element>` - Read text from element
- `extract <element>` - Extract content from element

### Other
- `submit` - Submit current form
- `press enter` - Press enter key
- `hit enter` - Hit enter key
- `help` - Show help message
- `quit` / `exit` / `q` - Close browser and exit

## Examples

### Example 1: Simple Web Search
```bash
python browser_automation.py --commands \
  "go to google.com" \
  "search for weather forecast" \
  "take screenshot"
```

### Example 2: Form Automation
```bash
python browser_automation.py --commands \
  "go to example.com/login" \
  "fill username with myuser" \
  "fill password with mypassword123" \
  "click login" \
  "take screenshot"
```

### Example 3: Data Extraction
```bash
python browser_automation.py --commands \
  "go to news.ycombinator.com" \
  "get text from .titleline" \
  "take screenshot"
```

### Example 4: Using Command File
```bash
# automation_tasks.txt
# Login to a website and capture homepage
go to example.com
fill email with user@example.com
fill password with secret123
click Sign In
wait for dashboard
take screenshot
get text from welcome-message
```

```bash
python browser_automation.py --file automation_tasks.txt
```

## API Usage

You can also use the `BrowserAutomation` class directly in your Python code:

```python
from browser_automation import BrowserAutomation

# Create automation instance
automation = BrowserAutomation(headless=True)

# Start browser
automation.start_browser()

# Navigate and interact
automation.navigate_to("https://example.com")
automation.fill_form("#username", "myuser")
automation.fill_form("#password", "mypassword")
automation.click_element("#login-btn")

# Take screenshot
automation.take_screenshot("logged_in.png")

# Get page title
title = automation.get_page_title()
print(f"Page title: {title}")

# Close browser
automation.close_browser()
```

## Advanced Features

### Custom Selectors

The tool supports various CSS selectors:
- By ID: `#element-id`
- By class: `.class-name`
- By attribute: `[name='username']`
- By tag: `button`, `input`, `a`
- Combined: `button.submit`, `input[type='email']`

### Smart Element Matching

When you use natural language commands like "click login", the tool automatically tries multiple strategies:
1. Match by name attribute: `[name='login']`
2. Match by ID: `[id='login']`
3. Match by link text: `a[href*='login']`
4. Match by button text: `button:contains('login')`
5. Use as raw CSS selector

## Troubleshooting

### Browser Not Starting

If Chrome/Firefox is not installed, the tool will attempt to run in headless mode. Make sure you have:
- Chrome/Chromium or Firefox installed, OR
- The appropriate WebDriver (chromedriver/geckodriver) in your PATH

### Element Not Found

If an element can't be found:
1. Try using more specific selectors
2. Add a wait command before interacting: `wait for loading-spinner`
3. Check if the page has fully loaded
4. Use CSS selectors directly: `click #specific-element-id`

### Timeout Issues

Increase the wait time by modifying `self.wait_time` in the `__init__` method of `BrowserAutomation` class.

## License

MIT License - Feel free to use and modify for your projects.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

---

**Note**: This tool is intended for legitimate automation tasks. Please respect website terms of service and robots.txt files when automating interactions.