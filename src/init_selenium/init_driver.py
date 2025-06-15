from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import chromedriver_autoinstaller
import undetected_chromedriver as uc
import json
import logging
from typing import Optional, Tuple, Dict

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants for window sizes and language preferences
WINDOW_MIN = "min"
WINDOW_MAX = "max"
SPANISH = ("es-ES", "es")
ENGLISH_USA = ("en", "en_US")


class LanguageManager:
    """Handles browser language settings using a JSON configuration file"""

    def __init__(self, lang: str):
        self.lang = lang
        self.lang_file_path = "driver_info/langs.json"

    def get_language_code(self) -> Tuple[str, str]:
        """
        Retrieves language code from JSON configuration
        Returns tuple of (language_code, language_code)
        """
        try:
            with open(self.lang_file_path, "r", encoding="utf-8") as lang_file:
                lang_data = json.load(lang_file)
                lang_label = lang_data["langs"]["langs"].get(self.lang)

                if not lang_label:
                    raise KeyError(f"Language '{self.lang}' not found in configuration")

                # Extract primary language code
                primary_lang = lang_label.split(',')[0].strip()
                return primary_lang, primary_lang

        except FileNotFoundError:
            logger.error(f"Language configuration file not found: {self.lang_file_path}")
            raise
        except json.JSONDecodeError:
            logger.error("Invalid JSON in language configuration file")
            raise


def install_chrome_driver() -> str:
    """Installs and returns path to the latest compatible ChromeDriver"""
    logger.info("Installing ChromeDriver...")
    try:
        driver_path = chromedriver_autoinstaller.install()
        logger.info(f"ChromeDriver installed successfully at: {driver_path}")
        return driver_path
    except Exception as e:
        logger.error(f"Failed to install ChromeDriver: {e}")
        raise


def create_driver(
        drivers_route: Optional[str] = None,
        user_agent: Optional[str] = None,
        window_size: str = WINDOW_MAX,
        window_position: Tuple[int, int] = (0, 0),
        sandbox_enabled: bool = True,
        wait_time: int = 20,
        notification_level: int = 2,
        language: Tuple[str, str] = ENGLISH_USA,
        save_passwords: bool = False,
        camouflage: bool = True,
        web_security: bool = False,
        force_install: bool = False,
        undetectable: bool = False,
        cookies: Optional[Dict[str, str]] = None,
        initial_url: Optional[str] = None
) -> Tuple[webdriver.Chrome, WebDriverWait]:
    """
    Creates and configures a Chrome WebDriver instance with specified options
    Returns tuple of (WebDriver, WebDriverWait)
    """
    logger.info("Initializing Chrome WebDriver...")

    # Validate notification level
    if notification_level not in [0, 1, 2]:
        logger.error(f"Invalid notification level: {notification_level}")
        raise ValueError("Notification level must be 0, 1, or 2")

    # Install or use existing ChromeDriver
    driver_path = install_chrome_driver() if force_install or not drivers_route else drivers_route

    # Configure Chrome options
    options = Options()
    window_dimensions = (None, None)

    # Configure window size
    if window_size == WINDOW_MAX:
        options.add_argument("--start-maximized")
    elif window_size == WINDOW_MIN:
        options.add_argument("--headless")
    elif "x" in window_size:
        try:
            width, height = map(int, window_size.split("x"))
            window_dimensions = (width, height)
        except ValueError:
            logger.error(f"Invalid window size format: {window_size}")
            raise ValueError("Window size must be 'max', 'min', or 'WIDTHxHEIGHT'")

    # Add Chrome options
    if user_agent:
        options.add_argument(f"user-agent={user_agent}")
    if not web_security:
        options.add_argument("--disable-web-security")
    if not sandbox_enabled:
        options.add_argument("--no-sandbox")

    # Basic security and performance options
    chrome_arguments = [
        "--disable-extensions",
        "--disable-notifications",
        "--ignore-certificate-errors",
        "--log-level=3",
        "--allow-running-insecure-content",
        "--no-default-browser-check",
        "--no-first-run",
        "--no-proxy-server"
    ]
    for arg in chrome_arguments:
        options.add_argument(arg)

    # Anti-detection measures
    if camouflage:
        options.add_argument("--disable-blink-features=AutomationControlled")

    # Initialize driver
    try:
        if undetectable:
            # options.add_argument("user-data-dir=./")
            # options.add_experimental_option("detach", True)
            # options.add_experimental_option("excludeSwitches", ["enable-logging"])
            driver = uc.Chrome(options=options, driver_executable_path=driver_path)
        else:
            # Experimental options
            options.add_experimental_option("excludeSwitches", [
                "enable-automation",
                "ignore-certificate-errors",
                "enable-logging"
            ])

            # Browser preferences
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": notification_level,
                "intl.accept_languages": list(language),
                "credentials_enable_service": save_passwords
            })

            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)

        # Configure window dimensions if specified
        if all(window_dimensions):
            driver.set_window_size(*window_dimensions)
            driver.set_window_position(*window_position)

        wait = WebDriverWait(driver, wait_time)

        # Handle initial URL and cookies
        if initial_url:
            logger.info(f"Navigating to initial URL: {initial_url}")
            driver.get(initial_url)

        if cookies and cookies != {}:
            logger.info("Setting cookies...")
            for cookie in cookies:
                driver.add_cookie(cookie)

        logger.info("Chrome WebDriver initialized successfully")
        return driver, wait

    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        raise


if __name__ == "__main__":
    try:
        _driver, _wait = create_driver(
            window_size=WINDOW_MAX,
            language=ENGLISH_USA
        )
        _driver.get("https://www.google.com/")
        input("Press Enter to continue...")
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    else:
        _driver.quit()

