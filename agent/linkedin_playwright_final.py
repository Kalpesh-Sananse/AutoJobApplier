import asyncio
import logging
import time
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

class LinkedInBotPlaywright:
    def __init__(self, page: Page, secrets, config, ai_handler):
        self.page = page
        self.email = secrets['linkedin']['username']
        self.password = secrets['linkedin']['password']
        self.resume_path = secrets['paths']['resume_path']
        self.config = config
        self.ai_handler = ai_handler
        self.logger = logging.getLogger("AutoJobApplier.LinkedIn")

    async def login(self):
        """Login to LinkedIn with verification code support."""
        self.logger.info("Checking login status...")
        
        try:
            # First check if already logged in (from saved session)
            try:
                await self.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(2)
                
                # Check if we're actually on the feed (logged in)
                current_url = self.page.url
                if '/feed' in current_url:
                    self.logger.info("✅ Already logged in from saved session!")
                    
                    # Close any onboarding modals
                    try:
                        close_btns = await self.page.query_selector_all('button[aria-label="Dismiss"]')
                        for btn in close_btns:
                            await btn.click()
                            await asyncio.sleep(0.5)
                    except:
                        pass
                    return
            except:
                # Feed didn't load, need to login
                pass
            
            # Not logged in, proceed with login
            self.logger.info("Not logged in, proceeding with login...")
            await self.page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            # Fill credentials
            await self.page.fill('#username', self.email)
            await self.page.fill('#password', self.password)
            await self.page.click('button[type="submit"]')
            await asyncio.sleep(3)
            
            # Check current URL to determine if logged in or verification needed
            current_url = self.page.url
            
            if '/feed' in current_url or '/check/add-phone' in current_url:
                # Successfully logged in
                self.logger.info("✅ Login successful!")
                
                # Close any onboarding modals
                try:
                    close_btns = await self.page.query_selector_all('button[aria-label="Dismiss"]')
                    for btn in close_btns:
                        await btn.click()
                        await asyncio.sleep(0.5)
                except:
                    pass
                return
                
            # Check if we're on verification page
            if '/checkpoint/challenge' in current_url or 'verification' in current_url.lower():
                self.logger.warning("⚠️  VERIFICATION CODE REQUIRED!")
                self.logger.warning("=" * 60)
                self.logger.warning("Please enter the verification code in the browser.")
                self.logger.warning("DO NOT CLOSE THE BROWSER")
                self.logger.warning("=" * 60)
                
                # Wait for verification by checking URL changes
                for _ in range(60):  # Wait up to 5 minutes
                    await asyncio.sleep(5)
                    current_url = self.page.url
                    if '/feed' in current_url or '/jobs' in current_url:
                        self.logger.info("✅ Verification complete!")
                        
                        # Close any onboarding modals
                        try:
                            close_btns = await self.page.query_selector_all('button[aria-label="Dismiss"]')
                            for btn in close_btns:
                                await btn.click()
                                await asyncio.sleep(0.5)
                        except:
                            pass
                        return
                        
                raise Exception("Verification timeout")
            
            # Unknown state - try navigating to feed
            self.logger.info("Attempting to navigate to feed...")
            await self.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            if '/feed' in self.page.url:
                self.logger.info("✅ Login successful!")
                return
            else:
                raise Exception("Login failed - unexpected state")
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            try:
                await self.page.screenshot(path="login_error.png")
            except:
                pass  # Browser might be closed
            raise

    async def search_jobs(self):
        """Navigate to job search results."""
        keywords = self.config['search_parameters']['keywords']
        location = self.config['search_parameters']['location']
        url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_AL=true"
        
        self.logger.info(f"Navigating to: {url}")
        await self.page.goto(url)
        await asyncio.sleep(3)

    async def apply_to_jobs(self):
        """Main loop for finding and applying to jobs."""
        applied_count = 0
        max_applications = self.config['limit']['daily_applications']
        
        # Scroll to load jobs
        await self._scroll_job_list()
        
        # Get all job cards - CORRECTED SELECTOR
        job_cards = await self.page.query_selector_all('li.jobs-search-results__list-item')
        
        if not job_cards:
            self.logger.warning("No job cards found. Trying alternate selector...")
            job_cards = await self.page.query_selector_all('.scaffold-layout__list-item')
        
        self.logger.info(f"Found {len(job_cards)} job listings.")
        
        for i, job_card in enumerate(job_cards):
            if applied_count >= max_applications:
                self.logger.info(f"Reached daily limit of {max_applications} applications.")
                break
                
            try:
                # Scroll job into view and click
                await job_card.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                await job_card.click()
                await asyncio.sleep(2)
                
                # Check for Easy Apply button - CORRECTED SELECTOR
                easy_apply_btn = await self.page.query_selector('button.jobs-apply-button')
                
                if easy_apply_btn:
                    btn_text = await easy_apply_btn.inner_text()
                    if "Easy Apply" in btn_text:
                        self.logger.info(f"Job {i+1}: Clicking Easy Apply...")
                        await easy_apply_btn.click()
                        await asyncio.sleep(1)
                        
                        # Handle application modal
                        success = await self._handle_application_modal(job_index=i+1)
                        if success:
                            applied_count += 1
                            self.logger.info(f"✅ Successfully applied! Total: {applied_count}/{max_applications}")
                    else:
                        self.logger.info(f"Job {i+1}: External application, skipping.")
                else:
                    self.logger.info(f"Job {i+1}: No apply button found, skipping.")
                    
            except Exception as e:
                self.logger.error(f"Error on job {i+1}: {e}")
                await self.page.screenshot(path=f"error_job_{i+1}.png")

    async def _scroll_job_list(self):
        """Scroll the job list to load all available jobs."""
        try:
            # Try primary selector
            list_container = await self.page.query_selector('ul.scaffold-layout__list-container')
            if not list_container:
                list_container = await self.page.query_selector('.jobs-search-results-list')
            
            if list_container:
                self.logger.info("Scrolling job list to load more results...")
                for _ in range(3):  # Scroll 3 times
                    await list_container.evaluate('el => el.scrollTop += 500')
                    await asyncio.sleep(1)
            else:
                self.logger.warning("Could not find job list container for scrolling.")
        except Exception as e:
            self.logger.warning(f"Scrolling issue: {e}")

    async def _handle_application_modal(self, job_index=0):
        """Handle the multi-step Easy Apply modal with COMPREHENSIVE logging."""
        max_attempts = 30
        attempt = 0
        page_num = 1
        
        while attempt < max_attempts:
            attempt += 1
            await asyncio.sleep(1)
            
            self.logger.info(f"📋 Form Page {page_num}, Step {attempt}")
            
            # Take screenshot of current form page
            screenshot_path = f"job_{job_index}_page_{page_num}_step_{attempt}.png"
            await self.page.screenshot(path=screenshot_path)
            self.logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
            # Check for Submit button FIRST
            submit_btn = await self.page.query_selector('button[aria-label*="Submit application"]')
            if submit_btn:
                self.logger.info("✅ Found Submit button! Submitting application...")
                await submit_btn.click()
                await asyncio.sleep(3)
                await self._close_modal()
                return True
            
            # Upload resume if file upload present
            await self._upload_resume_if_needed()
            
            # Fill form fields on current page
            await self._fill_form_fields_with_logging()
            await asyncio.sleep(1)
            
            # Check for Next button
            next_btn = await self.page.query_selector('button[aria-label*="Continue to next step"]')
            if next_btn:
                page_num += 1
                self.logger.info(f"➡️  Clicking Next to page {page_num}...")
                await next_btn.click()
                await asyncio.sleep(2)
                continue
            
            # Check for Review button
            review_btn = await self.page.query_selector('button[aria-label*="Review your application"]')
            if review_btn:
                self.logger.info("📝 Clicking Review...")
                await review_btn.click()
                await asyncio.sleep(2)
                continue
            
            # Check if there's an error message
            error_msg = await self.page.query_selector('.artdeco-inline-feedback--error')
            if error_msg:
                error_text = await error_msg.inner_text()
                self.logger.error(f"❌ Form error detected: {error_text}")
                await self.page.screenshot(path=f"job_{job_index}_error.png")
                
        self.logger.warning(f"⏱️  Could not complete application after {max_attempts} attempts")
        await self.page.screenshot(path=f"job_{job_index}_timeout.png")
        await self._close_modal()
        return False

    async def _upload_resume_if_needed(self):
        """Upload resume if file input is present."""
        try:
            # Look for file upload input
            file_inputs = await self.page.query_selector_all('input[type="file"]')
            for file_input in file_inputs:
                is_visible = await file_input.is_visible()
                
                # Check if already uploaded
                files = await file_input.evaluate('el => el.files.length')
                if files > 0:
                    self.logger.info("📄 Resume already uploaded, skipping")
                    continue
                
                # Upload resume
                self.logger.info(f"📤 Uploading resume: {self.resume_path}")
                await file_input.set_input_files(self.resume_path)
                await asyncio.sleep(1)
                self.logger.info("✅ Resume uploaded successfully!")
        except Exception as e:
            self.logger.warning(f"Resume upload issue: {e}")

    async def _fill_form_fields_with_logging(self):
        """Fill all form fields with DETAILED logging."""
        
        self.logger.info("🔍 Scanning for form fields...")
        
        # Text inputs
        text_inputs = await self.page.query_selector_all('input[type="text"], input[type="tel"], input[type="email"], input[type="number"], textarea')
        self.logger.info(f"Found {len(text_inputs)} text input fields")
        
        for idx, inp in enumerate(text_inputs):
            try:
                is_visible = await inp.is_visible()
                is_enabled = await inp.is_enabled()
                
                if not is_visible or not is_enabled:
                    continue
                
                # Get current value
                current_value = await inp.evaluate('el => el.value')
                
                # Get label
                label_text = await self._get_label_for_field(inp)
                
                # Skip if already filled with valid data
                if current_value and len(current_value.strip()) > 0:
                    # Check if malformed
                    if not any(x in current_value.lower() for x in ['software', 'engineer', 'state', 'city', 'new york']):
                        self.logger.info(f"  ✓ Field {idx+1} '{label_text}': Already filled with '{current_value[:30]}'")
                        continue
                    else:
                        self.logger.warning(f"  ⚠️  Field {idx+1} '{label_text}': Malformed value '{current_value[:30]}', clearing...")
                        await inp.evaluate('el => el.value = ""')
                
                # Determine field type
                field_type = await self._determine_field_type(inp, label_text)
                
                # Get answer - with fallback to dummy data
                self.logger.info(f"  🤖 Field {idx+1} '{label_text}' (type: {field_type})")
                answer = self._get_answer_with_fallback(label_text, field_type)
                
                if answer and len(answer.strip()) > 0:
                    try:
                        # Clear and fill
                        await inp.evaluate('el => el.value = ""')
                        await asyncio.sleep(0.1)
                        await inp.fill(answer, timeout=5000)
                        await asyncio.sleep(0.1)
                        await inp.evaluate('el => el.dispatchEvent(new Event("change", { bubbles: true }))')
                        
                        self.logger.info(f"  ✅ Filled with: '{answer[:50]}'")
                    except Exception as e:
                        self.logger.warning(f"  ❌ Fill failed: {e}")
            except Exception as e:
                pass
        
        # Radio buttons
        fieldsets = await self.page.query_selector_all('fieldset')
        self.logger.info(f"Found {len(fieldsets)} radio button groups")
        
        for idx, fieldset in enumerate(fieldsets):
            try:
                legend = await fieldset.query_selector('legend')
                if not legend:
                    continue
                    
                legend_text = await legend.inner_text()
                radios = await fieldset.query_selector_all('input[type="radio"]')
                
                if not radios:
                    continue
                
                # Check if already selected
                selected = False
                for radio in radios:
                    if await radio.is_checked():
                        selected = True
                        break
                
                if selected:
                    self.logger.info(f"  ✓ Radio {idx+1} '{legend_text}': Already selected")
                    continue
                
                # Get options
                options = []
                for radio in radios:
                    label = await radio.evaluate('el => el.nextElementSibling?.textContent || ""')
                    options.append(label.strip())
                
                question = f"{legend_text} Options: {', '.join(options)}"
                self.logger.info(f"  🔘 Radio {idx+1}: {legend_text}")
                choice = self._get_answer_with_fallback(question, "text")
                
                # Click best match
                for i, opt in enumerate(options):
                    if opt.lower() in choice.lower() or choice.lower() in opt.lower():
                        try:
                            await radios[i].click(timeout=3000)
                            self.logger.info(f"  ✅ Selected: {opt}")
                            break
                        except:
                            pass
                        
            except Exception as e:
                pass
        
        # Dropdowns
        selects = await self.page.query_selector_all('select')
        self.logger.info(f"Found {len(selects)} dropdown fields")
        
        for idx, select in enumerate(selects):
            try:
                is_visible = await select.is_visible()
                if not is_visible:
                    continue
                
                # Check if already selected
                current_value = await select.evaluate('el => el.value')
                label_text = await self._get_label_for_field(select)
                
                if current_value and current_value != 'SELECT' and len(current_value) > 0:
                    self.logger.info(f"  ✓ Dropdown {idx+1} '{label_text}': Already selected")
                    continue
                    
                options_elements = await select.query_selector_all('option')
                options = []
                for opt in options_elements:
                    text = await opt.inner_text()
                    if text and text.strip() and text.strip().lower() not in ['select an option', 'select']:
                        options.append(text.strip())
                
                if len(options) > 1:
                    question = f"{label_text} Options: {', '.join(options[:10])}"  # Limit to first 10 options
                    self.logger.info(f"  📋 Dropdown {idx+1}: {label_text}")
                    choice = self._get_answer_with_fallback(question, "text")
                    
                    # Select best match
                    for opt_text in options:
                        if opt_text.lower() in choice.lower() or choice.lower() in opt_text.lower():
                            try:
                                await select.select_option(label=opt_text, timeout=3000)
                                self.logger.info(f"  ✅ Selected: {opt_text}")
                                break
                            except:
                                pass
            except Exception as e:
                pass

    def _get_answer_with_fallback(self, question, field_type):
        """Get AI answer with intelligent fallback to dummy data."""
        try:
            # Try AI first
            answer = self.ai_handler.generate_answer(question, field_type=field_type)
            if answer and len(answer.strip()) > 0:
                return answer
        except:
            pass
        
        # Fallback to intelligent dummy data based on question
        question_lower = question.lower()
        
        # Phone/Mobile
        if 'phone' in question_lower or 'mobile' in question_lower:
            return "5551234567"
        
        # Email
        if 'email' in question_lower:
            return "alex.danny@email.com"
        
        # City
        if 'city' in question_lower:
            return "New York"
        
        # State
        if 'state' in question_lower:
            return "New York"
        
        # Years of experience
        if 'year' in question_lower and 'experience' in question_lower:
            return "5"
        
        # Salary
        if 'salary' in question_lower or 'compensation' in question_lower:
            return "120000"
        
        # Yes/No questions
        if field_type == "boolean" or 'yes' in question_lower or 'no' in question_lower:
            return "Yes"
        
        # Generic text
        return "Not applicable"

    async def _get_label_for_field(self, element):
        """Get the label text for a form field."""
        try:
            # Try aria-label
            aria_label = await element.get_attribute('aria-label')
            if aria_label:
                return aria_label
            
            # Try ID-based label
            field_id = await element.get_attribute('id')
            if field_id:
                label = await self.page.query_selector(f'label[for="{field_id}"]')
                if label:
                    return await label.inner_text()
            
            # Try placeholder
            placeholder = await element.get_attribute('placeholder')
            if placeholder:
                return placeholder
        except:
            pass
        return "Unknown Field"

    async def _determine_field_type(self, element, label_text):
        """Determine if field should be numeric or text."""
        inp_type = await element.get_attribute('type')
        label_lower = label_text.lower()
        
        if 'phone' in label_lower or 'mobile' in label_lower or inp_type == 'tel':
            return 'numeric'
        elif 'years' in label_lower or 'experience' in label_lower or inp_type == 'number':
            return 'numeric'
        return 'text'

    async def _close_modal(self):
        """Close the Easy Apply modal."""
        try:
            close_btn = await self.page.query_selector('button[aria-label*="Dismiss"]')
            if close_btn:
                await close_btn.click()
                await asyncio.sleep(1)
                
                # Confirm discard if needed
                discard_btn = await self.page.query_selector('button:has-text("Discard")')
                if discard_btn:
                    await discard_btn.click()
        except:
            pass
