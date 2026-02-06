
import logging
import sys
from utils import setup_logger, load_config, load_secrets
from browser import Browser
from linkedin import LinkedInBot
from ai_handler import AIHandler

def main():
    # Setup
    logger = setup_logger()
    logger.info("Starting LinkedIn Auto Job Applier...")

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

    ai_handler = AIHandler(secrets, resume_text)

    # Initialize Browser
    browser = Browser(headless=config['settings']['run_in_background'])

    # Initialize Bot
    bot = LinkedInBot(browser, secrets, config, ai_handler)

    try:
        bot.login()
        bot.search_jobs()
        bot.apply_loop()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        logger.info("Closing browser...")
        browser.close()
        logger.info("Done.")

if __name__ == "__main__":
    main()
