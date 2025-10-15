# init-selenium

`init_selenium` is a Python package that provides a convenient `DriverInit` class for initializing and customizing Selenium Chrome WebDriver sessions. It supports undetected Chrome, user agent management, language settings, and more, making it ideal for web scraping and automation tasks.

## Installation

Install directly from GitHub using pip:

```bash
pip install "git+https://github.com/lm319aka/init_selenium"
```

Or clone the repository and install in development mode:

```bash
git clone https://github.com/lm319aka/init_selenium.git
cd init_selenium
pip install -e .
```

Or directly pip-install:

```bash
pip install "git+https://github.com/lm319aka/init_selenium"
```

## Features

- **Automatic ChromeDriver Management** - Uses `webdriver_manager` for automatic driver installation
- **Undetected Chrome Support** - Built-in integration with `undetected_chromedriver`
- **Language Management** - Easy configuration of browser language preferences
- **Window Control** - Predefined window sizes and custom positioning
- **Security Settings** - Control over sandbox, web security, and notifications
- **Session Management** - Cookie injection and initial URL loading
- **Gmail Login Helper** - Built-in method for handling Gmail authentication flows

## Usage

### Basic Example

```python
from init_selenium.init_driver import DriverInit, WINDOW_MAX, ENGLISH_USA

# Initialize the driver manager
driver_init = DriverInit(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    language=ENGLISH_USA
)

# Create a new WebDriver instance
driver, wait = driver_init.create_driver(
    window_size=WINDOW_MAX,
    undetectable=True
)

try:
    driver.get("https://www.google.com/")
    # Your automation code here
finally:
    driver.quit()
```

### Using Language Manager

```python
from init_selenium.init_driver import DriverInit, LanguageManager

# Create a LanguageManager instance for Spanish
spanish = LanguageManager("Spanish")

# Initialize driver with custom language
driver_init = DriverInit(language=spanish)
driver, wait = driver_init.create_driver()

try:
    driver.get("https://www.google.com/")
    # The browser will use Spanish language settings
finally:
    driver.quit()
```

### Gmail Login Helper

```python
from init_selenium.init_driver import DriverInit

driver_init = DriverInit()
driver, wait = driver_init.create_driver()

try:
    driver_init.pass_gmail_login(
        driver,
        wait,
        mail="your_email@gmail.com",
        password="your_password",
        phone="your_phone_number"
    )
    # Now you're logged in to Gmail
finally:
    driver.quit()
```

## DriverInit Class

### Initialization Parameters

```python
DriverInit(
    drivers_route: Optional[str] = None,
    user_agent: Optional[str] = None,
    language: Tuple[str, str] | LanguageManager = ENGLISH_USA,
    force_install: bool = False
)
```

- `drivers_route`: Custom path to ChromeDriver (auto-installed if not provided)
- `user_agent`: Custom user agent string
- `language`: Language settings as a tuple or LanguageManager instance (default: ENGLISH_USA)
- `force_install`: Force ChromeDriver installation (default: False)

### create_driver() Method

```python
create_driver(
    window_size: str = WINDOW_MAX,
    window_position: Tuple[int, int] = (0, 0),
    sandbox_enabled: bool = True,
    wait_time: int = 20,
    notification_level: int = 2,
    save_passwords: bool = False,
    camouflage: bool = True,
    web_security: bool = False,
    undetectable: bool = False,
    cookies: Optional[Dict[str, str]] = None,
    initial_url: Optional[str] = None,
    save_user_agent_data: bool = True
) -> Tuple[WebDriver, WebDriverWait]
```

- `window_size`: Predefined size ('max', 'min') or custom 'WIDTHxHEIGHT' string
- `window_position`: (x, y) coordinates for window position
- `sandbox_enabled`: Enable Chrome sandbox
- `wait_time`: Timeout for WebDriverWait in seconds
- `notification_level`: Chrome notification level (0=default, 1=ask, 2=block)
- `save_passwords`: Allow Chrome to save passwords
- `camouflage`: Hide Selenium automation traces
- `web_security`: Disable web security if True
- `undetectable`: Use undetected_chromedriver
- `cookies`: Dictionary of cookies to inject
- `initial_url`: URL to load on browser start
- `save_user_agent_data`: Save user agent data to JSON file

## Requirements

- Python 3.8+
- selenium
- webdriver-manager
- undetected-chromedriver
- fake-useragent (optional, for random user agent generation)

## Known Limitations

- **Chrome/Chromium Browsers Only** - No support for Firefox, Edge, or other browsers
- **Platform Support** - Primarily tested on Windows and Linux
- **External Dependencies** - Requires Chrome/Chromium browser installed
- **Gmail Login** - The Gmail login helper may require updates if Google changes their login flow

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE.txt) for details.

MIT License

---
