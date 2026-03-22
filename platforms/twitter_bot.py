"""
NexoraFuture Twitter/X Bot
Generates daily tweets and saves them for easy copy-paste posting.
Also supports auto-posting via Tweepy if you have a paid X API plan.
Copyright 2026 NexoraFuture. All rights reserved.
"""

import json
import os
import sys
import time
import subprocess
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from content_engine import get_twitter_post, get_daily_twitter_posts

POSTED_FILE = os.path.join(config.LOGS_DIR, "twitter_posted.json")
DAILY_FILE = os.path.join(config.OUTPUT_DIR, "twitter", "today_tweets.txt")


def load_posted():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r") as f:
            return json.load(f)
    return {"posts": [], "daily_count": {}}


def save_posted(data):
    os.makedirs(os.path.dirname(POSTED_FILE), exist_ok=True)
    with open(POSTED_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_today_count(posted_data):
    today = date.today().isoformat()
    return posted_data.get("daily_count", {}).get(today, 0)


def can_post_today(posted_data):
    return get_today_count(posted_data) < config.TWITTER_MAX_POSTS_PER_DAY


def has_api():
    """Check if X API credentials are configured."""
    return bool(config.TWITTER_API_KEY)


def get_client():
    """Create Tweepy v2 client."""
    try:
        import tweepy
    except ImportError:
        print("NOTE: tweepy not installed. Using copy-paste mode.")
        return None

    if not config.TWITTER_API_KEY:
        return None

    client = tweepy.Client(
        bearer_token=config.TWITTER_BEARER_TOKEN,
        consumer_key=config.TWITTER_API_KEY,
        consumer_secret=config.TWITTER_API_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_SECRET,
    )
    return client


def copy_to_clipboard(text):
    """Copy text to macOS clipboard."""
    try:
        process = subprocess.Popen(
            ["pbcopy"], stdin=subprocess.PIPE, env={"LANG": "en_US.UTF-8"}
        )
        process.communicate(text.encode("utf-8"))
        return True
    except Exception:
        return False


def generate_daily_file():
    """Generate today's tweets and save to a file for easy copy-paste."""
    os.makedirs(os.path.dirname(DAILY_FILE), exist_ok=True)
    posts = get_daily_twitter_posts(config.TWITTER_MAX_POSTS_PER_DAY)
    today = date.today()

    content = f"NEXORAFUTURE TWEETS FOR {today.strftime('%A, %B %d, %Y')}\n"
    content += f"Days until MTD deadline: {config.days_until_deadline()}\n"
    content += "=" * 50 + "\n\n"

    for i, post in enumerate(posts, 1):
        content += f"--- TWEET {i} ({post['category']}) ---\n"
        content += f"{post['full_text']}\n"
        content += f"[{len(post['full_text'])}/280 chars]\n\n"

    content += "=" * 50 + "\n"
    content += "HOW TO POST:\n"
    content += "  python run.py --tweet-copy 1    (copies tweet 1 to clipboard)\n"
    content += "  python run.py --tweet-copy 2    (copies tweet 2 to clipboard)\n"
    content += "  Then paste directly into X/Twitter\n"

    with open(DAILY_FILE, "w") as f:
        f.write(content)

    return posts


def post_tweet_api(text):
    """Post via API (requires paid plan)."""
    client = get_client()
    if not client:
        return False

    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"  Posted via API! Tweet ID: {tweet_id}")
        return tweet_id
    except Exception as e:
        print(f"  API post failed: {e}")
        return False


