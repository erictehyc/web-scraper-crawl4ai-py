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
    schedule.every(1).minute.do(job)

    print("Scheduler started. Press Ctrl+C to stop.")

    try:
        while True:
            schedule.run_pending()
            # Sleep for a short time to avoid busy waiting
            time.sleep(50)
    except KeyboardInterrupt:
        print("Scheduler stopped.")
