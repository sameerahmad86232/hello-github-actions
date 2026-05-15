#!/usr/bin/env python3
"""
Browser Automation Tool
Automates user tasks via natural language prompts using Selenium.
"""

import re
import os
import time
import json
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)


class BrowserAutomation:
    """Automates browser tasks based on natural language prompts."""

    def __init__(self, headless=True):
        """Initialize the browser automation tool."""
        self.driver = None
        self.headless = headless
        self.wait_time = 10
        self.command_history = []
        self.task_log = []
        self.downloads_path = None

    def start_browser(self):
        """Start the browser instance."""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Setup downloads directory
        self.downloads_path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.downloads_path, exist_ok=True)
        prefs = {
            "download.default_directory": self.downloads_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("✓ Browser started successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to start browser: {e}")
            print("Trying with Firefox...")
            return self.start_firefox()

    def start_firefox(self):
        """Try starting Firefox browser."""
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        
        options = FirefoxOptions()
        if self.headless:
            options.add_argument("--headless")
        
        try:
            self.driver = webdriver.Firefox(options=options)
            print("✓ Firefox browser started successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to start Firefox: {e}")
            return False

    def close_browser(self):
        """Close the browser instance."""
        if self.driver:
            self.driver.quit()
            print("✓ Browser closed")

    def navigate_to(self, url):
        """Navigate to a URL."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            self.driver.get(url)
            print(f"✓ Navigated to: {url}")
            return True
        except Exception as e:
            print(f"✗ Navigation failed: {e}")
            return False

    def find_element(self, selector, by=By.CSS_SELECTOR):
        """Find an element on the page."""
        try:
            element = WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            return None

    def click_element(self, selector, by=By.CSS_SELECTOR):
        """Click an element on the page."""
        try:
            element = self.find_element(selector, by)
            if element:
                element.click()
                print(f"✓ Clicked: {selector}")
                return True
            else:
                print(f"✗ Element not found: {selector}")
                return False
        except ElementClickInterceptedException:
            # Try clicking with JavaScript
            self.driver.execute_script("arguments[0].click();", element)
            print(f"✓ Clicked (via JS): {selector}")
            return True
        except Exception as e:
            print(f"✗ Click failed: {e}")
            return False

    def fill_form(self, selector, text, by=By.CSS_SELECTOR):
        """Fill a form field with text."""
        try:
            element = self.find_element(selector, by)
            if element:
                element.clear()
                element.send_keys(text)
                print(f"✓ Filled '{selector}' with: {text}")
                return True
            else:
                print(f"✗ Element not found: {selector}")
                return False
        except Exception as e:
            print(f"✗ Fill failed: {e}")
            return False

    def get_page_content(self):
        """Get the current page content."""
        return self.driver.page_source

    def get_page_title(self):
        """Get the current page title."""
        return self.driver.title

    def take_screenshot(self, filename="screenshot.png"):
        """Take a screenshot of the current page."""
        try:
            self.driver.save_screenshot(filename)
            print(f"✓ Screenshot saved: {filename}")
            return True
        except Exception as e:
            print(f"✗ Screenshot failed: {e}")
            return False

    def scroll_to_element(self, selector, by=By.CSS_SELECTOR):
        """Scroll to an element."""
        try:
            element = self.find_element(selector, by)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                print(f"✓ Scrolled to: {selector}")
                return True
            return False
        except Exception as e:
            print(f"✗ Scroll failed: {e}")
            return False

    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Wait for an element to appear."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            print(f"✓ Element appeared: {selector}")
            return True
        except TimeoutException:
            print(f"✗ Timeout waiting for: {selector}")
            return False

    def select_dropdown(self, selector, value, by=By.CSS_SELECTOR, by_value="value"):
        """Select an option from a dropdown menu."""
        try:
            element = self.find_element(selector, by)
            if element:
                select = Select(element)
                if by_value == "value":
                    select.select_by_value(value)
                elif by_value == "text":
                    select.select_by_visible_text(value)
                elif by_value == "index":
                    select.select_by_index(int(value))
                print(f"✓ Selected '{value}' in dropdown: {selector}")
                return True
            else:
                print(f"✗ Dropdown not found: {selector}")
                return False
        except Exception as e:
            print(f"✗ Selection failed: {e}")
            return False

    def hover_over(self, selector, by=By.CSS_SELECTOR):
        """Hover mouse over an element."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            element = self.find_element(selector, by)
            if element:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).perform()
                print(f"✓ Hovered over: {selector}")
                return True
            else:
                print(f"✗ Element not found: {selector}")
                return False
        except Exception as e:
            print(f"✗ Hover failed: {e}")
            return False

    def double_click(self, selector, by=By.CSS_SELECTOR):
        """Double click an element."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            element = self.find_element(selector, by)
            if element:
                actions = ActionChains(self.driver)
                actions.double_click(element).perform()
                print(f"✓ Double clicked: {selector}")
                return True
            else:
                print(f"✗ Element not found: {selector}")
                return False
        except Exception as e:
            print(f"✗ Double click failed: {e}")
            return False

    def right_click(self, selector, by=By.CSS_SELECTOR):
        """Right click (context click) an element."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            element = self.find_element(selector, by)
            if element:
                actions = ActionChains(self.driver)
                actions.context_click(element).perform()
                print(f"✓ Right clicked: {selector}")
                return True
            else:
                print(f"✗ Element not found: {selector}")
                return False
        except Exception as e:
            print(f"✗ Right click failed: {e}")
            return False

    def get_attribute(self, selector, attribute, by=By.CSS_SELECTOR):
        """Get an attribute value from an element."""
        try:
            element = self.find_element(selector, by)
            if element:
                attr_value = element.get_attribute(attribute)
                print(f"📄 Attribute '{attribute}' value: {attr_value}")
                return attr_value
            else:
                print(f"✗ Element not found: {selector}")
                return None
        except Exception as e:
            print(f"✗ Get attribute failed: {e}")
            return None

    def execute_javascript(self, script):
        """Execute custom JavaScript code."""
        try:
            result = self.driver.execute_script(script)
            print(f"✓ JavaScript executed successfully")
            return result
        except Exception as e:
            print(f"✗ JavaScript execution failed: {e}")
            return None

    def wait_for_url_contains(self, text, timeout=10):
        """Wait until URL contains specific text."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.url_contains(text)
            )
            print(f"✓ URL now contains: {text}")
            return True
        except TimeoutException:
            print(f"✗ Timeout waiting for URL containing: {text}")
            return False

    def switch_to_frame(self, frame_identifier):
        """Switch to a frame by name, id, or index."""
        try:
            self.driver.switch_to.frame(frame_identifier)
            print(f"✓ Switched to frame: {frame_identifier}")
            return True
        except Exception as e:
            print(f"✗ Switch to frame failed: {e}")
            return False

    def switch_to_window(self, window_index=0):
        """Switch to a different browser window/tab."""
        try:
            windows = self.driver.window_handles
            if 0 <= window_index < len(windows):
                self.driver.switch_to.window(windows[window_index])
                print(f"✓ Switched to window {window_index}")
                return True
            else:
                print(f"✗ Window index {window_index} out of range")
                return False
        except Exception as e:
            print(f"✗ Switch to window failed: {e}")
            return False

    def save_page_html(self, filename=None):
        """Save the current page HTML to a file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"page_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"✓ Page saved to: {filename}")
            return True
        except Exception as e:
            print(f"✗ Save page failed: {e}")
            return False

    def log_task(self, prompt, success=True):
        """Log a task execution to the task log."""
        self.task_log.append({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "success": success
        })

    def export_task_log(self, filename="task_log.json"):
        """Export the task log to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.task_log, f, indent=2)
            print(f"✓ Task log exported to: {filename}")
            return True
        except Exception as e:
            print(f"✗ Export task log failed: {e}")
            return False

    def parse_prompt(self, prompt):
        """Parse natural language prompt and extract action."""
        prompt_lower = prompt.lower().strip()
        
        # Add to command history
        self.command_history.append(prompt)
        
        actions = {
            'navigate': [r'go to\s+(.+)', r'navigate to\s+(.+)', r'open\s+(.+)', r'visit\s+(.+)', r'browse\s+(.+)'],
            'click': [r'click\s+(?:on\s+)?(.+)', r'press\s+(?:on\s+)?(.+)', r'tap\s+(?:on\s+)?(.+)'],
            'fill': [r'fill\s+(.+?)\s+with\s+(.+)', r'enter\s+(.+?)\s+in(?:to)?\s+(.+)', r'type\s+(.+?)\s+in(?:to)?\s+(.+)', r'input\s+(.+?)\s+in(?:to)?\s+(.+)'],
            'search': [r'search for\s+(.+)', r'look for\s+(.+)', r'find\s+(.+)'],
            'screenshot': [r'take\s+(?:a\s+)?screenshot', r'capture\s+(?:a\s+)?screenshot', r'save\s+(?:a\s+)?screenshot'],
            'scroll': [r'scroll to\s+(.+)', r'scroll down to\s+(.+)'],
            'wait': [r'wait for\s+(.+)', r'pause until\s+(.+)'],
            'get_text': [r'get text from\s+(.+)', r'read\s+(.+)', r'extract\s+(.+)'],
            'submit': [r'submit', r'press enter', r'hit enter'],
            'select': [r'select\s+(.+?)\s+from\s+(.+)', r'choose\s+(.+?)\s+in\s+(.+)'],
            'hover': [r'hover over\s+(.+)', r'mouse over\s+(.+)'],
            'double_click': [r'double click\s+(?:on\s+)?(.+)', r'double-click\s+(.+)'],
            'right_click': [r'right click\s+(?:on\s+)?(.+)', r'context click\s+(.+)'],
            'get_attr': [r'get\s+(.+?)\s+attribute from\s+(.+)', r'attribute\s+(.+?)\s+of\s+(.+)'],
            'js': [r'run javascript\s+(.+)', r'execute js\s+(.+)', r'javascript\s+(.+)'],
            'wait_url': [r'wait for url.*?(.+)', r'url contains\s+(.+)'],
            'switch_frame': [r'switch to frame\s+(.+)', r'go to frame\s+(.+)'],
            'switch_window': [r'switch to window\s+(\d+)', r'go to tab\s+(\d+)'],
            'save_html': [r'save page', r'save html', r'export page'],
            'export_log': [r'export log', r'save task log'],
        }
        
        for action, patterns in actions.items():
            for pattern in patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    groups = match.groups()
                    return action, groups
        
        return None, None

    def execute_task(self, prompt):
        """Execute a task based on natural language prompt."""
        print(f"\n📝 Processing: '{prompt}'")
        
        action, params = self.parse_prompt(prompt)
        
        if not action:
            print("⚠ Could not understand the command. Please try rephrasing.")
            return False
        
        print(f"🎯 Detected action: {action}")
        
        try:
            if action == 'navigate':
                url = params[0].strip()
                return self.navigate_to(url)
            
            elif action == 'click':
                selector = params[0].strip()
                # Try different selector strategies
                selectors_to_try = [
                    f"[name='{selector}']",
                    f"[id='{selector}']",
                    f"a[href*='{selector}']",
                    f"button:contains('{selector}')",
                    f"*[text*='{selector}']",
                    selector,  # Use as-is (CSS selector)
                ]
                
                for sel in selectors_to_try:
                    if self.click_element(sel):
                        return True
                return False
            
            elif action == 'fill':
                if len(params) == 2:
                    value, field = params
                else:
                    field, value = params[0], params[1]
                
                field = field.strip()
                value = value.strip()
                
                selectors_to_try = [
                    f"[name='{field}']",
                    f"[id='{field}']",
                    f"input[placeholder*='{field}']",
                    f"label:contains('{field}') + input",
                    field,
                ]
                
                for sel in selectors_to_try:
                    if self.fill_form(sel, value):
                        return True
                return False
            
            elif action == 'search':
                query = params[0].strip()
                # Navigate to Google search
                self.navigate_to(f"https://www.google.com/search?q={query.replace(' ', '+')}")
                return True
            
            elif action == 'screenshot':
                filename = f"screenshot_{int(time.time())}.png"
                return self.take_screenshot(filename)
            
            elif action == 'scroll':
                selector = params[0].strip()
                return self.scroll_to_element(selector)
            
            elif action == 'wait':
                selector = params[0].strip()
                return self.wait_for_element(selector)
            
            elif action == 'get_text':
                selector = params[0].strip()
                element = self.find_element(selector)
                if element:
                    text = element.text
                    print(f"📄 Text content: {text}")
                    return True
                return False
            
            elif action == 'submit':
                # Try to submit the active form
                self.driver.execute_script("document.activeElement.form.submit();")
                print("✓ Form submitted")
                return True
            
            elif action == 'select':
                if len(params) == 2:
                    value, dropdown = params
                else:
                    dropdown, value = params[0], params[1]
                dropdown = dropdown.strip()
                value = value.strip()
                selectors_to_try = [
                    f"[name='{dropdown}']",
                    f"[id='{dropdown}']",
                    dropdown,
                ]
                for sel in selectors_to_try:
                    if self.select_dropdown(sel, value):
                        return True
                return False
            
            elif action == 'hover':
                selector = params[0].strip()
                return self.hover_over(selector)
            
            elif action == 'double_click':
                selector = params[0].strip()
                return self.double_click(selector)
            
            elif action == 'right_click':
                selector = params[0].strip()
                return self.right_click(selector)
            
            elif action == 'get_attr':
                if len(params) == 2:
                    attr, element = params
                else:
                    element, attr = params[0], params[1]
                element = element.strip()
                attr = attr.strip()
                selectors_to_try = [
                    f"[name='{element}']",
                    f"[id='{element}']",
                    element,
                ]
                for sel in selectors_to_try:
                    result = self.get_attribute(sel, attr)
                    if result is not None:
                        return True
                return False
            
            elif action == 'js':
                script = params[0].strip()
                return self.execute_javascript(script) is not None
            
            elif action == 'wait_url':
                text = params[0].strip()
                return self.wait_for_url_contains(text)
            
            elif action == 'switch_frame':
                frame_id = params[0].strip()
                try:
                    return self.switch_to_frame(int(frame_id))
                except ValueError:
                    return self.switch_to_frame(frame_id)
            
            elif action == 'switch_window':
                window_idx = int(params[0].strip())
                return self.switch_to_window(window_idx)
            
            elif action == 'save_html':
                return self.save_page_html()
            
            elif action == 'export_log':
                return self.export_task_log()
            
            else:
                print(f"⚠ Unknown action: {action}")
                return False
                
        except Exception as e:
            print(f"✗ Task execution failed: {e}")
            return False

    def run_interactive_mode(self):
        """Run in interactive mode, accepting commands from user."""
        print("\n" + "="*60)
        print("🌐 Browser Automation Tool - Interactive Mode")
        print("="*60)
        print("\nAvailable commands:")
        print("  Navigation:")
        print("    • go to <url> - Navigate to a website")
        print("    • search for <query> - Search on Google")
        print()
        print("  Interaction:")
        print("    • click <element> - Click on an element")
        print("    • double click <element> - Double click")
        print("    • right click <element> - Right click")
        print("    • hover over <element> - Hover mouse")
        print("    • fill <field> with <text> - Fill form field")
        print("    • select <option> from <dropdown> - Select dropdown option")
        print("    • submit - Submit current form")
        print()
        print("  Utilities:")
        print("    • take screenshot - Capture current page")
        print("    • scroll to <element> - Scroll to element")
        print("    • wait for <element> - Wait for element")
        print("    • wait for url <text> - Wait for URL change")
        print("    • get text from <element> - Extract text")
        print("    • get <attr> attribute from <element> - Get attribute")
        print("    • save page - Save HTML to file")
        print()
        print("  Advanced:")
        print("    • run javascript <code> - Execute JS")
        print("    • switch to frame <id> - Switch to iframe")
        print("    • switch to window <n> - Switch to tab/window")
        print("    • export log - Save task log to JSON")
        print()
        print("  Other:")
        print("    • help - Show this message")
        print("    • quit/exit - Close browser and exit")
        print("="*60 + "\n")
        
        if not self.start_browser():
            print("Failed to start browser. Exiting.")
            return
        
        while True:
            try:
                prompt = input("\n🤖 Enter command: ").strip()
                
                if not prompt:
                    continue
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    # Export task log before exiting
                    if self.task_log:
                        self.export_task_log()
                    print("\n👋 Closing browser...")
                    self.close_browser()
                    break
                
                if prompt.lower() in ['help', 'h', '?']:
                    self.print_help()
                    continue
                
                success = self.execute_task(prompt)
                self.log_task(prompt, success)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Closing browser...")
                if self.task_log:
                    self.export_task_log()
                self.close_browser()
                break
            except EOFError:
                print("\n\n👋 EOF received. Closing browser...")
                if self.task_log:
                    self.export_task_log()
                self.close_browser()
                break

    def print_help(self):
        """Print help information."""
        print("\n" + "-"*60)
        print("📖 Help - Available Commands:")
        print("-"*60)
        print("Navigation:")
        print("  • go to example.com")
        print("  • navigate to https://example.com")
        print("  • open google.com")
        print()
        print("Interaction:")
        print("  • click login / click on button#submit")
        print("  • double click item / right click menu")
        print("  • hover over dropdown")
        print("  • fill username with john_doe")
        print("  • enter password123 into password")
        print("  • select 'Option 1' from myDropdown")
        print("  • submit (submit current form)")
        print()
        print("Search:")
        print("  • search for python tutorial")
        print("  • look for best restaurants")
        print()
        print("Utilities:")
        print("  • take screenshot")
        print("  • scroll to footer")
        print("  • wait for loading-spinner")
        print("  • wait for url results")
        print("  • get text from article-title")
        print("  • get href attribute from link")
        print("  • save page (save HTML)")
        print()
        print("Advanced:")
        print("  • run javascript alert('hello')")
        print("  • switch to frame 0")
        print("  • switch to window 1")
        print("  • export log (save task history)")
        print()
        print("Other:")
        print("  • help (show this message)")
        print("  • quit/exit (close browser)")
        print("-"*60 + "\n")

    def run_batch_mode(self, commands):
        """Run a batch of commands from a list."""
        print("\n🔄 Running batch mode with %d commands..." % len(commands))
        
        if not self.start_browser():
            print("Failed to start browser.")
            return False
        
        success_count = 0
        for i, command in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] Executing: {command}")
            if self.execute_task(command):
                success_count += 1
            time.sleep(1)  # Small delay between commands
        
        print(f"\n✅ Completed: {success_count}/{len(commands)} commands successful")
        self.close_browser()
        return success_count == len(commands)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Browser Automation Tool - Automate tasks via natural language prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python browser_automation.py
    
  Batch mode with commands:
    python browser_automation.py --commands "go to google.com" "search for python" "take screenshot"
    
  Headful mode (with visible browser):
    python browser_automation.py --no-headless
    
  From file (one command per line):
    python browser_automation.py --file commands.txt
        """
    )
    
    parser.add_argument(
        '--commands', '-c',
        nargs='+',
        help='Commands to execute in batch mode'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='File containing commands (one per line)'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in visible mode (not headless)'
    )
    
    args = parser.parse_args()
    
    automation = BrowserAutomation(headless=not args.no_headless)
    
    if args.file:
        # Read commands from file
        try:
            with open(args.file, 'r') as f:
                commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            automation.run_batch_mode(commands)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
        except Exception as e:
            print(f"Error reading file: {e}")
    
    elif args.commands:
        # Run batch mode with provided commands
        automation.run_batch_mode(args.commands)
    
    else:
        # Run interactive mode
        automation.run_interactive_mode()


if __name__ == "__main__":
    main()
