import unittest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src.init_selenium.init_driver import create_driver, ENGLISH_USA
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestDriverManager(unittest.TestCase):
    def setUp(self):
        """Initialize the driver before each test"""
        self.driver, self.wait = create_driver(
            window_size="1920x1080",
            language=ENGLISH_USA,
            camouflage=True,
            notification_level=2
        )

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def test_basic_driver_functionality(self):
        """Test if driver can navigate and find elements"""
        self.driver.get("https://www.python.org")
        self.assertIn("Python", self.driver.title)

    def test_website_scraping(self):
        """Test scraping Python.org's latest news"""
        try:
            # Navigate to Python.org
            self.driver.get("https://www.python.org")

            # Wait for and find the latest news section
            news_items = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.get-started-widget")
                )
            )

            logger.info(msg=news_items.text)

        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise

    def test_driver_options(self):
        """Test various driver options"""
        try:
            # Test user agent
            self.driver.get("https://www.whatismybrowser.com/detect/what-is-my-user-agent/")
            user_agent = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#detected_value")
                )
            )
            self.assertTrue(user_agent.text, "User agent should be detected")
            logger.info(f"Detected User Agent: {user_agent.text}")

        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise

    def test_cookies_handling(self):
        """Test cookie handling capabilities"""
        test_cookie = {
            "name": "test_cookie",
            "value": "test_value",
            "domain": "python.org"
        }

        try:
            self.driver.get("https://www.python.org")
            self.driver.add_cookie(test_cookie)

            # Verify cookie was set
            cookie = self.driver.get_cookie("test_cookie")
            self.assertIsNotNone(cookie)
            self.assertEqual(cookie["value"], "test_value")

        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise


if __name__ == '__main__':
    unittest.main(verbosity=2)
