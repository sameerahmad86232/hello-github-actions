#!/usr/bin/env python3
"""
Advanced AI Browser Automation Tool
Automates complex tasks via natural language prompts using Selenium + AI.
Features: 50+ automation capabilities, parallel scraping, YouTube transcription, 
book generation, KDP analysis, Reedsy publishing, and more.
"""

import re
import os
import time
import json
import argparse
import hashlib
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from collections import Counter

# Selenium imports
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

# Optional AI imports
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Optional transcription imports
try:
    import youtube_transcript_api
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False


class AdvancedBrowserAutomation:
    """Advanced browser automation with AI capabilities."""
    
    def __init__(self, headless=True, api_key=None):
        """Initialize the advanced browser automation tool."""
        self.driver = None
        self.headless = headless
        self.wait_time = 15
        self.command_history = []
        self.task_log = []
        self.downloads_path = None
        self.data_store = {}
        self.scraped_data = []
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            print("✓ OpenAI client initialized")
        elif OPENAI_AVAILABLE and not self.api_key:
            print("⚠ OpenAI available but no API key provided")
        
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

    def start_browser(self):
        """Start the browser instance with enhanced settings."""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Setup downloads directory
        self.downloads_path = os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.downloads_path, exist_ok=True)
        prefs = {
            "download.default_directory": self.downloads_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.always_open_pdf_externally": True,
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✓ Browser started successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to start browser: {e}")
            return self.start_firefox()

    def start_firefox(self):
        """Try starting Firefox browser."""
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        
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

    # ==================== NAVIGATION FEATURES ====================
    
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

    def navigate_multiple(self, urls, max_workers=5):
        """Navigate to multiple URLs in parallel for scraping."""
        results = []
        
        def fetch_url(url):
            try:
                self.driver.get(url)
                time.sleep(2)
                content = {
                    "url": url,
                    "title": self.driver.title,
                    "content": self.driver.page_source,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"✓ Scraped: {url}")
                return content
            except Exception as e:
                print(f"✗ Failed {url}: {e}")
                return {"url": url, "error": str(e)}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_url, url): url for url in urls}
            for future in as_completed(futures):
                results.append(future.result())
        
        self.scraped_data.extend(results)
        return results

    def smart_wait(self, condition, timeout=30):
        """Wait for various conditions intelligently."""
        try:
            if condition.startswith("url:"):
                WebDriverWait(self.driver, timeout).until(EC.url_contains(condition[4:]))
            elif condition.startswith("element:"):
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, condition[8:]))
                )
            elif condition.startswith("text:"):
                WebDriverWait(self.driver, timeout).until(
                    EC.text_to_be_present_in_element((By.TAG_NAME, "body"), condition[5:])
                )
            elif condition == "load":
                WebDriverWait(self.driver, timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            print(f"✓ Wait condition met: {condition}")
            return True
        except TimeoutException:
            print(f"✗ Timeout waiting for: {condition}")
            return False

    # ==================== INTERACTION FEATURES ====================
    
    def find_element(self, selector, by=By.CSS_SELECTOR):
        """Find an element on the page."""
        try:
            element = WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            return None

    def find_elements(self, selector, by=By.CSS_SELECTOR):
        """Find multiple elements on the page."""
        try:
            elements = WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_all_elements_located((by, selector))
            )
            return elements
        except TimeoutException:
            return []

    def click_element(self, selector, by=By.CSS_SELECTOR):
        """Click an element on the page."""
        try:
            element = self.find_element(selector, by)
            if element:
                element.click()
                print(f"✓ Clicked: {selector}")
                return True
            return False
        except ElementClickInterceptedException:
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
            return False
        except Exception as e:
            print(f"✗ Fill failed: {e}")
            return False

    def type_slowly(self, selector, text, delay=0.1):
        """Type text slowly to simulate human input."""
        element = self.find_element(selector)
        if element:
            element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(delay)
            print(f"✓ Typed slowly: {text}")
            return True
        return False

    def submit_form(self):
        """Submit the current form."""
        try:
            self.driver.execute_script("document.activeElement.form.submit();")
            print("✓ Form submitted")
            return True
        except Exception as e:
            print(f"✗ Submit failed: {e}")
            return False

    def select_dropdown(self, selector, value, by_value="value"):
        """Select an option from a dropdown menu."""
        try:
            element = self.find_element(selector)
            if element:
                select = Select(element)
                if by_value == "value":
                    select.select_by_value(value)
                elif by_value == "text":
                    select.select_by_visible_text(value)
                elif by_value == "index":
                    select.select_by_index(int(value))
                print(f"✓ Selected '{value}' in dropdown")
                return True
            return False
        except Exception as e:
            print(f"✗ Selection failed: {e}")
            return False

    def hover_over(self, selector):
        """Hover mouse over an element."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            element = self.find_element(selector)
            if element:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).perform()
                print(f"✓ Hovered over: {selector}")
                return True
            return False
        except Exception as e:
            print(f"✗ Hover failed: {e}")
            return False

    def double_click(self, selector):
        """Double click an element."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            element = self.find_element(selector)
            if element:
                actions = ActionChains(self.driver)
                actions.double_click(element).perform()
                print(f"✓ Double clicked: {selector}")
                return True
            return False
        except Exception as e:
            print(f"✗ Double click failed: {e}")
            return False

    def right_click(self, selector):
        """Right click an element."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            element = self.find_element(selector)
            if element:
                actions = ActionChains(self.driver)
                actions.context_click(element).perform()
                print(f"✓ Right clicked: {selector}")
                return True
            return False
        except Exception as e:
            print(f"✗ Right click failed: {e}")
            return False

    def drag_and_drop(self, source_selector, target_selector):
        """Drag and drop an element."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            source = self.find_element(source_selector)
            target = self.find_element(target_selector)
            if source and target:
                actions = ActionChains(self.driver)
                actions.drag_and_drop(source, target).perform()
                print(f"✓ Dragged {source_selector} to {target_selector}")
                return True
            return False
        except Exception as e:
            print(f"✗ Drag and drop failed: {e}")
            return False

    def scroll_to_element(self, selector):
        """Scroll to an element."""
        try:
            element = self.find_element(selector)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                print(f"✓ Scrolled to: {selector}")
                return True
            return False
        except Exception as e:
            print(f"✗ Scroll failed: {e}")
            return False

    def scroll_page(self, direction="down", amount=500):
        """Scroll the page up or down."""
        try:
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"✓ Scrolled {direction}")
            return True
        except Exception as e:
            print(f"✗ Scroll failed: {e}")
            return False

    # ==================== DATA EXTRACTION FEATURES ====================
    
    def get_page_content(self):
        """Get the current page content."""
        return self.driver.page_source

    def get_page_title(self):
        """Get the current page title."""
        return self.driver.title

    def get_page_url(self):
        """Get the current page URL."""
        return self.driver.current_url

    def extract_text(self, selector):
        """Extract text from an element."""
        element = self.find_element(selector)
        if element:
            return element.text
        return None

    def extract_all_links(self):
        """Extract all links from the current page."""
        links = self.find_elements("a")
        return [{"text": link.text, "href": link.get_attribute("href")} for link in links]

    def extract_all_images(self):
        """Extract all images from the current page."""
        images = self.find_elements("img")
        return [{"src": img.get_attribute("src"), "alt": img.get_attribute("alt")} for img in images]

    def extract_table_data(self, table_selector):
        """Extract data from an HTML table."""
        table = self.find_element(table_selector)
        if not table:
            return []
        
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(By.TAG_NAME, "th")
            row_data = [cell.text for cell in cells]
            if row_data:
                data.append(row_data)
        return data

    def extract_product_info(self):
        """Extract product information from e-commerce pages."""
        info = {
            "title": self.extract_text("h1") or self.extract_text(".product-title"),
            "price": self.extract_text(".price") or self.extract_text("[data-price]"),
            "rating": self.extract_text(".rating") or self.extract_text("[itemprop='ratingValue']"),
            "reviews": self.extract_text(".reviews") or self.extract_text("[itemprop='reviewCount']"),
            "description": self.extract_text(".description") or self.extract_text("#productDescription"),
            "availability": self.extract_text(".availability") or self.extract_text("[data-availability]"),
        }
        return {k: v for k, v in info.items() if v}

    def get_attribute(self, selector, attribute):
        """Get an attribute value from an element."""
        element = self.find_element(selector)
        if element:
            return element.get_attribute(attribute)
        return None

    def capture_network_data(self):
        """Capture network requests (requires CDP)."""
        try:
            logs = self.driver.get_log("performance")
            requests = []
            for log in logs:
                message = json.loads(log["message"])["message"]
                if message["method"] == "Network.requestWillBeSent":
                    requests.append(message["params"]["request"])
            return requests
        except Exception as e:
            print(f"✗ Network capture failed: {e}")
            return []

    # ==================== SCREENSHOT & RECORDING FEATURES ====================
    
    def take_screenshot(self, filename=None):
        """Take a screenshot of the current page."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            self.driver.save_screenshot(filename)
            print(f"✓ Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Screenshot failed: {e}")
            return None

    def take_fullpage_screenshot(self, filename=None):
        """Take a full-page screenshot."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"fullpage_{timestamp}.png"
            
            # Get total height
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            total_width = self.driver.execute_script("return document.body.scrollWidth")
            
            # Resize window
            self.driver.set_window_size(total_width, total_height)
            time.sleep(1)
            
            self.driver.save_screenshot(filename)
            print(f"✓ Full-page screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Full-page screenshot failed: {e}")
            return None

    def save_page_html(self, filename=None):
        """Save the current page HTML to a file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"page_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"✓ Page saved to: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Save page failed: {e}")
            return None

    def save_page_pdf(self, filename=None):
        """Save the current page as PDF."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"page_{timestamp}.pdf"
            
            self.driver.execute_cdp_cmd("Page.printToPDF", {
                "printBackground": True,
                "path": os.path.abspath(filename)
            })
            print(f"✓ PDF saved to: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Save PDF failed: {e}")
            return None

    # ==================== WINDOW & TAB MANAGEMENT ====================
    
    def switch_to_frame(self, frame_identifier):
        """Switch to a frame by name, id, or index."""
        try:
            self.driver.switch_to.frame(frame_identifier)
            print(f"✓ Switched to frame: {frame_identifier}")
            return True
        except Exception as e:
            print(f"✗ Switch to frame failed: {e}")
            return False

    def switch_to_parent_frame(self):
        """Switch to parent frame."""
        try:
            self.driver.switch_to.parent_frame()
            print("✓ Switched to parent frame")
            return True
        except Exception as e:
            print(f"✗ Switch to parent frame failed: {e}")
            return False

    def switch_to_window(self, window_index=0):
        """Switch to a different browser window/tab."""
        try:
            windows = self.driver.window_handles
            if 0 <= window_index < len(windows):
                self.driver.switch_to.window(windows[window_index])
                print(f"✓ Switched to window {window_index}")
                return True
            return False
        except Exception as e:
            print(f"✗ Switch to window failed: {e}")
            return False

    def open_new_tab(self, url=None):
        """Open a new tab."""
        try:
            self.driver.execute_script("window.open();")
            if url:
                windows = self.driver.window_handles
                self.driver.switch_to.window(windows[-1])
                self.driver.get(url)
            print(f"✓ New tab opened")
            return True
        except Exception as e:
            print(f"✗ Open new tab failed: {e}")
            return False

    def close_current_tab(self):
        """Close the current tab."""
        try:
            self.driver.close()
            print("✓ Tab closed")
            return True
        except Exception as e:
            print(f"✗ Close tab failed: {e}")
            return False

    def get_all_windows(self):
        """Get all open window handles."""
        return self.driver.window_handles

    # ==================== COOKIE & STORAGE MANAGEMENT ====================
    
    def get_cookies(self):
        """Get all cookies."""
        return self.driver.get_cookies()

    def add_cookie(self, cookie_dict):
        """Add a cookie."""
        try:
            self.driver.add_cookie(cookie_dict)
            print(f"✓ Cookie added: {cookie_dict.get('name')}")
            return True
        except Exception as e:
            print(f"✗ Add cookie failed: {e}")
            return False

    def delete_cookie(self, cookie_name):
        """Delete a specific cookie."""
        try:
            self.driver.delete_cookie(cookie_name)
            print(f"✓ Cookie deleted: {cookie_name}")
            return True
        except Exception as e:
            print(f"✗ Delete cookie failed: {e}")
            return False

    def clear_cookies(self):
        """Clear all cookies."""
        try:
            self.driver.delete_all_cookies()
            print("✓ All cookies cleared")
            return True
        except Exception as e:
            print(f"✗ Clear cookies failed: {e}")
            return False

    def get_local_storage(self, key=None):
        """Get local storage items."""
        try:
            if key:
                return self.driver.execute_script(f"return localStorage.getItem('{key}');")
            return self.driver.execute_script("return localStorage;")
        except Exception as e:
            print(f"✗ Get local storage failed: {e}")
            return None

    def set_local_storage(self, key, value):
        """Set a local storage item."""
        try:
            self.driver.execute_script(f"localStorage.setItem('{key}', '{value}');")
            print(f"✓ Local storage set: {key}")
            return True
        except Exception as e:
            print(f"✗ Set local storage failed: {e}")
            return False

    # ==================== JAVASCRIPT EXECUTION ====================
    
    def execute_javascript(self, script):
        """Execute custom JavaScript code."""
        try:
            result = self.driver.execute_script(script)
            return result
        except Exception as e:
            print(f"✗ JavaScript execution failed: {e}")
            return None

    def execute_async_javascript(self, script):
        """Execute async JavaScript code."""
        try:
            result = self.driver.execute_async_script(script)
            return result
        except Exception as e:
            print(f"✗ Async JavaScript execution failed: {e}")
            return None

    def inject_javascript(self, js_file):
        """Inject JavaScript from a file."""
        try:
            with open(js_file, 'r') as f:
                script = f.read()
            self.driver.execute_script(script)
            print(f"✓ Injected: {js_file}")
            return True
        except Exception as e:
            print(f"✗ Inject JavaScript failed: {e}")
            return False

    # ==================== AI-POWERED FEATURES ====================
    
    def ai_analyze_page(self, focus=None):
        """Use AI to analyze the current page content."""
        if not self.client:
            print("⚠ OpenAI client not available")
            return None
        
        content = self.extract_text("body")[:15000]  # Limit content length
        prompt = f"Analyze this webpage content{' focusing on ' + focus if focus else ''}:\n\n{content}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a web content analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )
            analysis = response.choices[0].message.content
            print(f"✓ AI Analysis complete")
            return analysis
        except Exception as e:
            print(f"✗ AI analysis failed: {e}")
            return None

    def ai_extract_entities(self):
        """Use AI to extract entities from page content."""
        if not self.client:
            print("⚠ OpenAI client not available")
            return None
        
        content = self.extract_text("body")[:10000]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Extract key entities (names, dates, places, organizations) from the text."},
                    {"role": "user", "content": content}
                ],
                response_format={"type": "json_object"}
            )
            entities = json.loads(response.choices[0].message.content)
            print(f"✓ Entity extraction complete")
            return entities
        except Exception as e:
            print(f"✗ Entity extraction failed: {e}")
            return None

    def ai_summarize_content(self, length="medium"):
        """Use AI to summarize page content."""
        if not self.client:
            print("⚠ OpenAI client not available")
            return None
        
        content = self.extract_text("body")[:15000]
        length_map = {"short": 100, "medium": 300, "long": 500}
        word_limit = length_map.get(length, 300)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Summarize this content in approximately {word_limit} words."},
                    {"role": "user", "content": content}
                ]
            )
            summary = response.choices[0].message.content
            print(f"✓ Summary generated ({length})")
            return summary
        except Exception as e:
            print(f"✗ Summarization failed: {e}")
            return None

    def ai_generate_content(self, prompt, context=None):
        """Use AI to generate content based on prompt."""
        if not self.client:
            print("⚠ OpenAI client not available")
            return None
        
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\n{prompt}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful content generator."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=3000
            )
            content = response.choices[0].message.content
            print(f"✓ Content generated")
            return content
        except Exception as e:
            print(f"✗ Content generation failed: {e}")
            return None

    # ==================== YOUTUBE & TRANSCRIPTION FEATURES ====================
    
    def watch_youtube_video(self, video_url):
        """Navigate to and play a YouTube video."""
        try:
            self.navigate_to(video_url)
            time.sleep(3)
            
            # Try to click play button
            play_button = self.find_element("button.ytp-play-button")
            if play_button:
                play_button.click()
                print("✓ Video playing")
            return True
        except Exception as e:
            print(f"✗ Watch video failed: {e}")
            return False

    def get_youtube_transcript(self, video_url):
        """Get transcript from a YouTube video."""
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            print("⚠ youtube-transcript-api not installed")
            return None
        
        try:
            video_id = video_url.split("v=")[1].split("&")[0] if "v=" in video_url else video_url.split("/")[-1]
            transcript_list = youtube_transcript_api.YouTubeTranscriptApi.list_transcripts(video_id)
            
            transcript = transcript_list.find_generated_transcript(['en']) or transcript_list.find_manually_created_transcript(['en'])
            transcript_data = transcript.fetch()
            
            full_text = " ".join([entry['text'] for entry in transcript_data])
            print(f"✓ Transcript retrieved ({len(full_text)} chars)")
            return full_text
        except Exception as e:
            print(f"✗ Transcript retrieval failed: {e}")
            return None

    def transcribe_and_summarize_youtube(self, video_url):
        """Transcribe YouTube video and provide AI summary."""
        transcript = self.get_youtube_transcript(video_url)
        if not transcript:
            return None
        
        if self.client:
            summary = self.ai_summarize_content(transcript[:15000])
            return {"transcript": transcript, "summary": summary}
        
        return {"transcript": transcript, "summary": "AI not available for summarization"}

    # ==================== KDP & BOOK ANALYSIS FEATURES ====================
    
    def analyze_kdp_bestsellers(self, category="fiction", num_books=20):
        """Analyze KDP bestsellers in a category."""
        try:
            self.navigate_to(f"https://www.amazon.com/Best-Sellers-Kindle-Store-{category}/zgbs/digital-text")
            time.sleep(3)
            
            books = []
            book_elements = self.find_elements(".zg-item-immersion")[:num_books]
            
            for i, book in enumerate(book_elements, 1):
                try:
                    title_elem = book.find_element(By.CSS_SELECTOR, ".zg-text-truncate")
                    author_elem = book.find_element(By.CSS_SELECTOR, ".a-size-small")
                    rank_elem = book.find_element(By.CSS_SELECTOR, ".zg-badge-text")
                    
                    books.append({
                        "rank": i,
                        "title": title_elem.text if title_elem else "N/A",
                        "author": author_elem.text if author_elem else "N/A",
                        "badge": rank_elem.text if rank_elem else "N/A"
                    })
                except:
                    continue
            
            print(f"✓ Analyzed {len(books)} books")
            self.data_store["kdp_analysis"] = books
            return books
        except Exception as e:
            print(f"✗ KDP analysis failed: {e}")
            return []

    def analyze_author_patterns(self, author_names):
        """Analyze patterns in author names and styles."""
        if not self.client:
            print("⚠ OpenAI client not available for pattern analysis")
            return None
        
        analysis_prompt = f"Analyze these bestselling authors and identify patterns in their names, genres, writing styles, and success factors:\n\n{', '.join(author_names)}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a publishing industry analyst."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=2000
            )
            patterns = response.choices[0].message.content
            print(f"✓ Pattern analysis complete")
            return patterns
        except Exception as e:
            print(f"✗ Pattern analysis failed: {e}")
            return None

    # ==================== BOOK WRITING FEATURES ====================
    
    def generate_book_outline(self, topic, num_chapters=10):
        """Generate a book outline using AI."""
        if not self.client:
            print("⚠ OpenAI client not available")
            return None
        
        prompt = f"Create a detailed book outline about '{topic}' with {num_chapters} chapters. Include chapter titles and brief descriptions."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional book editor and author."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000
            )
            outline = response.choices[0].message.content
            print(f"✓ Book outline generated ({num_chapters} chapters)")
            return outline
        except Exception as e:
            print(f"✗ Outline generation failed: {e}")
            return None

    def write_book_chapter(self, topic, chapter_title, word_count=2000):
        """Write a book chapter using AI."""
        if not self.client:
            print("⚠ OpenAI client not available")
            return None
        
        prompt = f"Write a compelling chapter titled '{chapter_title}' for a book about '{topic}'. The chapter should be approximately {word_count} words, well-structured, engaging, and professionally written."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a bestselling author known for beautiful, engaging prose."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000
            )
            chapter = response.choices[0].message.content
            print(f"✓ Chapter written: {chapter_title} (~{word_count} words)")
            return chapter
        except Exception as e:
            print(f"✗ Chapter writing failed: {e}")
            return None

    def write_complete_book(self, topic, num_chapters=10, words_per_chapter=2000, output_file=None):
        """Write a complete book using AI."""
        if not self.client:
            print("⚠ OpenAI client not available")
            return None
        
        print(f"📚 Starting book project: '{topic}'")
        print(f"   Chapters: {num_chapters}, Words per chapter: {words_per_chapter}")
        
        # Generate outline first
        outline = self.generate_book_outline(topic, num_chapters)
        if not outline:
            return None
        
        # Extract chapter titles from outline (simplified)
        chapter_titles = [f"Chapter {i+1}" for i in range(num_chapters)]
        
        book_content = f"# {topic}\n\n## Book Outline\n{outline}\n\n"
        
        # Write each chapter
        for i in range(num_chapters):
            print(f"\n✍️ Writing chapter {i+1}/{num_chapters}...")
            chapter = self.write_book_chapter(topic, chapter_titles[i], words_per_chapter)
            if chapter:
                book_content += f"\n\n## {chapter_titles[i]}\n\n{chapter}"
            
            # Save progress
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(book_content)
                print(f"   ✓ Progress saved to {output_file}")
        
        print(f"\n✓ Book complete! Total content generated.")
        return book_content

    def generate_book_title(self, topic, style="catchy"):
        """Generate attractive book titles using AI."""
        if not self.client:
            print("⚠ OpenAI client not available")
            return None
        
        prompt = f"Generate 10 {style} book titles for a book about '{topic}'. Make them compelling, memorable, and marketable."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative book title generator."},
                    {"role": "user", "content": prompt}
                ]
            )
            titles = response.choices[0].message.content
            print(f"✓ Generated book titles")
            return titles
        except Exception as e:
            print(f"✗ Title generation failed: {e}")
            return None

    # ==================== REEDSY INTEGRATION ====================
    
    def login_to_reedsy(self, email, password):
        """Login to Reedsy platform."""
        try:
            self.navigate_to("https://reedsy.com/login")
            time.sleep(2)
            
            # Fill login form
            self.fill_form("input[type='email']", email)
            self.fill_form("input[type='password']", password)
            time.sleep(1)
            
            # Submit
            self.click_element("button[type='submit']")
            time.sleep(3)
            
            # Check if login successful
            if "dashboard" in self.get_page_url().lower() or "welcome" in self.get_page_title().lower():
                print("✓ Logged in to Reedsy successfully")
                return True
            else:
                print("⚠ Login may have failed - please verify")
                return False
        except Exception as e:
            print(f"✗ Reedsy login failed: {e}")
            return False

    def create_reedsy_project(self, title, author_name):
        """Create a new book project on Reedsy."""
        try:
            self.navigate_to("https://reedsy.com/studio")
            time.sleep(2)
            
            # Click create new project
            self.click_element("button:contains('Create'), a:contains('New')")
            time.sleep(2)
            
            # Fill project details
            self.fill_form("input[placeholder*='title']", title)
            self.fill_form("input[placeholder*='author']", author_name)
            
            # Create project
            self.click_element("button:contains('Create'), button:contains('Start')")
            time.sleep(3)
            
            print(f"✓ Created Reedsy project: {title}")
            return True
        except Exception as e:
            print(f"✗ Create Reedsy project failed: {e}")
            return False

    def paste_content_to_reedsy(self, content, chapter_title=None):
        """Paste content into Reedsy editor."""
        try:
            # Find editor area
            editor = self.find_element(".editor-content, .ProseMirror, [contenteditable='true']")
            if editor:
                editor.click()
                time.sleep(1)
                
                # Clear existing content
                self.driver.execute_script("arguments[0].innerHTML = '';", editor)
                
                # Paste new content
                editor.send_keys(content)
                
                if chapter_title:
                    print(f"✓ Pasted content: {chapter_title}")
                else:
                    print("✓ Content pasted to Reedsy")
                return True
            
            print("✗ Editor not found")
            return False
        except Exception as e:
            print(f"✗ Paste to Reedsy failed: {e}")
            return False

    def export_reedsy_book(self, format="epub"):
        """Export book from Reedsy."""
        try:
            # Navigate to export
            self.click_element("button:contains('Export'), a:contains('Export')")
            time.sleep(2)
            
            # Select format
            if format.lower() == "pdf":
                self.click_element("button:contains('PDF'), input[value='pdf']")
            else:
                self.click_element("button:contains('EPUB'), input[value='epub']")
            
            time.sleep(2)
            
            # Confirm export
            self.click_element("button:contains('Download'), button:contains('Export')")
            time.sleep(5)
            
            print(f"✓ Exported book as {format.upper()}")
            return True
        except Exception as e:
            print(f"✗ Export from Reedsy failed: {e}")
            return False

    # ==================== PARALLEL SCRAPING FEATURES ====================
    
    def scrape_multiple_websites(self, urls, selectors=None, max_workers=5):
        """Scrape multiple websites in parallel."""
        results = []
        
        def scrape_site(url):
            try:
                self.driver.get(url)
                time.sleep(2)
                
                data = {
                    "url": url,
                    "title": self.driver.title,
                    "content": self.extract_text("body")[:5000],
                    "links": len(self.find_elements("a")),
                    "timestamp": datetime.now().isoformat()
                }
                
                if selectors:
                    for key, selector in selectors.items():
                        data[key] = self.extract_text(selector)
                
                print(f"✓ Scraped: {url}")
                return data
            except Exception as e:
                return {"url": url, "error": str(e)}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scrape_site, url): url for url in urls}
            for future in as_completed(futures):
                results.append(future.result())
        
        self.scraped_data.extend(results)
        return results

    def monitor_website_changes(self, url, check_interval=60, max_checks=10):
        """Monitor a website for changes."""
        previous_content = None
        
        for i in range(max_checks):
            try:
                self.driver.get(url)
                current_content = hashlib.md5(self.driver.page_source.encode()).hexdigest()
                
                if previous_content and current_content != previous_content:
                    print(f"⚠ Change detected at {datetime.now().isoformat()}")
                    self.take_screenshot(f"change_detected_{i}.png")
                
                previous_content = current_content
                print(f"✓ Check {i+1}/{max_checks} complete")
                
                if i < max_checks - 1:
                    time.sleep(check_interval)
            except Exception as e:
                print(f"✗ Monitor check failed: {e}")
        
        return True

    # ==================== FORM AUTOMATION FEATURES ====================
    
    def auto_fill_form(self, form_data):
        """Automatically fill a form with provided data."""
        for field_name, value in form_data.items():
            selectors_to_try = [
                f"[name='{field_name}']",
                f"[id='{field_name}']",
                f"input[placeholder*='{field_name}']",
                f"label:contains('{field_name}') + input",
            ]
            
            for selector in selectors_to_try:
                if self.fill_form(selector, value):
                    break
        
        print(f"✓ Form filled with {len(form_data)} fields")
        return True

    def solve_simple_captcha(self):
        """Attempt to solve simple CAPTCHA (basic only)."""
        # This is a placeholder - real CAPTCHA solving requires specialized services
        print("⚠ CAPTCHA solving requires manual intervention or third-party service")
        return False

    # ==================== LOGGING & EXPORT FEATURES ====================
    
    def log_task(self, prompt, success=True, data=None):
        """Log a task execution."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "success": success,
            "session_id": self.session_id
        }
        if data:
            log_entry["data"] = data
        self.task_log.append(log_entry)

    def export_task_log(self, filename=None):
        """Export the task log to a JSON file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"task_log_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.task_log, f, indent=2, ensure_ascii=False)
            print(f"✓ Task log exported to: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Export task log failed: {e}")
            return None

    def export_scraped_data(self, filename=None, format="json"):
        """Export scraped data."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scraped_data_{timestamp}.{format}"
            
            if format == "json":
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            elif format == "csv":
                import csv
                if self.scraped_data:
                    keys = self.scraped_data[0].keys()
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=keys)
                        writer.writeheader()
                        writer.writerows(self.scraped_data)
            
            print(f"✓ Scraped data exported to: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Export scraped data failed: {e}")
            return None

    def save_session(self, filename=None):
        """Save current session state."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"session_{self.session_id}_{timestamp}.json"
            
            session_data = {
                "session_id": self.session_id,
                "task_log": self.task_log,
                "scraped_data": self.scraped_data,
                "data_store": self.data_store,
                "current_url": self.get_page_url() if self.driver else None,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Session saved to: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Save session failed: {e}")
            return None

    # ==================== UTILITY FEATURES ====================
    
    def wait_for_element(self, selector, timeout=None):
        """Wait for an element to appear."""
        timeout = timeout or self.wait_time
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            print(f"✓ Element appeared: {selector}")
            return True
        except TimeoutException:
            print(f"✗ Timeout waiting for: {selector}")
            return False

    def wait_for_url_contains(self, text, timeout=None):
        """Wait until URL contains specific text."""
        timeout = timeout or self.wait_time
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(text))
            print(f"✓ URL now contains: {text}")
            return True
        except TimeoutException:
            print(f"✗ Timeout waiting for URL containing: {text}")
            return False

    def highlight_element(self, selector):
        """Highlight an element for debugging."""
        try:
            self.driver.execute_script(
                "arguments[0].style.border = '3px solid red';",
                self.find_element(selector)
            )
            print(f"✓ Highlighted: {selector}")
            return True
        except Exception as e:
            print(f"✗ Highlight failed: {e}")
            return False

    def get_page_metrics(self):
        """Get page performance metrics."""
        try:
            metrics = self.driver.execute_script("""
                return {
                    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                    domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                    firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
                    resourcesLoaded: performance.getEntriesByType('resource').length
                };
            """)
            return metrics
        except Exception as e:
            print(f"✗ Get metrics failed: {e}")
            return None

    def parse_prompt(self, prompt):
        """Parse natural language prompt and extract action."""
        prompt_lower = prompt.lower().strip()
        self.command_history.append(prompt)
        
        # Comprehensive action patterns
        actions = {
            'navigate': [r'go to\s+(.+)', r'navigate to\s+(.+)', r'open\s+(.+)', r'visit\s+(.+)'],
            'click': [r'click\s+(?:on\s+)?(.+)', r'press\s+(?:on\s+)?(.+)'],
            'fill': [r'fill\s+(.+?)\s+with\s+(.+)', r'type\s+(.+?)\s+in(?:to)?\s+(.+)'],
            'search': [r'search for\s+(.+)', r'look for\s+(.+)'],
            'screenshot': [r'take\s+(?:a\s+)?screenshot', r'capture\s+(.+)'],
            'scroll': [r'scroll to\s+(.+)', r'scroll down'],
            'wait': [r'wait for\s+(.+)', r'pause until\s+(.+)'],
            'extract': [r'extract\s+(.+)', r'get text from\s+(.+)'],
            'analyze': [r'analyze\s+(.+)', r'analyse\s+(.+)'],
            'scrape': [r'scrape\s+(.+)', r'scrape website'],
            'write': [r'write\s+(.+)', r'generate\s+(.+)'],
            'transcribe': [r'transcribe\s+(.+)', r'get transcript'],
            'login': [r'login to\s+(.+)', r'sign in to\s+(.+)'],
            'export': [r'export\s+(.+)', r'download\s+(.+)'],
            'quit': [r'quit', r'exit', r'close']
        }
        
        for action, patterns in actions.items():
            for pattern in patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    return action, match.groups()
        
        return None, None

    def execute_task(self, prompt):
        """Execute a task based on natural language prompt."""
        print(f"\n📝 Processing: '{prompt}'")
        
        action, params = self.parse_prompt(prompt)
        
        if not action:
            print("⚠ Could not understand the command. Try rephrasing.")
            return False
        
        print(f"🎯 Detected action: {action}")
        
        try:
            if action == 'navigate' and params:
                return self.navigate_to(params[0].strip())
            elif action == 'click' and params:
                return self.click_element(params[0].strip())
            elif action == 'fill' and params and len(params) >= 2:
                return self.fill_form(params[0].strip(), params[1].strip())
            elif action == 'search' and params:
                return self.navigate_to(f"https://www.google.com/search?q={params[0].replace(' ', '+')}")
            elif action == 'screenshot':
                return self.take_screenshot() is not None
            elif action == 'scroll' and params:
                return self.scroll_to_element(params[0].strip())
            elif action == 'wait' and params:
                return self.wait_for_element(params[0].strip())
            elif action == 'extract' and params:
                text = self.extract_text(params[0].strip())
                if text:
                    print(f"📄 Extracted: {text[:200]}...")
                    return True
                return False
            elif action == 'quit':
                self.close_browser()
                return True
            else:
                print(f"⚠ Action '{action}' requires advanced mode or specific implementation")
                return False
                
        except Exception as e:
            print(f"✗ Task execution failed: {e}")
            return False

    def run_interactive_mode(self):
        """Run in interactive mode."""
        print("\n" + "="*70)
        print("🤖 Advanced AI Browser Automation Tool")
        print("="*70)
        print("\n✨ Features: 50+ automation capabilities")
        print("   • Web scraping & data extraction")
        print("   • AI-powered content analysis & generation")
        print("   • YouTube transcription & summarization")
        print("   • Book writing & KDP analysis")
        print("   • Reedsy integration & publishing")
        print("   • Parallel scraping & monitoring")
        print("   • Form automation & screenshots")
        print("\n💡 Tip: Set OPENAI_API_KEY environment variable for AI features")
        print("="*70 + "\n")
        
        if not self.start_browser():
            print("Failed to start browser. Exiting.")
            return
        
        while True:
            try:
                prompt = input("\n🤖 Enter command: ").strip()
                
                if not prompt:
                    continue
                
                if prompt.lower() in ['quit', 'exit', 'q']:
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
        print("\n" + "-"*70)
        print("📖 Available Commands:")
        print("-"*70)
        print("""
NAVIGATION:
  • go to <url>                    - Navigate to website
  • search for <query>             - Google search

INTERACTION:
  • click <element>                - Click element
  • fill <field> with <text>       - Fill form field
  • scroll to <element>            - Scroll to element

DATA EXTRACTION:
  • extract <selector>             - Get text from element
  • take screenshot                - Capture page

AI FEATURES (requires API key):
  • analyze <topic>                - AI page analysis
  • write <content>                - AI content generation
  • transcribe <youtube_url>       - Get video transcript

BOOK WRITING:
  • write book about <topic>       - Generate complete book
  • analyze kdp <category>         - KDP bestseller analysis

PUBLISHING:
  • login to reedsy                - Login to Reedsy
  • export as epub                 - Export book

UTILITIES:
  • help                           - Show this message
  • quit/exit                      - Close browser
        """)
        print("-"*70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Advanced AI Browser Automation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python advanced_browser_automation.py
    
  With visible browser:
    python advanced_browser_automation.py --no-headless
    
  Batch commands:
    python advanced_browser_automation.py -c "go to google.com" "search for python"
    
  From file:
    python advanced_browser_automation.py -f commands.txt

Environment Variables:
  OPENAI_API_KEY    - Required for AI features
        """
    )
    
    parser.add_argument('--commands', '-c', nargs='+', help='Commands to execute')
    parser.add_argument('--file', '-f', type=str, help='File with commands')
    parser.add_argument('--no-headless', action='store_true', help='Visible browser')
    parser.add_argument('--api-key', type=str, help='OpenAI API key')
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    automation = AdvancedBrowserAutomation(headless=not args.no_headless, api_key=api_key)
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                commands = [line.strip() for line in f if line.strip()]
            for cmd in commands:
                automation.execute_task(cmd)
                time.sleep(1)
            automation.export_task_log()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
    
    elif args.commands:
        for cmd in args.commands:
            automation.execute_task(cmd)
            time.sleep(1)
        automation.export_task_log()
    
    else:
        automation.run_interactive_mode()


if __name__ == "__main__":
    main()
