import asyncio
import logging
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import os

class PlaywrightBrowser:
    def __init__(self, headless=False, session_file="browser_session.json"):
        self.logger = logging.getLogger("AutoJobApplier.Browser")
        self.headless = headless
        self.session_file = session_file
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        """Initialize the browser with anti-detection and session management."""
        self.playwright = await async_playwright().start()
        
        # Launch browser with anti-detection arguments
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Try to load saved session
        if os.path.exists(self.session_file):
            self.logger.info(f"Loading saved session from {self.session_file}")
            self.context = await self.browser.new_context(storage_state=self.session_file)
        else:
            self.logger.info("No saved session found, creating new context")
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
        
        self.page = await self.context.new_page()
        self.logger.info("Browser initialized successfully.")

    async def save_session(self):
        """Save the current browser session for reuse."""
        if self.context:
            await self.context.storage_state(path=self.session_file)
            self.logger.info(f"Session saved to {self.session_file}")

    async def close(self):
        """Close the browser and save session."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("Browser closed.")
