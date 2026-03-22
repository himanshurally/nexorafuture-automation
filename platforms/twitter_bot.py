"""
NexoraFuture Twitter/X Bot
Auto-posts tweets using Tweepy (free tier: 1500 tweets/month).
Copyright 2026 NexoraFuture. All rights reserved.
"""

import json
import os
import sys
import time
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from content_engine import get_twitter_post, get_daily_twitter_posts

POSTED_FILE = os.path.join(config.LOGS_DIR, "twitter_posted.json")


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


def get_client():
    """Create Tweepy v2 client."""
    try:
        import tweepy
    except ImportError:
        print("ERROR: tweepy not installed. Run: pip install tweepy")
        return None

    if not config.TWITTER_API_KEY:
        print("ERROR: Twitter API credentials not configured.")
        print("Set these environment variables:")
        print("  NF_TWITTER_API_KEY")
        print("  NF_TWITTER_API_SECRET")
        print("  NF_TWITTER_ACCESS_TOKEN")
        print("  NF_TWITTER_ACCESS_SECRET")
        return None

    client = tweepy.Client(
        bearer_token=config.TWITTER_BEARER_TOKEN,
        consumer_key=config.TWITTER_API_KEY,
        consumer_secret=config.TWITTER_API_SECRET,
        access_token=config.TWITTER_ACCESS_TOKEN,
        access_token_secret=config.TWITTER_ACCESS_SECRET,
    )
    return client


def post_tweet(text=None, category=None):
    """Post a single tweet. If no text, generates one from templates."""
    client = get_client()
    if not client:
        return False

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
        # Trim hashtags if needed
        lines = text.strip().split("\n")
        while len("\n".join(lines)) > 280 and lines:
            lines.pop()
        text = "\n".join(lines)

    print(f"\nPosting tweet ({len(text)} chars):\n{text}\n")

    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"Posted successfully! Tweet ID: {tweet_id}")

        # Log it
        today = date.today().isoformat()
        posted_data["posts"].append({
            "id": tweet_id,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "date": today,
        })
        posted_data.setdefault("daily_count", {})
        posted_data["daily_count"][today] = posted_data["daily_count"].get(today, 0) + 1
        save_posted(posted_data)
        return True

    except Exception as e:
        print(f"Failed to post: {e}")
        return False


def post_daily_batch():
    """Post all scheduled tweets for today."""
    posted_data = load_posted()
    remaining = config.TWITTER_MAX_POSTS_PER_DAY - get_today_count(posted_data)

    if remaining <= 0:
        print("All tweets for today already posted.")
        return

    print(f"Posting {remaining} tweets for today...\n")
    posts = get_daily_twitter_posts(remaining)

    for i, post in enumerate(posts):
        print(f"--- Tweet {i + 1}/{len(posts)} ---")
        success = post_tweet(text=post["full_text"])
        if success and i < len(posts) - 1:
            # Wait between posts to avoid rate limits
            wait = 60
            print(f"Waiting {wait}s before next tweet...")
            time.sleep(wait)

    print("\nDaily batch complete.")


def preview():
    """Preview today's tweets without posting."""
    posts = get_daily_twitter_posts(config.TWITTER_MAX_POSTS_PER_DAY)
    print(f"\n{'='*50}")
    print(f"  TWITTER PREVIEW - {date.today()}")
    print(f"  Days until MTD deadline: {config.days_until_deadline()}")
    print(f"{'='*50}\n")

    for i, post in enumerate(posts, 1):
        print(f"[Tweet {i}] Category: {post['category']}")
        print(f"Characters: {len(post['full_text'])}/280")
        print(f"{post['full_text']}")
        print()

    posted_data = load_posted()
    today_count = get_today_count(posted_data)
    print(f"Posted today: {today_count}/{config.TWITTER_MAX_POSTS_PER_DAY}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NexoraFuture Twitter Bot")
    parser.add_argument("--post", action="store_true", help="Post a single tweet")
    parser.add_argument("--batch", action="store_true", help="Post daily batch")
    parser.add_argument("--preview", action="store_true", help="Preview without posting")
    parser.add_argument("--category", type=str, help="Tweet category")
    args = parser.parse_args()

    if args.preview:
        preview()
    elif args.batch:
        post_daily_batch()
    elif args.post:
        post_tweet(category=args.category)
    else:
        preview()
