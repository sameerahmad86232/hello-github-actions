#!/usr/bin/env python3
"""
Browser Automation Tool
Automates user tasks via natural language prompts using Selenium.
"""

import re
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
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

    def parse_prompt(self, prompt):
        """Parse natural language prompt and extract action."""
        prompt_lower = prompt.lower().strip()
        
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
        print("  - 'go to <url>' - Navigate to a website")
        print("  - 'click <element>' - Click on an element")
        print("  - 'fill <field> with <text>' - Fill a form field")
        print("  - 'search for <query>' - Search on Google")
        print("  - 'take screenshot' - Capture current page")
        print("  - 'scroll to <element>' - Scroll to an element")
        print("  - 'wait for <element>' - Wait for element to appear")
        print("  - 'get text from <element>' - Extract text")
        print("  - 'quit' or 'exit' - Close browser and exit")
        print("  - 'help' - Show this help message")
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
                    print("\n👋 Closing browser...")
                    self.close_browser()
                    break
                
                if prompt.lower() in ['help', 'h', '?']:
                    self.print_help()
                    continue
                
                self.execute_task(prompt)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Closing browser...")
                self.close_browser()
                break
            except EOFError:
                print("\n\n👋 EOF received. Closing browser...")
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
        print("  • click login")
        print("  • click on button#submit")
        print("  • fill username with john_doe")
        print("  • enter password123 into password")
        print()
        print("Search:")
        print("  • search for python tutorial")
        print("  • look for best restaurants")
        print()
        print("Utilities:")
        print("  • take screenshot")
        print("  • scroll to footer")
        print("  • wait for loading-spinner")
        print("  • get text from article-title")
        print()
        print("Other:")
        print("  • submit (submit current form)")
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
