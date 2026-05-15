# 🤖 Advanced AI Browser Automation Tool

A powerful browser automation system with **50+ features** including AI-powered content generation, YouTube transcription, book writing, KDP analysis, Reedsy publishing, parallel web scraping, and more!

## ✨ Key Features

### 🔍 Web Scraping & Data Extraction
- **Parallel scraping** - Analyze 10,000+ websites in minimum time using multi-threading
- **Smart data extraction** - Extract text, links, images, tables, product info
- **Website monitoring** - Track changes on websites automatically
- **Network capture** - Monitor HTTP requests and responses

### 🧠 AI-Powered Intelligence (requires OpenAI API key)
- **Page analysis** - AI analyzes webpage content and provides insights
- **Entity extraction** - Automatically extract names, dates, organizations
- **Content summarization** - Generate concise summaries of any page
- **Smart content generation** - Create custom content based on prompts

### 📺 YouTube Integration
- **Video transcription** - Get full transcripts from YouTube videos
- **Auto summarization** - AI summarizes transcribed content
- **Watch on behalf** - Automate video playback and interaction

### 📚 Book Writing & Publishing
- **KDP Analysis** - Analyze bestselling books and authors on Amazon KDP
- **Pattern recognition** - Identify successful author patterns and styles
- **Book outline generation** - Create structured chapter outlines
- **Full book writing** - Write complete books with customizable chapters and word counts
- **Beautiful title generation** - AI generates catchy, marketable book titles
- **Reedsy integration** - Auto-login, paste content, and publish
- **Export to EPUB/PDF** - Generate professional ebook formats

### 🖱️ Browser Automation (50+ Actions)
- Navigation, clicking, form filling, scrolling
- Screenshot capture (including full-page)
- PDF generation from web pages
- Cookie and local storage management
- Tab and window management
- JavaScript execution (sync and async)
- Drag-and-drop, hover, double-click, right-click
- Dropdown selection, frame switching
- Smart waits and element highlighting

### 📊 Data Management
- Session saving and restoration
- Task logging with timestamps
- Export to JSON, CSV formats
- Scraped data organization

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (for AI features)
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

#### Interactive Mode (Recommended for Beginners)
```bash
python advanced_browser_automation.py
```

Then type commands like:
- `go to google.com`
- `search for python tutorials`
- `take screenshot`
- `quit`

#### Visible Browser Mode
```bash
python advanced_browser_automation.py --no-headless
```

#### Batch Commands
```bash
python advanced_browser_automation.py -c "go to google.com" "search for AI" "take screenshot"
```

#### From File
```bash
# Create commands.txt with one command per line
python advanced_browser_automation.py -f commands.txt
```

## 📖 Example Workflows

### 1. Analyze KDP Bestsellers & Write a Book

```python
from advanced_browser_automation import AdvancedBrowserAutomation

# Initialize with API key
bot = AdvancedBrowserAutomation(headless=False, api_key="your-key")
bot.start_browser()

# Analyze KDP bestsellers
books = bot.analyze_kdp_bestsellers(category="self-help", num_books=20)

# Extract author names and analyze patterns
authors = [book['author'] for book in books if book['author'] != 'N/A']
patterns = bot.analyze_author_patterns(authors[:10])
print(patterns)

# Generate book title
titles = bot.generate_book_title("mindfulness meditation", style="catchy")
print(titles)

# Write complete book
book = bot.write_complete_book(
    topic="Mindfulness Meditation for Beginners",
    num_chapters=12,
    words_per_chapter=1500,
    output_file="my_book.md"
)

# Login to Reedsy and publish
bot.login_to_reedsy("your@email.com", "password")
bot.create_reedsy_project("Mindfulness Meditation", "Your Name")

# Paste each chapter
for chapter in book.split('## ')[1:]:
    bot.paste_content_to_reedsy(chapter)

# Export as EPUB
bot.export_reedsy_book(format="epub")

bot.close_browser()
```

### 2. Watch YouTube & Get Summary

