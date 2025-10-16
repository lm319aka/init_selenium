import sys
# your path in here
sys.path.append("C:\\CODE_FOLDER\\init_selenium\\src")
import unittest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from init_selenium.init_driver import DriverInit, LanguageManager, WINDOW_MAX, ENGLISH_USA

# Configure logging with a more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestDriverManager(unittest.TestCase):
    driver = None
    wait = None

    def setUp(self):
        """Initialize the driver before each test. Adapt to several possible return types."""
        if DriverInit is None:
            self.skipTest("No compatible driver factory available in src.init_selenium.init_driver")

        # prefer new API (DriverInit). Build initializer with language if applicable.
        try:
            # Create a LanguageManager instance for English USA
            lang_manager = LanguageManager(ENGLISH_USA)
            # Initialize driver with custom language
            driver_init = DriverInit(language=lang_manager)
            result = driver_init.create_driver(window_size=WINDOW_MAX, undetectable=True)
        except Exception as e:
            # If driver cannot be created in this environment, skip tests
            self.skipTest(f"Could not create driver: {e}")

        # Normalize different possible return shapes:
        # - (driver, wait)
        # - object with .driver and .wait
        # - plain webdriver -> create WebDriverWait
        if isinstance(result, tuple) and len(result) >= 1:
            self.driver = result[0]
            if len(result) >= 2:
                self.wait = result[1]
        elif hasattr(result, "driver") and hasattr(result, "wait"):
            self.driver = result.driver
            self.wait = result.wait
        else:
            # assume it's a webdriver instance
            self.driver = result
            try:
                self.wait = WebDriverWait(self.driver, 10)
            except Exception as e:
                logger.error("Failed to create WebDriverWait: %s", e)

    def tearDown(self):
        """Clean up after each test"""
        try:
            if getattr(self, "driver", None):
                self.driver.quit()
        except Exception:
            pass

    def test_basic_driver_functionality(self):
        """Test if driver can navigate and basic title check"""
        try:
            self.driver.get("https://example.com")
            title = self.driver.title or ""
            self.assertTrue(len(title) > 0, "Page should have a title")
        except WebDriverException as e:
            self.skipTest(f"WebDriver not usable in this environment: {e}")

    def test_find_element_on_python_org(self):
        """Try to load python.org and find a stable element"""
        try:
            self.driver.get("https://www.python.org")
            wait = self.wait or WebDriverWait(self.driver, 10)
            elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a#start-shell, div.introduction"))
            )
            logger.info("Found element text: %s", getattr(elem, "text", "")[:200])
            self.assertIsNotNone(elem)
        except Exception as e:
            logger.error("Test failed: %s", e)
            raise

    def test_user_agent_detection_page(self):
        """Visit a user-agent detection page and assert presence of a detected value"""
        try:
            self.driver.get("https://www.whatismybrowser.com/detect/what-is-my-user-agent/")
            wait = self.wait or WebDriverWait(self.driver, 10)
            ua_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#detected_value, .detected-result")))
            self.assertTrue(ua_elem.text and len(ua_elem.text) > 5, "User agent should be present")
            logger.info("Detected user agent: %s", ua_elem.text.strip())
        except Exception as e:
            logger.error("Test failed: %s", e)
            raise

    def test_cookies_handling(self):
        """Test cookie handling capabilities on example.com (stable domain)"""
        try:
            self.driver.get("https://example.com")
            test_cookie = {"name": "test_cookie", "value": "test_value"}
            # set cookie for current domain
            self.driver.add_cookie(test_cookie)
            cookie = self.driver.get_cookie("test_cookie")
            self.assertIsNotNone(cookie)
            self.assertEqual(cookie.get("value"), "test_value")
        except Exception as e:
            logger.error("Test failed: %s", e)
            raise

if __name__ == "__main__":
    unittest.main()