import asyncio
import logging
import sys
from utils import setup_logger, load_config, load_secrets
from browser_playwright import PlaywrightBrowser
from linkedin_playwright import LinkedInBotPlaywright
from ai_handler import AIHandler

async def main():
    # Setup
    logger = setup_logger()
    logger.info("🚀 Starting LinkedIn Auto Job Applier (Playwright Edition)...")

    # Load Configuration
    try:
        config = load_config()
        secrets = load_secrets()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Validating Credentials
    if secrets['linkedin']['password'] == "your_password" or secrets['linkedin']['username'] == "your_email@example.com":
        logger.error("Please update 'agent/secrets.yaml' with your actual LinkedIn credentials.")
        sys.exit(1)

    # Initialize AI
    try:
        resume_path = secrets['paths']['resume_path']
        logger.info(f"Loading resume from: {resume_path}")
        
        resume_text = ""
        if resume_path.lower().endswith('.pdf'):
            try:
                from pypdf import PdfReader
                reader = PdfReader(resume_path)
                for page in reader.pages:
                    resume_text += page.extract_text() + "\n"
            except ImportError:
                logger.error("pypdf is not installed. Run `pip install pypdf`.")
        else:
            # Load text/markdown resume
            with open(resume_path, 'r', errors='ignore') as f:
                resume_text = f.read()
                
        if not resume_text.strip():
            logger.warning("Resume content appeared empty.")

    except Exception as e:
        logger.warning(f"Could not read resume file: {e}. AI will work with limited context.")
        resume_text = ""

    # Inject User Profile Built from the Frontend UI
    try:
        import os, json
        profile_path = "user_profile.json"
        # Since this script runs from root or agent, safely check both
        if not os.path.exists(profile_path):
            profile_path = os.path.join("..", "user_profile.json")
            
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                profile_data = json.load(f)
            
            # Format nicely
            formatted_profile = "=== CANDIDATE PROFILE (PRIMARY SOURCE OF TRUTH) ===\n"
            for k, v in profile_data.items():
                if v and str(v).strip():
                    formatted_profile += f"{k.upper()}:\n{v}\n\n"
            
            resume_text = formatted_profile + "=== ORIGINAL RESUME ===\n" + resume_text
            logger.info("Successfully loaded User Profile context into the AI.")
        else:
            logger.info("No user_profile.json found. Relying solely on resume context.")
    except Exception as e:
        logger.warning(f"Failed to load user profile: {e}")

    ai_handler = AIHandler(secrets, resume_text)

    # Initialize Browser
    browser = PlaywrightBrowser(headless=config['settings']['run_in_background'])
    
    try:
        await browser.initialize()
        
        # Initialize Bot
        bot = LinkedInBotPlaywright(browser.page, secrets, config, ai_handler)
        
        await bot.login()
        await browser.save_session()  # Save session after successful login
        
        await bot.search_jobs()
        await bot.apply_to_jobs()
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Closing browser...")
        await browser.close()
        logger.info("✅ Done.")

if __name__ == "__main__":
    asyncio.run(main())
