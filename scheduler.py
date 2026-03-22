"""
NexoraFuture Scheduler
Runs automated posting on a schedule.
Copyright 2026 NexoraFuture. All rights reserved.
"""

import sys
import time
from datetime import datetime

try:
    import schedule
except ImportError:
    print("ERROR: schedule not installed. Run: pip install schedule")
    sys.exit(1)

import config


def twitter_job():
    """Post a tweet."""
    print(f"\n[{datetime.now().strftime('%H:%M')}] Running Twitter job...")
    from platforms.twitter_bot import post_tweet
    post_tweet()


def reddit_job():
    """Run one Reddit monitoring cycle."""
    print(f"\n[{datetime.now().strftime('%H:%M')}] Running Reddit job...")
    from platforms.reddit_bot import get_reddit, run_full_cycle
    reddit = get_reddit()
    if reddit:
        run_full_cycle(reddit)


def quora_job():
    """Generate Quora answers."""
    print(f"\n[{datetime.now().strftime('%H:%M')}] Running Quora job...")
    from platforms.quora_generator import generate_daily
    generate_daily()


def setup_schedule():
    """Configure the daily schedule."""
    # Twitter: post at UK peak times
    for post_time in config.TWITTER_POST_TIMES_UTC:
        schedule.every().day.at(post_time).do(twitter_job)
        print(f"  Twitter scheduled at {post_time} UTC")

    # Reddit: monitor every 30 minutes during active hours (7am-10pm UTC)
    schedule.every(30).minutes.do(reddit_job)
    print("  Reddit monitoring every 30 minutes")

    # Quora: generate answers once daily at 9am
    schedule.every().day.at("09:00").do(quora_job)
    print("  Quora generation at 09:00 UTC")


def run_scheduler():
    """Start the scheduler loop."""
    print("=" * 50)
    print("  NEXORAFUTURE SCHEDULER")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Days until MTD deadline: {config.days_until_deadline()}")
    print("=" * 50)
    print()

    setup_schedule()

    print(f"\nScheduler running. Press Ctrl+C to stop.")
    print(f"Next job: {schedule.next_run()}\n")

    while True:
        try:
            schedule.run_pending()
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Continuing in 60s...")
            time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
