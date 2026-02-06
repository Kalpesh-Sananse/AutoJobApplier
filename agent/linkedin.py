
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class LinkedInBot:
    def __init__(self, browser, secrets, config, ai_handler):
        self.browser = browser
        self.driver = browser.driver
        self.email = secrets['linkedin']['username']
        self.password = secrets['linkedin']['password']
        self.config = config
        self.ai_handler = ai_handler
        self.logger = logging.getLogger("AutoJobApplier.LinkedIn")

    def login(self):
        self.logger.info("Logging into LinkedIn...")
        self.browser.get("https://www.linkedin.com/login")
        
        try:
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(self.email)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            
            # Simple check for login success (e.g., search bar presence)
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "global-nav-typeahead"))
                )
                self.logger.info("Login successful.")
            except TimeoutException:
                self.logger.warning("Login verification needed! Please solve the CAPTCHA/Code in the browser.")
                self.logger.warning("Waiting 300 seconds for manual login...")
                # Wait up to 5 minutes for user to solve it
                WebDriverWait(self.driver, 300).until(
                    EC.presence_of_element_located((By.ID, "global-nav-typeahead"))
                )
                self.logger.info("Login successful after manual verification.")

        except TimeoutException:
            self.logger.error("Login timed out. Did you solve the captcha?")
            raise Exception("Login failed")

    def search_jobs(self):
        keywords = self.config['search_parameters']['keywords']
        location = self.config['search_parameters']['location']
        # Construct URL
        url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}"
        if self.config['search_parameters']['easy_apply']:
            url += "&f_AL=true" # Easy Apply filter
            
        self.logger.info(f"Navigating to search URL: {url}")
        self.browser.get(url)
        time.sleep(3)

    def apply_loop(self):
        """
        Iterates through job listings and attempts to apply.
        """
        try:
            # Locate the jobs list container
            job_list_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
        except:
            self.logger.warning("Could not find job list container. Might be different layout.")
            return

        while True:
            # Get current view of jobs
            job_listings = self.driver.find_elements(By.CLASS_NAME, "job-card-container")
            self.logger.info(f"Scanning {len(job_listings)} jobs in current view...")
            
            for i, job in enumerate(job_listings):
                try:
                    # Scroll job into view
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", job)
                    time.sleep(1)
                    
                    # Click job
                    try:
                        job.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", job)
                        
                    time.sleep(2)
                    
                    # Check for Easy Apply button
                    try:
                        # Look for the specific Easy Apply button
                        easy_apply_btn = self.driver.find_element(By.CLASS_NAME, "jobs-apply-button--top-card")
                        if "Easy Apply" in easy_apply_btn.text:
                            easy_apply_btn.click()
                            self.logger.info("Clicked Easy Apply.")
                            time.sleep(1)
                            self.handle_application_modal()
                        else:
                            self.logger.info("Not an Easy Apply job (likely external).")
                    except NoSuchElementException:
                        self.logger.info("Already applied or button not found.")
                        
                except Exception as e:
                    self.logger.error(f"Error processing job {i}: {e}")
                    self.driver.save_screenshot(f"error_job_{i}.png")
            
            # Scroll down the list to load more (simplified)
            self.logger.info("Scrolling down to load more jobs...")
            self.driver.execute_script("arguments[0].scrollTop += 500;", job_list_container)
            time.sleep(3)
            # Break if end of list reached (logic needed here, but keeping loop simple for now)
            # for demo purposes, we might stop after one pass or keep trying
            break # stopping after one batch for safety debugging

    def handle_application_modal(self):
        """
        Handles the multi-step application modal.
        """
        max_steps = 15
        step = 0
        
        while step < max_steps:
            step += 1
            time.sleep(1)
            
            # Check for "Submit application" button
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            submit_btn = next((b for b in buttons if "Submit application" in b.text), None)
            review_btn = next((b for b in buttons if "Review" in b.text), None)
            next_btn = next((b for b in buttons if "Next" in b.text), None)
            
            if submit_btn:
                self.logger.info("Found Submit button!")
                submit_btn.click() # ENABLED SUBMISSION
                self.logger.info("Submitted Application!")
                time.sleep(3)
                self.close_modal() # Close success modal
                return
            
            # Handle Form Fields before clicking Next/Review
            self.fill_form_fields()

            if review_btn:
                review_btn.click()
                self.logger.info("Clicked Review.")
                continue

            if next_btn:
                next_btn.click()
                self.logger.info("Clicked Next.")
                continue
                
            # If no buttons found that we recognize, or errors
            # self.logger.warning("Stuck in modal, breaking out.")
            # break
            
        self.close_modal()

    def fill_form_fields(self):
        """
        Scans for inputs and uses AI to fill them.
        Handles: Text Inputs, Radio Buttons, Select Dropdowns.
        """
        # 1. Text Inputs
        text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='tel'], input[type='email'], input[type='number'], textarea")
        for inp in text_inputs:
            if inp.get_attribute("value"):
                continue # Already filled
            
            label_txt = self.get_label_for_element(inp)
            field_type = "text"
            
            # Heuristics for field type
            inp_type = inp.get_attribute("type")
            outer_html = inp.get_attribute("outerHTML").lower()
            label_lower = label_txt.lower()
            
            if "phone" in label_lower or "mobile" in label_lower or inp_type == "tel":
                field_type = "numeric" # Phone numbers are numeric-ish
            elif "years" in label_lower or "experience" in label_lower or inp_type == "number":
                field_type = "numeric"
            
            # Avoid filling "skills" into Phone/Mobile fields ??
            # The AI prompt execution will handle "Output only a number" if field_type is numeric.
            
            answer = self.ai_handler.generate_answer(label_txt, field_type=field_type)
            # Remove non-digits for phone if needed, but AI should handle it
            inp.send_keys(answer)
            time.sleep(0.5)

        # 2. Radio Buttons (Fieldsets)
        fieldsets = self.driver.find_elements(By.CSS_SELECTOR, "fieldset")
        for fieldset in fieldsets:
            try:
                legend = fieldset.find_element(By.CSS_SELECTOR, "legend").text
                radios = fieldset.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if not radios:
                    continue
                
                # Check if one is already selected
                if any(r.is_selected() for r in radios):
                    continue

                # Ask AI which option to pick
                options = []
                for r in radios:
                    try:
                        # label is usually a sibling or parent
                        lbl = r.find_element(By.XPATH, "./following-sibling::label").text
                        options.append(lbl)
                    except:
                        options.append("Unknown")
                
                question_with_options = f"{legend} Options: {', '.join(options)}"
                choice = self.ai_handler.generate_answer(question_with_options, field_type="text")
                
                # Try to click the best match
                for i, opt in enumerate(options):
                    if opt.lower() in choice.lower():
                        self.driver.execute_script("arguments[0].click();", radios[i])
                        break
            except Exception as e:
                self.logger.warning(f"Error handling radio button: {e}")

        # 3. Dropdowns (Select)
        selects = self.driver.find_elements(By.TAG_NAME, "select")
        for sel in selects:
            try:
                label_txt = self.get_label_for_element(sel)
                # Get options
                options = [o.text for o in sel.find_elements(By.TAG_NAME, "option")]
                
                question_with_options = f"{label_txt} Options: {', '.join(options)}"
                choice = self.ai_handler.generate_answer(question_with_options, field_type="text")
                
                # Select match
                from selenium.webdriver.support.ui import Select
                dropdown = Select(sel)
                # Try to match text
                found = False
                for opt in options:
                    if opt.lower() in choice.lower():
                        dropdown.select_by_visible_text(opt)
                        found = True
                        break
                if not found and len(options) > 1:
                    dropdown.select_by_index(1) # Default to first real option
            except Exception as e:
                self.logger.warning(f"Error handling dropdown: {e}")

    def get_label_for_element(self, element):
        try:
            # Try aria-label first
            label = element.get_attribute("aria-label")
            if label: return label
            
            # Try ID matching
            my_id = element.get_attribute("id")
            if my_id:
                label_elem = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{my_id}']")
                return label_elem.text
        except:
            pass
        return "Unknown Question"

    def close_modal(self):
        try:
            close_btn = self.driver.find_element(By.CLASS_NAME, "artdeco-modal__dismiss")
            close_btn.click()
            time.sleep(1)
            # Confirm discard if needed
            try:
                discard_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Discard')]")
                discard_btn.click()
            except:
                pass
        except:
            pass

