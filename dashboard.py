"""
NexoraFuture Dashboard
Terminal dashboard showing automation status.
Copyright 2026 NexoraFuture. All rights reserved.
"""

import json
import os
from datetime import datetime, date, timedelta

import config


def load_log(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {"items": [], "daily_count": {}}


def show_dashboard():
    """Display the full dashboard."""
    today = date.today()
    today_str = today.isoformat()
    week_start = (today - timedelta(days=today.weekday())).isoformat()

    # Load all logs
    twitter_log = load_log(os.path.join(config.LOGS_DIR, "twitter_posted.json"))
    reddit_comment_log = load_log(os.path.join(config.LOGS_DIR, "reddit_commented.json"))
    reddit_post_log = load_log(os.path.join(config.LOGS_DIR, "reddit_posted.json"))

    # Stats
    tw_today = twitter_log.get("daily_count", {}).get(today_str, 0)
    tw_total = len(twitter_log.get("posts", []))

    rd_comments_today = reddit_comment_log.get("daily_count", {}).get(today_str, 0)
    rd_comments_total = len(reddit_comment_log.get("items", []))

    rd_posts_week = sum(
        1 for item in reddit_post_log.get("items", [])
        if item.get("date", "") >= week_start
    )
    rd_posts_total = len(reddit_post_log.get("items", []))

    # Quora output count
    quora_dir = os.path.join(config.OUTPUT_DIR, "quora")
    quora_today = 0
    quora_total = 0
    if os.path.exists(quora_dir):
        for f in os.listdir(quora_dir):
            if f.endswith(".txt"):
                quora_total += 1
                if f.startswith(today_str):
                    quora_today += 1

    days_left = config.days_until_deadline()

    print()
    print("\033[1m" + "=" * 56 + "\033[0m")
    print("\033[1m  NEXORAFUTURE PROMOTION DASHBOARD\033[0m")
    print(f"  {today.strftime('%A, %B %d, %Y')}")
    print("\033[1m" + "=" * 56 + "\033[0m")

    # MTD Deadline
    if days_left > 0:
        print(f"\n  \033[93mMTD DEADLINE: {days_left} days remaining (April 6)\033[0m")
    else:
        print(f"\n  \033[92mMTD DEADLINE: PASSED\033[0m")

    # Platform stats
    print(f"\n  \033[1m--- TWITTER/X ---\033[0m")
    print(f"  Today:    {tw_today}/{config.TWITTER_MAX_POSTS_PER_DAY} tweets")
    print(f"  Total:    {tw_total} tweets posted")
    api = "Connected" if config.TWITTER_API_KEY else "Not configured"
    print(f"  API:      {api}")

    print(f"\n  \033[1m--- REDDIT ---\033[0m")
    print(f"  Comments today: {rd_comments_today}/{config.REDDIT_MAX_COMMENTS_PER_DAY}")
    print(f"  Posts this week: {rd_posts_week}/{config.REDDIT_MAX_POSTS_PER_WEEK}")
    print(f"  Total comments: {rd_comments_total}")
    print(f"  Total posts:    {rd_posts_total}")
    api = "Connected" if config.REDDIT_CLIENT_ID else "Not configured"
    print(f"  API:            {api}")
    print(f"  Blacklisted:    {', '.join(config.REDDIT_BLACKLISTED_SUBREDDITS)}")

    print(f"\n  \033[1m--- QUORA ---\033[0m")
    print(f"  Generated today: {quora_today}")
    print(f"  Total generated: {quora_total}")
    print(f"  Mode:            Manual (copy-paste)")

    # Recent activity
    all_activity = []

    for item in twitter_log.get("posts", [])[-10:]:
        all_activity.append({
            "time": item.get("timestamp", ""),
            "platform": "Twitter",
            "detail": item.get("text", "")[:60],
        })

    for item in reddit_comment_log.get("items", [])[-10:]:
        all_activity.append({
            "time": item.get("timestamp", ""),
            "platform": "Reddit",
            "detail": f"Comment on r/{item.get('subreddit', '?')}: {item.get('post_title', '')[:40]}",
        })

    for item in reddit_post_log.get("items", [])[-10:]:
        all_activity.append({
            "time": item.get("timestamp", ""),
            "platform": "Reddit",
            "detail": f"Post in r/{item.get('subreddit', '?')}: {item.get('title', '')[:40]}",
        })

    all_activity.sort(key=lambda x: x["time"], reverse=True)

    if all_activity:
        print(f"\n  \033[1m--- RECENT ACTIVITY ---\033[0m")
        for item in all_activity[:8]:
            ts = item["time"][:16].replace("T", " ") if item["time"] else "?"
            print(f"  [{ts}] {item['platform']}: {item['detail']}")

    print()
    print("\033[1m" + "=" * 56 + "\033[0m")
    print(f"  {config.COPYRIGHT}")
    print(f"  {config.DISCLAIMER_SHORT}")
    print("\033[1m" + "=" * 56 + "\033[0m")
    print()


if __name__ == "__main__":
    show_dashboard()