def post_tweet(text=None, category=None, copy_mode=True):
    """Generate a tweet. Copies to clipboard by default (or posts via API if available)."""
    posted_data = load_posted()
    if not can_post_today(posted_data):
        print(f"Daily limit reached ({config.TWITTER_MAX_POSTS_PER_DAY} tweets/day)")
        return False

    if text is None:
        post = get_twitter_post(category=category)
        if not post:
            print("No templates available")
            return False
        text = post["full_text"]
        print(f"Category: {post['category']}")

    # Enforce 280 char limit
    if len(text) > 280:
        lines = text.strip().split("\n")
        while len("\n".join(lines)) > 280 and lines:
            lines.pop()
        text = "\n".join(lines)

    print(f"\n{text}")
    print(f"\n[{len(text)}/280 chars]")

    tweet_id = None

    # Try API first if configured
    if has_api() and not copy_mode:
        tweet_id = post_tweet_api(text)

    # Copy to clipboard
    if copy_to_clipboard(text):
        print("\n  Copied to clipboard! Paste it into X/Twitter.")
    else:
        print("\n  (Clipboard copy failed — manually copy the text above)")

    # Log it
    today = date.today().isoformat()
    posted_data["posts"].append({
        "id": tweet_id or "manual",
        "text": text,
        "timestamp": datetime.now().isoformat(),
        "date": today,
        "method": "api" if tweet_id else "clipboard",
    })
    posted_data.setdefault("daily_count", {})
    posted_data["daily_count"][today] = posted_data["daily_count"].get(today, 0) + 1
    save_posted(posted_data)
    return True


def copy_tweet_by_number(num):
    """Copy a specific tweet from today's generated batch to clipboard."""
    posts = get_daily_twitter_posts(config.TWITTER_MAX_POSTS_PER_DAY)

    if num < 1 or num > len(posts):
        print(f"Invalid tweet number. Choose 1-{len(posts)}")
        return False

    post = posts[num - 1]
    text = post["full_text"]

    if copy_to_clipboard(text):
        print(f"\n  Tweet {num} copied to clipboard! ({post['category']})")
        print(f"\n{text}")
        print(f"\n[{len(text)}/280 chars]")
        print("\n  Now paste it into X/Twitter.")
        return True
    else:
        print(f"\n{text}")
        print("\n  (Copy the text above manually)")
        return False


def post_daily_batch():
    """Generate and display all tweets for today."""
    posted_data = load_posted()
    remaining = config.TWITTER_MAX_POSTS_PER_DAY - get_today_count(posted_data)

    if remaining <= 0:
        print("All tweets for today already generated.")
        return

    posts = generate_daily_file()

    print(f"\n{'='*50}")
    print(f"  TODAY'S TWEETS — {date.today().strftime('%A, %B %d')}")
    print(f"  Days until MTD deadline: {config.days_until_deadline()}")
    print(f"{'='*50}\n")

    for i, post in enumerate(posts, 1):
        print(f"--- Tweet {i} ({post['category']}) ---")
        print(post["full_text"])
        print(f"[{len(post['full_text'])}/280 chars]\n")

    print(f"{'='*50}")
    print(f"  Saved to: {DAILY_FILE}")
    print(f"  Copy a specific tweet: python run.py --tweet-copy [1-{len(posts)}]")
    print(f"{'='*50}")


def preview():
    """Preview today's tweets."""
    posts = get_daily_twitter_posts(config.TWITTER_MAX_POSTS_PER_DAY)
    print(f"\n{'='*50}")
    print(f"  TWITTER PREVIEW - {date.today()}")
    print(f"  Days until MTD deadline: {config.days_until_deadline()}")
    api_status = "API connected" if has_api() else "Copy-paste mode (no API)"
    print(f"  Mode: {api_status}")
    print(f"{'='*50}\n")

    for i, post in enumerate(posts, 1):
        print(f"[Tweet {i}] Category: {post['category']}")
        print(f"Characters: {len(post['full_text'])}/280")
        print(f"{post['full_text']}")
        print()

    posted_data = load_posted()
    today_count = get_today_count(posted_data)
    print(f"Posted/generated today: {today_count}/{config.TWITTER_MAX_POSTS_PER_DAY}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NexoraFuture Twitter Bot")
    parser.add_argument("--post", action="store_true", help="Generate and copy a tweet")
    parser.add_argument("--batch", action="store_true", help="Generate daily batch")
    parser.add_argument("--preview", action="store_true", help="Preview without posting")
    parser.add_argument("--copy", type=int, help="Copy tweet N to clipboard")
    parser.add_argument("--category", type=str, help="Tweet category")
    parser.add_argument("--api", action="store_true", help="Force API posting (paid plan)")
    args = parser.parse_args()

    if args.copy:
        copy_tweet_by_number(args.copy)
    elif args.preview:
        preview()
    elif args.batch:
        post_daily_batch()
    elif args.post:
        post_tweet(category=args.category, copy_mode=not args.api)
    else:
        preview()
