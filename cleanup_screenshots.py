import os
import asyncio
from pathlib import Path

async def cleanup_screenshots():
    """Helper method to clean up screenshots."""
    
    # Get all screenshot files
    screenshots = list(Path('.').glob('job_*.png'))
    
    if not screenshots:
        print("No screenshots to clean up")
        return
    
    print(f"Found {len(screenshots)} screenshots")
    
    # Delete all screenshots
    for screenshot in screenshots:
        try:
            os.remove(screenshot)
            print(f"🗑️  Deleted: {screenshot}")
        except Exception as e:
            print(f"❌ Failed to delete {screenshot}: {e}")
    
    print(f"✅ Cleaned up {len(screenshots)} screenshots")

if __name__ == "__main__":
    asyncio.run(cleanup_screenshots())
