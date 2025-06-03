import schedule
import time
import asyncio
from datetime import datetime, timedelta
from scraper_without_llm import main as scraper_main


def job():
    asyncio.run(scraper_main())
    # Here you can call your main function or any other function you want to run periodically


if __name__ == "__main__":
    # Schedule the job to run every 5 seconds
    schedule.every(1).day.do(job)

    print("Scheduler started. Press Ctrl+C to stop.")

    try:
        while True:
            schedule.run_pending()
            # Sleep for 23 hours and 50 minutes to avoid running the job too frequently
            time.sleep(60 * 60 * 23 + 60 * 50)
    except KeyboardInterrupt:
        print("Scheduler stopped.")