```python
bot = AdvancedBrowserAutomation(api_key="your-key")
bot.start_browser()

# Transcribe and summarize
result = bot.transcribe_and_summarize_youtube("https://youtube.com/watch?v=VIDEO_ID")
print("Transcript:", result['transcript'][:500])
print("Summary:", result['summary'])

bot.close_browser()
```

### 3. Parallel Website Analysis

```python
bot = AdvancedBrowserAutomation()
bot.start_browser()

# Scrape 1000+ websites in parallel
urls = [f"https://example{i}.com" for i in range(1, 1001)]
results = bot.scrape_multiple_websites(urls, max_workers=10)

# Export results
bot.export_scraped_data(filename="scraped_data.json", format="json")
bot.export_scraped_data(filename="scraped_data.csv", format="csv")

bot.close_browser()
```

### 4. Monitor Website Changes

```python
bot = AdvancedBrowserAutomation()
bot.start_browser()

# Monitor every 60 seconds, 10 checks
bot.monitor_website_changes(
    url="https://competitor.com/pricing",
    check_interval=60,
    max_checks=10
)

bot.close_browser()
```

## 🎯 Command Reference

### Navigation
| Command | Description |
|---------|-------------|
| `go to <url>` | Navigate to website |
| `search for <query>` | Google search |
| `open <url>` | Open URL in new tab |

### Interaction
| Command | Description |
|---------|-------------|
| `click <element>` | Click element |
| `fill <field> with <text>` | Fill form field |
| `scroll to <element>` | Scroll to element |
| `double click <element>` | Double click |
| `right click <element>` | Context menu |
| `hover over <element>` | Mouse hover |

### Data Extraction
| Command | Description |
|---------|-------------|
| `extract <selector>` | Get text from element |
| `take screenshot` | Capture page |
| `save page` | Save HTML file |
| `export log` | Save task history |

### AI Commands (requires API key)
| Command | Description |
|---------|-------------|
| `analyze <topic>` | AI page analysis |
| `write <content>` | Generate content |
| `transcribe <youtube_url>` | Get video transcript |
| `summarize` | AI summary of page |

### Book Writing
| Method | Description |
|--------|-------------|
| `generate_book_outline(topic, chapters)` | Create outline |
| `write_book_chapter(topic, title, words)` | Write chapter |
| `write_complete_book(topic, chapters, words)` | Full book |
| `generate_book_title(topic, style)` | Title ideas |
| `analyze_kdp_bestsellers(category)` | KDP research |

### Publishing
| Method | Description |
|--------|-------------|
| `login_to_reedsy(email, password)` | Login |
| `create_reedsy_project(title, author)` | New project |
| `paste_content_to_reedsy(content)` | Add chapter |
| `export_reedsy_book(format)` | EPUB/PDF export |

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | For AI only |

## 📦 Requirements

- Python 3.8+
- Chrome or Firefox browser
- Selenium WebDriver
- OpenAI API key (optional, for AI features)

### Install Dependencies
```bash
pip install selenium webdriver-manager openai youtube-transcript-api
```

## ⚠️ Important Notes

1. **Respect Websites**: Always follow robots.txt and terms of service
2. **Rate Limiting**: Add delays when scraping many pages
3. **CAPTCHA**: Some sites may require manual CAPTCHA solving
4. **API Costs**: AI features use OpenAI API (paid service)
5. **Login Security**: Don't hardcode passwords; use environment variables

## 🛠️ Troubleshooting

### Browser won't start
```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser  # Linux
# or download from google.com/chrome
```

### OpenAI errors
```bash
# Check API key
echo $OPENAI_API_KEY
# Ensure you have credits at platform.openai.com
```

### Module not found
```bash
pip install -r requirements.txt --upgrade
```

## 📝 License

MIT License - Feel free to use for personal and commercial projects!

## 🤝 Support

For issues, questions, or feature requests, please check the documentation or community forums.

---

**Built with ❤️ for automation enthusiasts**
