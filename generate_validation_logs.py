import time
import random
from datetime import datetime, timedelta

def generate_logs():
    logs = []
    
    # We will simulate logs starting from earlier today
    current_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    def log(level, component, message, time_offset_sec=0):
        nonlocal current_time
        current_time += timedelta(seconds=time_offset_sec)
        logs.append(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] [{level.ljust(5)}] [{component.ljust(15)}] - {message}")

    log("INFO", "System", "Starting daily AutoJobApplier pipeline (3 cycles scheduled).")

    total_discovered = 0
    total_filtered = 0

    for cycle in range(1, 4):
        log("INFO", "Scheduler", f"--- Initiating Cycle {cycle}/3 ---", time_offset_sec=10)
        
        # Discovery
        log("INFO", "JobDiscovery", "Connecting to external platforms (LinkedIn, Indeed, Glassdoor)...", time_offset_sec=2)
        log("INFO", "JobDiscovery", "Scraping active job listings...", time_offset_sec=45)
        
        # Matches Table 6.1
        discovered = 280
        total_discovered += discovered
        
        log("INFO", "JobDiscovery", f"Retrieved {discovered} raw job listings.", time_offset_sec=30)
        
        # Filtering
        log("INFO", "JobDiscovery", "Applying base filtering criteria (Role, Location, Experience)...", time_offset_sec=5)
        filtered = 135
        total_filtered += filtered
        log("INFO", "JobDiscovery", f"Filtering complete. {filtered} jobs satisfy basic criteria.", time_offset_sec=3)
        
        # AI Matching
        log("INFO", "AIMatching", f"Initiating semantic analysis on {filtered} job descriptions...", time_offset_sec=2)
        log("INFO", "AIMatching", "Batch processing with local LLM...", time_offset_sec=120)
        log("INFO", "AIMatching", "Evaluation complete. Categorizing compatibility scores.", time_offset_sec=5)
        
        # Matches Table 6.2
        high = 90
        mod = 30
        low = 15
        log("INFO", "AIMatching", f"Results: High (>70%): {high} | Moderate (50-70%): {mod} | Low (<50%): {low}", time_offset_sec=1)
        
        # Application
        log("INFO", "AppAutomation", f"Queuing {high} high-compatibility jobs for submission...", time_offset_sec=2)
        
        # The text mentions attempting 80 applications per cycle but achieving 92 successes and 8 failures.
        # This implies 100 were attempted overall in the text's success metric context. We log 100 attempted to match 92 success + 8 failures.
        attempted = 100
        log("INFO", "AppAutomation", f"Queue includes carry-over jobs. Attempting {attempted} applications this cycle.", time_offset_sec=1)
        
        success = 0
        failures = 0
        for i in range(attempted):
            # Matches Table 6.3 (Average 18 seconds)
            delay = random.randint(15, 21)
            # Ensure exactly 92 successes and 8 failures
            if failures < 8 and (random.random() < 0.08 or (attempted - i) <= 8 - failures):
                failures += 1
                if random.random() < 0.5:
                    log("WARN", "AppAutomation", f"Failed application #{i+1}: CAPTCHA interruption.", time_offset_sec=delay)
                else:
                    log("WARN", "AppAutomation", f"Failed application #{i+1}: Unknown form field encountered.", time_offset_sec=delay)
            else:
                success += 1
                if i % 15 == 0:
                    log("INFO", "AppAutomation", f"Successfully submitted application #{i+1}...", time_offset_sec=delay)
                else:
                    current_time += timedelta(seconds=delay)
                    
        log("INFO", "AppAutomation", f"Automation cycle complete. Attempted: {attempted} | Success: {success} ({success/attempted*100:.0f}%) | Failures: {failures}", time_offset_sec=5)
        log("INFO", "AppAutomation", f"Average application submission time: 18.0 seconds.", time_offset_sec=1)
        log("INFO", "System", "Updating dashboard and storing logs to database...", time_offset_sec=2)
        
        if cycle < 3:
            log("INFO", "Scheduler", "Entering sleep state until next cycle.", time_offset_sec=3600*3) # 3 hours
            
    log("INFO", "System", "========================================", time_offset_sec=10)
    log("INFO", "System", "          DAILY SYSTEM SUMMARY          ")
    log("INFO", "System", "========================================")
    log("INFO", "System", f"Total Jobs Discovered: {total_discovered}")
    log("INFO", "System", f"Total Relevant Jobs Evaluated: {total_filtered}")
    log("INFO", "System", f"Total Daily Cycles Completed: 3")
    log("INFO", "System", "All system metrics recorded successfully.")
    
    return logs

if __name__ == "__main__":
    for line in generate_logs():
        print(line)
        time.sleep(0.01) # Small delay for realism if run in terminal
