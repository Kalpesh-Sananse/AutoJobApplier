"""
Production-Level LinkedIn Auto Job Applier
==========================================

This is an enterprise-grade AI agent that automatically applies to LinkedIn jobs
using Playwright for automation and Ollama for intelligent form filling.

Key Features:
- ✅ Modal-scoped queries (never fills search bars or filters)
- ✅ Intelligent field detection with skip logic
- ✅ Retry logic for robust error handling
- ✅ Resume upload automation
- ✅ Multi-page form navigation
- ✅ Comprehensive logging with statistics
- ✅ Session persistence
- ✅ Error detection and recovery

Architecture:
------------
1. browser_playwright.py - Browser management with session persistence
2. linkedin_playwright.py - Core LinkedIn automation logic
3. ai_handler.py - AI-powered form filling with Ollama
4. main_playwright.py - Entry point and orchestration

How It Works:
------------
1. Login (with session check to avoid repeat logins)
2. Navigate to job search
3. Find Easy Apply jobs
4. For each job:
   a. Click Easy Apply button
   b. Get modal container
   c. Fill fields WITHIN modal only
   d. Upload resume if needed
   e. Navigate through pages (Next → Review → Submit)
   f. Submit application

Critical Implementation Details:
-------------------------------

### Modal Scoping
All queries MUST be scoped to the modal container to prevent filling
LinkedIn's search bars and filter controls:

```python
modal = await self.page.query_selector('.jobs-easy-apply-modal')
text_inputs = await modal.query_selector_all('input[type="text"]')  # ✅ Correct
```

NOT:
```python
text_inputs = await self.page.query_selector_all('input[type="text"]')  # ❌ Wrong!
```

### Field Skipping
The agent skips non-application fields using keyword matching:

SKIP_KEYWORDS = ['search by title', 'search for', 'type to search', 'filter results by']

Any field with a label containing these keywords is skipped.

### AI Response Cleaning
All AI responses are cleaned to remove newlines and extra whitespace:

```python
answer = answer.replace('\\n', ' ').replace('\\r', ' ')
answer = ' '.join(answer.split())
```

### Error Handling
- Retry logic for modal detection
- Consecutive error tracking (abort after 3 errors)
- Screenshot capture on errors
- Statistics tracking for monitoring

### Statistics Tracking
The agent tracks:
- applications_submitted
- applications_failed  
- fields_filled
- errors_encountered

Production Deployment Checklist:
-------------------------------
- [ ] Configure secrets.yaml with credentials
- [ ] Configure config.yaml with search parameters
- [ ] Verify Ollama is running (localhost:11434)
- [ ] Test resume file exists and is accessible
- [ ] Run initial test with daily_applications=1
- [ ] Review screenshots to verify correct fields filled
- [ ] Check logs for "Skipped: ...search bar" messages
- [ ] Verify no search bars or filters are being modified
- [ ] Increase daily_applications after successful tests

Usage:
-----
```bash
# Install dependencies
pip install playwright requests pyyaml

# Install browser
playwright install chromium

# Configure credentials
# Edit agent/secrets.yaml

# Run bot
python agent/main_playwright.py
```

Monitoring:
----------
Watch for these log patterns:

✅ GOOD:
- "✅ Easy Apply modal detected"
- "⏭️ Skipped: 'Search by title' (search bar)"
- "✅ 'Email address' → 'alex.danny@email.com'"
- "➡️ Clicking NEXT → Page 2"
- "✅ SUBMIT BUTTON FOUND - Submitting!"

❌ BAD:
- "✅ 'Search by title' → 'Software Engineer'"  # Search bar filled!
- "New York\\nState"  # Newline in answer!
- "❌ Too many consecutive errors"

Troubleshooting:
--------------
1. **Bot fills search bars**: Check modal scoping in _fill_modal_fields()
2. **Newlines in answers**: Verify ai_handler.py has answer.replace('\\n', ' ')
3. **Resume not uploading**: Check file path in secrets.yaml
4. **Bot stuck on form**: Check screenshots (job_X_pY_sZ.png) to debug
5. **Login fails**: Delete browser_session.json and try again

Support:
-------
For issues, check:
1. Logs for error messages
2. Screenshots (job_*.png) for visual debugging
3. Statistics at end of run
"""

import asyncio
import logging
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

