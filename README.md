# init_driver

`init_driver.py` is a Python utility for quickly initializing and customizing Selenium Chrome WebDriver sessions, with support for undetected Chrome, user agent spoofing, language settings, and more. It is designed to simplify web scraping and automation tasks.

## Features

- **Automatic ChromeDriver installation** (via `chromedriver_autoinstaller`)
- **Support for undetected Chrome** (via `undetected_chromedriver`)
- **Custom user agent and language settings**
- **Window size and position control** (including headless mode)
- **Notification and security settings**
- **Cookie injection and initial URL loading**
- **Logging for debugging**

## Usage

### Basic Example

```python
from init_driver import create_driver

driver, wait = create_driver(window_size="max")
driver.get("https://www.google.com/")
# ... your automation code ...
driver.quit()
```

### Custom User Agent and Language

```python
from init_driver import create_driver, ENGLISH_USA

driver, wait = create_driver(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    language=ENGLISH_USA,
    window_size="1200x800"
)
driver.get("https://www.example.com/")
driver.quit()
```

### Using Undetected Chrome

```python
from init_driver import create_driver

driver, wait = create_driver(undetectable=True)
driver.get("https://www.whatsmyua.info/")
driver.quit()
```

## Parameters

- `drivers_route`: Path to ChromeDriver (auto-installed if not provided)
- `user_agent`: Custom user agent string
- `window_size`: `"max"`, `"min"`, or `"WIDTHxHEIGHT"`
- `window_position`: Tuple for window position
- `sand_box`: Enable/disable Chrome sandbox
- `wait_time`: Timeout for WebDriverWait
- `manage_notificaions`: Chrome notification level (0, 1, 2)
- `language`: Tuple for browser language
- `save_psw`: Enable/disable password saving
- `camuflate`: Hide Selenium automation
- `disable_web_security`: Disable Chrome web security
- `install`: Force ChromeDriver installation
- `undetectable`: Use undetected Chrome
- `cookies`: Dictionary of cookies to inject
- `initial_url`: URL to open on start

## Drawbacks

- **Chrome only**: No support for Firefox, Edge, or other browsers.
- **Linux/Windows only**: May not work on all platforms.
- **Limited error handling**: Some exceptions may not be caught.
- **Requires external files**: Needs `driver_info/langs.json` for language support.
- **Not a full Selenium wrapper**: Only covers initialization, not advanced browser automation.

## Requirements

- Python 3.8+
- selenium
- chromedriver_autoinstaller
- undetected_chromedriver
- (optional) fake_useragent

## License

MIT License

---
