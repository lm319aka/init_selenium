import os.path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import chromedriver_autoinstaller
import undetected_chromedriver as uc
import json
import logging
from typing import Optional, Tuple, Dict
import time
from webdriver_manager.core.manager import DriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import *


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
        self.lang = lang.title()
        self.lang_file_path = "./driver_info/langs.json"
        self.langcode = self.get_language_code()

    def get_language_code(self) -> Tuple[str, str]:
        """
        Retrieves language code from JSON configuration
        Returns tuple of (language_code, language_code)
        """
        try:
            with open(self.lang_file_path, "r", encoding="utf-8") as lang_file:
                lang_data = json.load(lang_file)
                lang_label = lang_data["langs"].get(self.lang)

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


class DriverInit:

    def __init__(self,
                 drivers_route: Optional[str] = None,
                 user_agent: Optional[str] = None,
                 language: Tuple[str, str] | LanguageManager = ENGLISH_USA,
                 force_install: bool = False
                 ):
        self.drivers_route = drivers_route
        self.user_agent = user_agent
        if isinstance(language, LanguageManager):
            self.language = language.langcode
        else:
            self.language = language
        self.force_install = force_install
        self.user_agent_json = "./driver_info/driver_data.json"

    @staticmethod
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

    def create_driver(self,
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
        driver_path = self.install_chrome_driver() if self.force_install or not self.drivers_route else self.drivers_route

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
        if self.user_agent:
            options.add_argument(f"user-agent={self.user_agent}")
        else:
            if os.path.exists(self.user_agent_json):
                with open(self.user_agent_json, "r") as ua_file:
                    self.user_agent = json.loads(ua_file.read())
                options.add_argument(f"user-agent={self.user_agent}")

            else:
                raise FileNotFoundError("No driver_data.json file found")

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
                    "intl.accept_languages": list(self.language),
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

            if save_user_agent_data:
                with open(self.user_agent_json, "w") as ua_file:
                    ua_file.write(json.dumps(self.user_agent))

            logger.info("Chrome WebDriver initialized successfully")
            return driver, wait

        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise

    @staticmethod
    def pass_gmail_login(new_driver,
                         new_wt,
                         mail: str,
                         password: str,
                         phone: str):

        # wt.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input[name="identifier"]'))).send_keys(mail)
        # time.sleep(1)
        # wt.until(ec.presence_of_element_located((By.XPATH, '//span[.="Siguiente"]'))).click()
        # time.sleep(1)
        # wt.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'input[name="Passwd"]'))).send_keys(password)
        # time.sleep(1)
        # wt.until(ec.presence_of_element_located((By.XPATH, '//span[.="Siguiente"]'))).click()
        # time.sleep(2)
        try:
            # Replace 'input_selector' with the actual selector for Gemini AI's input box.
            mail_box = new_driver.find_element(By.CSS_SELECTOR, 'input[name="identifier"]')
            mail_box.send_keys(mail)
            mail_box.send_keys(Keys.RETURN)  # Simulate pressing Enter to submit the query.
            time.sleep(3)  # Wait for page to respond.

            # Find the password input box and enter the password.
            pwd_box = new_wt.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="Passwd"]')))
            pwd_box.send_keys(password)
            pwd_box.send_keys(Keys.RETURN)
            time.sleep(3)  # Wait for page to respond.
            # input("Press Enter to continue...")
            # Telephone input box
            tp_box = new_wt.until(ec.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="tel"]')))
            tp_box.send_keys(phone)
            tp_box.send_keys(Keys.RETURN)

            # check if too many attempts
            time.sleep(3)
            try:
                new_driver.find_element(By.XPATH, '//span[.="Too many attempts. Please try again later."]')
                # print("too many attempts")
                # time.sleep(5)
                new_driver.quit()
                raise Exception("Too many attempts")
                # return
            except NoSuchElementException or InvalidSelectorException:
                pass

            # Confirmation code input box
            code = input("Enter confirmation code: ")

            # send button xpath (just in case): //button[.="Enviar"]
            print("ok")
            time.sleep(2)

            code_box = new_wt.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input#idvPin')))
            code_box.send_keys(code)
            code_box.send_keys(Keys.RETURN)

            time.sleep(2)

            while 1:
                curr_url = new_driver.current_url
                # check if we are in captcha page
                print("do captcha")
                print("curr:", curr_url)

                try:
                    url_part = curr_url[:29]
                except IndexError:
                    break

                print("part:", url_part)
                print(("https://www.google.com/sorry/" == url_part) or ("https://accounts.google.com/v" == url_part))

                if len(curr_url) < 29:
                    break

                if ("https://www.google.com/sorry/" == url_part) or ("https://accounts.google.com/v" == url_part):
                    time.sleep(1)
                else:
                    # confirm we are not in captcha
                    time.sleep(1)
                    if ("https://www.google.com/sorry/" != url_part) or ("https://accounts.google.com/v" != url_part):
                        break

            try:
                # cancel saving any info about our account
                new_driver.find_element(By.XPATH, '//button[.="Cancelar"]').click()
            except NoSuchElementException or InvalidSelectorException or ElementNotInteractableException:
                pass
            try:
                # not follow suggestions
                new_driver.find_element(By.XPATH, '//button[.="Ahora no"]').click()
            except NoSuchElementException or InvalidSelectorException:
                pass

        except Exception as e:
            print(f"Error interacting with page: {e}")
        # input("Press Enter to continue...")

        # new_driver.quit()
        return new_driver, new_wt


if __name__ == "__main__":
    try:
    # if True:
        initializer = DriverInit(language=LanguageManager("spanish"))
        _driver, _wait = initializer.create_driver(
            window_size=WINDOW_MAX,
            undetectable=True
        )
        _driver.get("https://www.google.com/")
        input("Press Enter to continue...")
        _driver.quit()

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
    else:
        _driver.quit()