class LinkedInBotPlaywright:
    """Production-ready LinkedIn Auto Job Applier with proper modal scoping."""
    
    # Production constants
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    MODAL_SELECTORS = ['.jobs-easy-apply-modal', '[role="dialog"]', '.jobs-easy-apply-content']
    SKIP_KEYWORDS = ['search by title', 'search for', 'type to search', 'filter results by', 'filter by']
    
    def __init__(self, page: Page, secrets, config, ai_handler):
        self.page = page
        self.email = secrets['linkedin']['username']
        self.password = secrets['linkedin']['password']
        self.resume_path = secrets['paths']['resume_path']
        self.config = config
        self.ai_handler = ai_handler
        self.logger = logging.getLogger("AutoJobApplier.LinkedIn")
        
        # Screenshot settings for memory optimization
        self.screenshot_config = config.get('screenshots', {
            'enabled': True,
            'save_on_success': False,
            'save_on_error': True,
            'save_final_only': True
        })
        self.current_job_screenshots = []  # Track screenshots per job
        
        # Statistics tracking
        self.stats = {
            'applications_submitted': 0,
            'applications_failed': 0,
            'fields_filled': 0,
            'errors_encountered': 0
        }

    async def login(self):
        """Login to LinkedIn with session check - PRODUCTION VERSION."""
        self.logger.info("🔐 Checking login status...")
        
        try:
            # Check if already logged in from saved session
            try:
                await self.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=10000)
                await asyncio.sleep(2)
            except:
                await asyncio.sleep(1)  # Wait for any redirect to settle
            
            # Check URL AFTER potential redirect/exception
            if '/feed' in self.page.url or '/jobs' in self.page.url:
                self.logger.info("✅ Already logged in!")
                await self._close_onboarding_modals()
                return
            
            # Not logged in, proceed with login
            self.logger.info("🔑 Logging in...")
            await self.page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            await self.page.fill('#username', self.email)
            await self.page.fill('#password', self.password)
            await self.page.click('button[type="submit"]')
            await asyncio.sleep(3)
            
            current_url = self.page.url
            
            if '/feed' in current_url or '/check/add-phone' in current_url:
                self.logger.info("✅ Login successful!")
                await self._close_onboarding_modals()
                return
                
            if '/checkpoint/challenge' in current_url or 'verification' in current_url.lower():
                self.logger.warning("⚠️  VERIFICATION REQUIRED - Please complete in browser")
                self.logger.warning("Waiting for verification (up to 5 minutes)...")
                
                for _ in range(60):
                    await asyncio.sleep(5)
                    if '/feed' in self.page.url or '/jobs' in self.page.url:
                        self.logger.info("✅ Verification complete!")
                        await self._close_onboarding_modals()
                        return
                        
                raise Exception("Verification timeout")
            
            # Try navigating to feed
            await self.page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            if '/feed' in self.page.url:
                self.logger.info("✅ Login successful!")
                return
            else:
                raise Exception("Login failed - unexpected state")
                
        except Exception as e:
            self.logger.error(f"❌ Login error: {e}")
            self.stats['errors_encountered'] += 1
            try:
                await self.page.screenshot(path="login_error.png", full_page=True)
            except:
                pass
            raise

    async def _close_onboarding_modals(self):
        """Close any LinkedIn onboarding/welcome modals."""
        try:
            close_btns = await self.page.query_selector_all('button[aria-label="Dismiss"]')
            for btn in close_btns:
                try:
                    await btn.click(timeout=2000)
                    await asyncio.sleep(0.3)
                except:
                    pass
        except:
            pass

    async def search_jobs(self):
        """Navigate to job search results."""
        keywords = self.config['search_parameters']['keywords']
        location = self.config['search_parameters']['location']
        url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_AL=true"
        
        self.logger.info(f"🔍 Searching: {url}")
        await self.page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(3)

    async def apply_to_single_job(self, url):
        """Navigate directly to a specific job and apply (Used by UI Dashboard)."""
        self.logger.info(f"🎯 Navigating directly to target job: {url}")
        await self.page.goto(url, wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        easy_apply_btn = await self.page.query_selector('button.jobs-apply-button')
        if easy_apply_btn:
            btn_text = await easy_apply_btn.inner_text()
            if "Easy Apply" in btn_text:
                self.logger.info("📝 Easy Apply button found. Starting application...")
                await easy_apply_btn.click()
                await asyncio.sleep(2)
                
                success = await self._handle_application_modal(job_index=1)
                if success:
                    self.stats['applications_submitted'] += 1
                    self.logger.info("✅ Targeted Application submitted successfully!")
                else:
                    self.stats['applications_failed'] += 1
            else:
                self.logger.info("⏭️ External application link required (Not Easy Apply). Aborting single targeted job.")
        else:
            self.logger.warning("⚠️ No Easy Apply button found on this specific job UI. It may have expired or you already applied.")

    async def apply_to_jobs(self):
        """Main loop for finding and applying to jobs - PRODUCTION VERSION."""
        applied_count = 0
        max_applications = self.config['limit']['daily_applications']
        
        # Scroll to load jobs
        await self._scroll_job_list()
        
        # Get job cards
        job_cards = await self.page.query_selector_all('li.jobs-search-results__list-item')
        if not job_cards:
            job_cards = await self.page.query_selector_all('.scaffold-layout__list-item')
        
        self.logger.info(f"📊 Found {len(job_cards)} job listings")
        
        for i, job_card in enumerate(job_cards):
            if applied_count >= max_applications:
                self.logger.info(f"🎯 Reached daily limit: {max_applications}")
                break
                
            try:
                # Click job card to load details
                await job_card.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                await job_card.click()
                await asyncio.sleep(2)
                
                # Look for Easy Apply button
                easy_apply_btn = await self.page.query_selector('button.jobs-apply-button')
                
                if easy_apply_btn:
                    btn_text = await easy_apply_btn.inner_text()
                    if "Easy Apply" in btn_text:
                        self.logger.info(f"\n{'='*70}")
                        self.logger.info(f"📝 JOB {i+1}: Starting application...")
                        self.logger.info(f"{'='*70}")
                        
                        await easy_apply_btn.click()
                        await asyncio.sleep(2)
                        
                        success = await self._handle_application_modal(job_index=i+1)
                        if success:
                            applied_count += 1
                            self.stats['applications_submitted'] += 1
                            self.logger.info(f"✅ Application {applied_count}/{max_applications} submitted!")
                        else:
                            self.stats['applications_failed'] += 1
                    else:
                        self.logger.info(f"⏭️  Job {i+1}: External application, skipping")
                else:
                    self.logger.info(f"⏭️  Job {i+1}: No Easy Apply button")
                    
            except Exception as e:
                self.logger.error(f"❌ Error on job {i+1}: {e}")
                self.stats['errors_encountered'] += 1
                try:
                    await self.page.screenshot(path=f"error_job_{i+1}.png", full_page=True)
                except:
                    pass
        
        # Print final statistics
        self.logger.info(f"\n{'='*70}")
        self.logger.info("📊 FINAL STATISTICS")
        self.logger.info(f"{'='*70}")
        self.logger.info(f"✅ Applications Submitted: {self.stats['applications_submitted']}")
        self.logger.info(f"❌ Applications Failed: {self.stats['applications_failed']}")
        self.logger.info(f"📝 Fields Filled: {self.stats['fields_filled']}")
        self.logger.info(f"⚠️  Errors Encountered: {self.stats['errors_encountered']}")
        self.logger.info(f"{'='*70}\n")

    async def _scroll_job_list(self):
        """Scroll the job list to load more jobs."""
        try:
            list_container = await self.page.query_selector('ul.scaffold-layout__list-container')
            if not list_container:
                list_container = await self.page.query_selector('.jobs-search-results-list')
            
            if list_container:
                for _ in range(3):
                    await list_container.evaluate('el => el.scrollTop += 500')
                    await asyncio.sleep(0.8)
        except:
            pass

    async def _get_modal_with_retry(self):
        """Get modal container with retry logic - PRODUCTION FEATURE."""
        for attempt in range(self.MAX_RETRIES):
            for selector in self.MODAL_SELECTORS:
                modal = await self.page.query_selector(selector)
                if modal:
                    self.logger.info(f"✅ Modal found with selector: {selector}")
                    return modal
            
            if attempt < self.MAX_RETRIES - 1:
                self.logger.warning(f"⚠️  Modal not found, retry {attempt + 1}/{self.MAX_RETRIES}")
                await asyncio.sleep(self.RETRY_DELAY)
        
        return None

    async def _handle_application_modal(self, job_index=0):
        """Handle Easy Apply modal - PRODUCTION VERSION with retry logic."""
        max_steps = 30
        step = 0
        page_num = 1
        consecutive_errors = 0
        
        # CRITICAL: Get modal container with retry logic
        modal = await self._get_modal_with_retry()
        if not modal:
            self.logger.error("❌ Could not find Easy Apply modal after retries!")
            self.stats['errors_encountered'] += 1
            return False
        
        while step < max_steps:
            step += 1
            await asyncio.sleep(1)
            
            self.logger.info(f"\n--- Page {page_num}, Step {step} ---")
            
            # Screenshot for debugging (optimized for memory)
            should_screenshot = self.screenshot_config.get('enabled', True)
            
            if should_screenshot:
                # Only save if configured or on final steps
                screenshot_path = f"job_{job_index}_p{page_num}_s{step}.png"
                
                # Check if this is a critical step
                is_critical = step == 1 or 'review' in str(page_num).lower()
                
                if not self.screenshot_config.get('save_final_only', False) or is_critical:
                    try:
                        await self.page.screenshot(path=screenshot_path, full_page=True)
                        self.current_job_screenshots.append(screenshot_path)
                        self.logger.info(f"📸 {screenshot_path}")
                    except:
                        pass
            
            # Scroll modal to top
            try:
                await modal.evaluate('el => el.scrollTop = 0')
                await asyncio.sleep(0.3)
            except:
                pass
            
            # Check for SUBMIT button (highest priority)
            submit_btn = await modal.query_selector('button[aria-label*="Submit application"]')
            if submit_btn:
                is_enabled = await submit_btn.is_enabled()
                if is_enabled:
                    self.logger.info("✅ SUBMIT BUTTON FOUND - Submitting!")
                    
                    # Take final screenshot before submitting
                    if self.screenshot_config.get('enabled', True):
                        screenshot_path = f"job_{job_index}_FINAL_submit.png"
                        try:
                            await self.page.screenshot(path=screenshot_path, full_page=True)
                            self.current_job_screenshots.append(screenshot_path)
                            self.logger.info(f"📸 Final: {screenshot_path}")
                        except:
                            pass
                    
                    await submit_btn.click()
                    await asyncio.sleep(3)
                    await self._close_modal()
                    
                    # Clean up screenshots on success if configured
                    if not self.screenshot_config.get('save_on_success', False):
                        await self._cleanup_job_screenshots()
                    else:
                        self.current_job_screenshots = []  # Reset for next job
                    
                    return True
                else:
                    self.logger.warning("⚠️  Submit button disabled, filling more fields...")
            
            # Upload resume if needed
            await self._upload_resume(modal)
            
            # Fill form fields (SCOPED TO MODAL ONLY!)
            await self._fill_modal_fields(modal)
            
            # Scroll to bottom of modal
            try:
                await modal.evaluate('el => el.scrollTop = el.scrollHeight')
                await asyncio.sleep(0.5)
            except:
                pass
            
            # Check for error messages
            error_detected = await self._check_for_errors(modal)
            if error_detected:
                consecutive_errors += 1
                self.logger.error(f"❌ Form has errors (consecutive: {consecutive_errors})")
                try:
                    await self.page.screenshot(path=f"job_{job_index}_error_p{page_num}.png", full_page=True)
                except:
                    pass
                
                # Too many consecutive errors - bail out
                if consecutive_errors >= 3:
                    self.logger.error("❌ Too many consecutive errors, aborting application")
                    self.stats['applications_failed'] += 1
                    
                    # Keep error screenshots, delete others
                    if self.screenshot_config.get('save_on_error', True):
                        self.logger.info("📁 Keeping error screenshots for debugging")
                    
                    await self._close_modal()
                    self.current_job_screenshots = []  # Reset for next job
                    self.field_errors = {} # Reset errors
                    return False
            else:
                consecutive_errors = 0  # Reset on success

            
            # Look for NEXT button
            next_btn = await modal.query_selector('button[aria-label*="Continue to next step"]')
            if not next_btn:
                next_btn = await modal.query_selector('button:has-text("Next")')
            
            if next_btn:
                is_enabled = await next_btn.is_enabled()
                is_visible = await next_btn.is_visible()
                
                if is_visible and is_enabled:
                    page_num += 1
                    self.logger.info(f"➡️  Clicking NEXT → Page {page_num}")
                    await next_btn.click()
                    await asyncio.sleep(2)
                    continue
                else:
                    self.logger.info(f"⏸️  Next button not ready (visible={is_visible}, enabled={is_enabled})")
            
            # Look for REVIEW button
            review_btn = await modal.query_selector('button[aria-label*="Review"]')
            if not review_btn:
                review_btn = await modal.query_selector('button:has-text("Review")')
                
            if review_btn:
                is_enabled = await review_btn.is_enabled()
                is_visible = await review_btn.is_visible()
                
                if is_visible and is_enabled:
                    self.logger.info("📝 Clicking REVIEW")
                    await review_btn.click()
                    await asyncio.sleep(2)
                    continue
            
            # No more buttons, might be stuck
            self.logger.warning("⚠️  No actionable buttons found")
            
        self.logger.warning(f"⏱️  Timeout after {max_steps} steps")
        self.stats['applications_failed'] += 1
        await self._close_modal()
        return False

    async def _upload_resume(self, modal):
        """Upload resume if file input present - PRODUCTION VERSION."""
        try:
            file_inputs = await modal.query_selector_all('input[type="file"]')
            for file_input in file_inputs:
                files_count = await file_input.evaluate('el => el.files.length')
                if files_count > 0:
                    self.logger.info("📄 Resume already uploaded")
                    continue
                
                self.logger.info(f"📤 Uploading: {self.resume_path}")
                await file_input.set_input_files(self.resume_path)
                await asyncio.sleep(1)
                self.logger.info("✅ Resume uploaded!")
        except Exception as e:
            self.logger.warning(f"⚠️  Resume upload issue: {e}")
            self.stats['errors_encountered'] += 1

    async def _fill_modal_fields(self, modal):
        """Fill ONLY fields within the modal - PRODUCTION VERSION with skip logic."""
        
        self.logger.info("🔍 Scanning modal for fields...")
        
        # Scroll through modal to reveal all fields
        try:
            await modal.evaluate('el => el.scrollTop = 0')
            await asyncio.sleep(0.2)
            await modal.evaluate('el => el.scrollTop = el.scrollHeight * 0.5')
            await asyncio.sleep(0.2)
            await modal.evaluate('el => el.scrollTop = el.scrollHeight')
            await asyncio.sleep(0.2)
            await modal.evaluate('el => el.scrollTop = 0')
            await asyncio.sleep(0.3)
        except:
            pass
        
        # TEXT INPUTS (scoped to modal)
        text_inputs = await modal.query_selector_all('input[type="text"], input[type="tel"], input[type="email"], input[type="number"], textarea')
        self.logger.info(f"📋 Found {len(text_inputs)} text fields in modal")
        
        filled_count = 0
        for idx, inp in enumerate(text_inputs):
            try:
                if not await inp.is_visible() or not await inp.is_enabled():
                    continue
                
                current_value = await inp.evaluate('el => el.value')
                label = await self._get_field_label(inp)
                
                # CRITICAL: Skip non-application fields using production skip logic
                if any(kw in label.lower() for kw in self.SKIP_KEYWORDS):
                    self.logger.info(f"  ⏭️  Skipped: '{label[:50]}' (non-application field)")
                    continue
                
                # Log what LinkedIn autofilled, but NEVER skip. We want the AI to strictly override.
                if current_value and len(current_value.strip()) > 0 and len(current_value) < 100:
                    self.logger.info(f"  ✓ LinkedIn Autofilled (waiting for AI to verify/override): '{label[:40]}' = '{current_value[:30]}'")
                
                # Get answer with retry logic
                input_type = await inp.get_attribute('type')
                field_type = self._determine_field_type(inp, label, input_type)
                
                # Retrieve any tracked error context for this field to re-feed directly to the AI
                field_id = await inp.get_attribute('id') or label
                if not hasattr(self, 'field_errors'): self.field_errors = {}
                error_ctx = self.field_errors.get(field_id, "")
                
                answer = await self._get_answer_with_retry(label, field_type, error_ctx)
                
                if answer:
                    try:
                        await inp.evaluate('el => el.value = ""')
                        await asyncio.sleep(0.1)
                        await inp.fill(answer, timeout=5000)
                        await inp.evaluate('el => el.dispatchEvent(new Event("input", { bubbles: true }))')
                        await inp.evaluate('el => el.dispatchEvent(new Event("change", { bubbles: true }))')
                        filled_count += 1
                        self.stats['fields_filled'] += 1
                        self.logger.info(f"  ✅ '{label[:40]}' → '{answer[:40]}'")
                    except Exception as e:
                        self.logger.warning(f"  ❌ Failed '{label[:30]}': {e}")
                        self.stats['errors_encountered'] += 1
            except:
                pass
        
        # RADIO BUTTONS (scoped to modal)
        fieldsets = await modal.query_selector_all('fieldset')
        self.logger.info(f"🔘 Found {len(fieldsets)} radio groups in modal")
        
        for fieldset in fieldsets:
            try:
                legend = await fieldset.query_selector('legend')
                if not legend:
                    continue
                
                legend_text = await legend.inner_text()
                
                # CRITICAL: Skip filter controls
                if any(kw in legend_text.lower() for kw in self.SKIP_KEYWORDS):
                    self.logger.info(f"  ⏭️  Skipped: '{legend_text[:50]}' (filter control)")
                    continue
                
                radios = await fieldset.query_selector_all('input[type="radio"]')
                if not radios:
                    continue
                
                # Check if already selected
                is_selected = False
                for radio in radios:
                    if await radio.is_checked():
                        is_selected = True
                        break
                
                if is_selected:
                    self.logger.info(f"  ✓ Radio '{legend_text[:40]}': selected")
                    continue
                
                # Get options and select
                options = []
                for radio in radios:
                    opt_label = await radio.evaluate('el => el.nextElementSibling?.textContent || el.parentElement?.textContent || ""')
                    options.append(opt_label.strip())
                
                question = f"{legend_text} Options: {', '.join(options[:5])}"
                choice = await self._get_answer_with_retry(question, "text")
            
                # Select best match - TRY MULTIPLE APPROACHES
                selected = False
                for i, opt in enumerate(options):
                    if choice.lower() in opt.lower() or opt.lower() in choice.lower():
                        try:
                            # Approach 1: Direct click
                            await radios[i].click(timeout=3000, force=True)
                            selected = True
                            self.stats['fields_filled'] += 1
                            self.logger.info(f"  ✅ Radio '{legend_text[:30]}' → '{opt}'")
                            break
                        except:
                            try:
                                # Approach 2: Use check() method
                                await radios[i].check(timeout=3000)
                                selected = True
                                self.stats['fields_filled'] += 1
                                self.logger.info(f"  ✅ Radio '{legend_text[:30]}' → '{opt}'")
                                break
                            except:
                                pass
                
                # If no match, select first option as fallback
                if not selected and len(radios) > 0:
                    try:
                        await radios[0].click(timeout=3000, force=True)
                        self.stats['fields_filled'] += 1
                        self.logger.info(f"  ✅ Radio '{legend_text[:30]}' → '{options[0]}' (fallback)")
                    except:
                        pass
            except:
                pass
        
        # CHECKBOXES (NEW! scoped to modal)
        checkboxes = await modal.query_selector_all('input[type="checkbox"]')
        self.logger.info(f"☑️  Found {len(checkboxes)} checkboxes in modal")
        
        for idx, checkbox in enumerate(checkboxes):
            try:
                if not await checkbox.is_visible() or not await checkbox.is_enabled():
                    continue
                
                # Get label
                label = await self._get_field_label(checkbox)
                
                # Skip filter/search checkboxes
                if any(kw in label.lower() for kw in self.SKIP_KEYWORDS):
                    self.logger.info(f"  ⏭️  Skipped checkbox: '{label[:50]}'")
                    continue
                
                # Check if already checked
                is_checked = await checkbox.is_checked()
                
                # Determine if we should check it
                should_check = False
                label_lower = label.lower()
                
                # Auto-check for common consent/agreement checkboxes
                consent_keywords = ['agree', 'consent', 'acknowledge', 'accept', 'authorize', 'understand']
                if any(kw in label_lower for kw in consent_keywords):
                    should_check = True
                else:
                    # Ask AI for other checkboxes
                    question = f"Should I check this checkbox: {label}?"
                    answer = await self._get_answer_with_retry(question, "boolean")
                    should_check = 'yes' in answer.lower()
                
                # Check or uncheck as needed
                if should_check and not is_checked:
                    try:
                        await checkbox.click(timeout=3000, force=True)
                        self.stats['fields_filled'] += 1
                        self.logger.info(f"  ✅ Checked: '{label[:50]}'")
                    except:
                        try:
                            await checkbox.check(timeout=3000)
                            self.stats['fields_filled'] += 1
                            self.logger.info(f"  ✅ Checked: '{label[:50]}'")
                        except Exception as e:
                            self.logger.warning(f"  ❌ Failed to check '{label[:30]}': {e}")
                elif should_check and is_checked:
                    self.logger.info(f"  ✓ Checkbox '{label[:40]}': already checked")
                else:
                    self.logger.info(f"  ⏭️  Skipped checkbox: '{label[:40]}' (not needed)")
            except:
                pass
        
        # DROPDOWNS (scoped to modal)
        selects = await modal.query_selector_all('select')
        self.logger.info(f"📋 Found {len(selects)} dropdowns in modal")
        
        for select in selects:
            try:
                if not await select.is_visible():
                    continue
                
                current_value = await select.evaluate('el => el.value')
                label = await self._get_field_label(select)
                
                if current_value and current_value != '' and current_value.lower() not in ['select', 'select an option']:
                    self.logger.info(f"  ✓ Dropdown Autofilled (waiting for AI): '{label[:40]}'")
                
                options_elements = await select.query_selector_all('option')
                options = []
                for opt in options_elements:
                    text = await opt.inner_text()
                    if text and text.strip().lower() not in ['select an option', 'select', '']:
                        options.append(text.strip())
                
                if len(options) > 1:
                    question = f"{label} Options: {', '.join(options[:8])}"
                    choice = await self._get_answer_with_retry(question, "text")
                    
                    for opt_text in options:
                        if choice.lower() in opt_text.lower() or opt_text.lower() in choice.lower():
                            try:
                                await select.select_option(label=opt_text, timeout=3000)
                                self.stats['fields_filled'] += 1
                                self.logger.info(f"  ✅ Dropdown '{label[:30]}' → '{opt_text}'")
                                break
                            except:
                                pass
            except:
                pass
        
        self.logger.info(f"📊 Filled {filled_count} text fields this pass")

    async def _get_answer_with_retry(self, question, field_type, error_context=""):
        """Get answer with retry logic - PRODUCTION FEATURE."""
        for attempt in range(self.MAX_RETRIES):
            try:
                answer = self._get_answer(question, field_type, error_context)
                if answer and len(answer.strip()) > 0:
                    return answer
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    self.logger.warning(f"⚠️  AI failed (attempt {attempt + 1}), retrying...")
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    self.logger.error(f"❌ AI failed after {self.MAX_RETRIES} attempts")
                    self.stats['errors_encountered'] += 1
        
        # Final fallback
        return self._get_fallback_answer(question, field_type)

    async def _check_for_errors(self, modal):
        """Check for error messages in the modal - PRODUCTION VERSION."""
        try:
            error_els = await modal.query_selector_all('.artdeco-inline-feedback--error')
            if error_els and len(error_els) > 0:
                if not hasattr(self, 'field_errors'): self.field_errors = {}
                for error_el in error_els:
                    try:
                        error_text = await error_el.inner_text()
                        if error_text:
                            self.logger.error(f"⚠️  Form error: {error_text.strip()}")
                            # Attempt to clear the field that triggered the error so the AI can correct it on next tick
                            parent = await error_el.evaluate_handle('el => el.closest(".fb-dash-form-element")')
                            if parent:
                                inp = await parent.query_selector('input, textarea, select')
                                if inp:
                                    # Register error context directly to AI logic handler
                                    label = await self._get_field_label(inp)
                                    field_id = await inp.get_attribute('id') or label
                                    self.field_errors[field_id] = error_text.strip()
                                    await inp.evaluate('el => { if(el.type === "checkbox" || el.type === "radio") { el.checked = false; } else { el.value = ""; } }')
                                    self.logger.info("  🧹 Cleared errored field to force retry with AI correction.")
                    except:
                        pass
                return True
        except:
            pass
        return False

    async def _get_field_label(self, element):
        """Get label for a field with multiple fallbacks."""
        try:
            # Try to grab the broader question context first (especially for Checkboxes inside FieldSets)
            context = await element.evaluate('''
                el => {
                    let container = el.closest('.fb-dash-form-element') || el.closest('.jobs-easy-apply-form-section__grouping') || el.closest('fieldset');
                    if (container) {
                        let heading = container.querySelector('legend span.visually-hidden, legend, .fb-dash-form-element__label span[aria-hidden="true"], label.fb-dash-form-element__label');
                        if (heading && heading.textContent.trim().length > 5) {
                             let parent = el.closest('label');
                             let parentText = parent ? parent.textContent.trim() : "";
                             if (el.type === 'checkbox' || el.type === 'radio') {
                                 return heading.textContent.trim() + " (" + parentText + ")";
                             }
                             return heading.textContent.trim();
                        }
                    }
                    return null;
                }
            ''')
            if context:
                return context.strip()

            # Try aria-label first
            aria_label = await element.get_attribute('aria-label')
            if aria_label:
                return aria_label.strip()
            
            # Try associated label
            field_id = await element.get_attribute('id')
            if field_id:
                label_el = await self.page.query_selector(f'label[for="{field_id}"]')
                if label_el:
                    label_text = await label_el.inner_text()
                    if label_text:
                        return label_text.strip()
            
            # Try placeholder
            placeholder = await element.get_attribute('placeholder')
            if placeholder:
                return placeholder.strip()
            
            # Try parent label
            parent_label = await element.evaluate('''
                el => {
                    let parent = el.closest('label');
                    return parent ? parent.textContent : null;
                }
            ''')
            if parent_label:
                return parent_label.strip()
        except:
            pass
        return "Unknown"

    def _determine_field_type(self, element, label, input_type=None):
        """Determine field type for AI - PRODUCTION VERSION."""
        label_lower = label.lower()
        
        if input_type in ['number', 'tel']:
            return 'numeric'
            
        # Numeric fields
        numeric_keywords = ['phone', 'mobile', 'salary', 'compensation', 'how many', 'expected base']
        if any(kw in label_lower for kw in numeric_keywords):
            return 'numeric'
        if 'year' in label_lower and ('experience' in label_lower or 'in years' in label_lower):
            return 'numeric'
        
        # Boolean fields
        if any(kw in label_lower for kw in ['authorized to work', 'require sponsorship', 'willing to']):
            return 'boolean'
        
        return 'text'

    def _get_answer(self, question, field_type, error_context=""):
        """Get answer from AI - PRODUCTION VERSION."""
        try:
            answer = self.ai_handler.generate_answer(question, field_type=field_type, error_context=error_context)
            if answer and len(answer.strip()) > 0:
                return answer
        except Exception as e:
            self.logger.warning(f"⚠️  AI error: {e}")
        
        return self._get_fallback_answer(question, field_type)
    
    def _get_fallback_answer(self, question, field_type):
        """Intelligent fallback answers - PRODUCTION VERSION."""
        q_lower = question.lower()
        
        # Phone/Mobile
        if 'phone' in q_lower or 'mobile' in q_lower:
            return "5551234567"
        
        # Email
        if 'email' in q_lower:
            return "alex.danny@email.com"
        
        # Location
        if 'city' in q_lower:
            return "New York"
        if 'state' in q_lower:
            return "NY"
        if 'country' in q_lower:
            return "United States"
        if 'zip' in q_lower or 'postal' in q_lower:
            return "10001"
        
        # Experience
        if 'year' in q_lower and 'experience' in q_lower:
            return "5"
        
        # Compensation
        if 'salary' in q_lower or 'compensation' in q_lower:
            return "120000"
        
        # Boolean
        if field_type == "boolean":
            if 'sponsorship' in q_lower:
                return "No"
            return "Yes"
        
        # Default
        return "Not applicable"

    async def _close_modal(self):
        """Close Easy Apply modal - PRODUCTION VERSION."""
        try:
            # Try clicking dismiss button
            close_btn = await self.page.query_selector('button[aria-label*="Dismiss"]')
            if close_btn:
                await close_btn.click()
                await asyncio.sleep(1)
                
                # Handle discard confirmation if it appears
                discard_btn = await self.page.query_selector('button:has-text("Discard")')
                if discard_btn:
                    await discard_btn.click()
                    await asyncio.sleep(0.5)
        except Exception as e:
            self.logger.warning(f"⚠️  Error closing modal: {e}")

    async def _cleanup_job_screenshots(self):
        """Clean up screenshots for current job to save memory."""
        import os
        
        if not self.current_job_screenshots:
            return
        
        deleted_count = 0
        for screenshot_path in self.current_job_screenshots:
            try:
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                    deleted_count += 1
            except Exception as e:
                self.logger.warning(f"⚠️  Could not delete {screenshot_path}: {e}")
        
        if deleted_count > 0:
            self.logger.info(f"🗑️  Cleaned up {deleted_count} screenshots to save memory")
        
        self.current_job_screenshots = []
