"""
Browser automation service using Selenium
"""

import logging
import uuid
import time
from datetime import datetime
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

logger = logging.getLogger(__name__)


class BrowserAutomationService:
    """Service for browser automation with Selenium"""

    # Singleton instance
    _instance = None
    _driver = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserAutomationService, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def create_driver(browser_type: str = "chrome", headless: bool = True):
        """Create a Selenium WebDriver instance"""
        try:
            if browser_type.lower() == "chrome":
                options = webdriver.ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--start-maximized")
                options.add_argument(
                    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )

                driver = webdriver.Chrome(options=options)
            elif browser_type.lower() == "firefox":
                options = webdriver.FirefoxOptions()
                if headless:
                    options.add_argument("--headless")

                driver = webdriver.Firefox(options=options)
            else:
                raise ValueError(f"Unsupported browser type: {browser_type}")

            logger.info(f"Created {browser_type} driver (headless={headless})")
            return driver
        except Exception as e:
            logger.error(f"Error creating driver: {str(e)}")
            raise ValueError(f"Failed to create browser driver: {str(e)}")

    @staticmethod
    def navigate_to_url(driver, url: str, timeout: int = 10) -> bool:
        """Navigate to a URL"""
        try:
            driver.get(url)
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {str(e)}")
            return False

    @staticmethod
    def wait_for_element(
        driver, selector: str, by: By = By.CSS_SELECTOR, timeout: int = 10
    ) -> bool:
        """Wait for element to be present"""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            logger.info(f"Element found: {selector}")
            return True
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {selector}")
            return False
        except Exception as e:
            logger.error(f"Error waiting for element: {str(e)}")
            return False

    @staticmethod
    def click_element(driver, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Click an element"""
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by, selector))
            )
            element.click()
            logger.info(f"Clicked element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {str(e)}")
            return False

    @staticmethod
    def type_text(driver, selector: str, text: str, by: By = By.CSS_SELECTOR) -> bool:
        """Type text into an element"""
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )
            element.clear()
            element.send_keys(text)
            logger.info(f"Typed text into {selector}")
            return True
        except Exception as e:
            logger.error(f"Error typing into {selector}: {str(e)}")
            return False

    @staticmethod
    def select_option(
        driver, selector: str, value: str, by: By = By.CSS_SELECTOR
    ) -> bool:
        """Select an option from dropdown"""
        try:
            from selenium.webdriver.support.select import Select

            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )
            select = Select(element)
            select.select_by_value(value)
            logger.info(f"Selected {value} from {selector}")
            return True
        except Exception as e:
            logger.error(f"Error selecting option {value}: {str(e)}")
            return False

    @staticmethod
    def upload_file(driver, selector: str, file_path: str, by: By = By.CSS_SELECTOR) -> bool:
        """Upload a file"""
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )
            element.send_keys(file_path)
            logger.info(f"Uploaded file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return False

    @staticmethod
    def take_screenshot(driver, path: str) -> bool:
        """Take a screenshot"""
        try:
            driver.save_screenshot(path)
            logger.info(f"Screenshot saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {str(e)}")
            return False

    @staticmethod
    def wait(duration_ms: int) -> None:
        """Wait for specified duration"""
        time.sleep(duration_ms / 1000.0)
        logger.info(f"Waited {duration_ms}ms")

    @staticmethod
    def close_driver(driver) -> None:
        """Close the driver"""
        try:
            if driver:
                driver.quit()
                logger.info("Driver closed")
        except Exception as e:
            logger.error(f"Error closing driver: {str(e)}")

    @staticmethod
    def get_page_source(driver) -> Optional[str]:
        """Get page source"""
        try:
            return driver.page_source
        except Exception as e:
            logger.error(f"Error getting page source: {str(e)}")
            return None

    @staticmethod
    def get_current_url(driver) -> Optional[str]:
        """Get current URL"""
        try:
            return driver.current_url
        except Exception as e:
            logger.error(f"Error getting current URL: {str(e)}")
            return None

    @staticmethod
    def execute_script(driver, script: str) -> Optional[str]:
        """Execute JavaScript"""
        try:
            result = driver.execute_script(script)
            logger.info(f"Executed script, result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")
            return None

    @staticmethod
    def switch_to_frame(driver, selector: str, by: By = By.CSS_SELECTOR) -> bool:
        """Switch to iframe"""
        try:
            frame = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )
            driver.switch_to.frame(frame)
            logger.info(f"Switched to frame: {selector}")
            return True
        except Exception as e:
            logger.error(f"Error switching to frame: {str(e)}")
            return False

    @staticmethod
    def switch_to_default_content(driver) -> None:
        """Switch back to main content"""
        try:
            driver.switch_to.default_content()
            logger.info("Switched to default content")
        except Exception as e:
            logger.error(f"Error switching to default content: {str(e)}")

    @staticmethod
    def accept_alert(driver) -> bool:
        """Accept an alert"""
        try:
            alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
            alert.accept()
            logger.info("Accepted alert")
            return True
        except Exception as e:
            logger.error(f"Error accepting alert: {str(e)}")
            return False

    @staticmethod
    def find_element_text(driver, selector: str, by: By = By.CSS_SELECTOR) -> Optional[str]:
        """Find element and get text"""
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, selector))
            )
            return element.text
        except Exception as e:
            logger.error(f"Error finding element text: {str(e)}")
            return None
