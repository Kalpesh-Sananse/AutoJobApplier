
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time

class Browser:
    def __init__(self, headless=False):
        self.logger = logging.getLogger("AutoJobApplier.Browser")
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36")
        
        # Initialize Driver
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
            self.logger.info("Browser initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise e

    def get(self, url):
        self.driver.get(url)

    def close(self):
        self.driver.quit()

    def wait(self, seconds):
        time.sleep(seconds)
