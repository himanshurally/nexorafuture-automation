"""
NexoraFuture Reddit Bot
Fully automatic: monitors subreddits, posts comments, and creates posts.
Uses PRAW (free Reddit API).
Copyright 2026 NexoraFuture. All rights reserved.
"""

import json
import os
import sys
import time
import random
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from content_engine import get_reddit_comment, get_reddit_post, get_all_reddit_posts

COMMENTED_FILE = os.path.join(config.LOGS_DIR, "reddit_commented.json")
POSTED_FILE = os.path.join(config.LOGS_DIR, "reddit_posted.json")


def load_log(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {"items": [], "daily_count": {}, "subreddit_last_post": {}}


def save_log(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def get_today_count(log_data, key="daily_count"):
    today = date.today().isoformat()
    return log_data.get(key, {}).get(today, 0)


def increment_today_count(log_data, key="daily_count"):
    today = date.today().isoformat()
    log_data.setdefault(key, {})
    log_data[key][today] = log_data[key].get(today, 0) + 1


def get_reddit():
    """Create PRAW Reddit instance."""
    try:
        import praw
    except ImportError:
        print("ERROR: praw not installed. Run: pip install praw")
        return None

    if not config.REDDIT_CLIENT_ID:
        print("ERROR: Reddit API credentials not configured.")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'create another app'")
        print("3. Select 'script' type")
        print("4. Set redirect URI to http://localhost:8080")
        print("5. Set these environment variables:")
        print("   NF_REDDIT_CLIENT_ID")
        print("   NF_REDDIT_CLIENT_SECRET")
        print("   NF_REDDIT_USERNAME")
        print("   NF_REDDIT_PASSWORD")
        return None

    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        username=config.REDDIT_USERNAME,
        password=config.REDDIT_PASSWORD,
        user_agent=config.REDDIT_USER_AGENT,
    )
    return reddit


def find_relevant_posts(reddit, limit_per_sub=10):
    """Search subreddits for posts matching our keywords."""
    all_subs = config.REDDIT_ACTIVE_SUBREDDITS + config.REDDIT_MONITOR_SUBREDDITS
    comment_log = load_log(COMMENTED_FILE)
    commented_ids = {item["post_id"] for item in comment_log.get("items", [])}

    relevant = []

    for sub_name in all_subs:
        try:
            subreddit = reddit.subreddit(sub_name)
            # Check new and hot posts
            for post in subreddit.new(limit=limit_per_sub):
                if post.id in commented_ids:
                    continue
                if post.archived or post.locked:
                    continue

                # Check if title or body contains our keywords
                text = (post.title + " " + (post.selftext or "")).lower()
                matched_keywords = []
                for keyword in config.REDDIT_KEYWORDS:
                    if keyword.lower() in text:
                        matched_keywords.append(keyword)

                if matched_keywords:
                    relevant.append({
                        "post": post,
                        "subreddit": sub_name,
                        "keywords": matched_keywords,
                        "title": post.title,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "created": datetime.fromtimestamp(post.created_utc),
                    })
        except Exception as e:
            print(f"  Error scanning r/{sub_name}: {e}")

    # Sort by recency and engagement
    relevant.sort(key=lambda x: x["post"].created_utc, reverse=True)
    return relevant


def auto_comment(reddit, post_data):
    """Post a helpful comment on a relevant post."""
    post = post_data["post"]
    keywords = post_data["keywords"]
    sub_name = post_data["subreddit"]

    # Don't comment in blacklisted subreddits
    if sub_name in config.REDDIT_BLACKLISTED_SUBREDDITS:
        print(f"  Skipping r/{sub_name} (blacklisted)")
        return False

    # Generate comment
    comment_text = get_reddit_comment(keywords)
    if not comment_text:
        print(f"  No matching template for keywords: {keywords}")
        return False

    # Reddit policy: "Bots must clearly disclose to users that they are
    # engaging with a bot." — Append bot disclosure to every comment.
    comment_text += config.REDDIT_BOT_DISCLOSURE

    print(f"\n  Posting comment on r/{sub_name}:")
    print(f"  Post: {post.title}")
    print(f"  Keywords: {', '.join(keywords)}")
    print(f"  Comment preview: {comment_text[:100]}...")

    try:
        comment = post.reply(comment_text)
        print(f"  Comment posted! ID: {comment.id}")

        # Log it
        comment_log = load_log(COMMENTED_FILE)
        comment_log["items"].append({
            "post_id": post.id,
            "comment_id": comment.id,
            "subreddit": sub_name,
            "post_title": post.title,
            "keywords": keywords,
            "timestamp": datetime.now().isoformat(),
        })
        increment_today_count(comment_log)
        save_log(COMMENTED_FILE, comment_log)
        return True

    except Exception as e:
        print(f"  Failed to comment: {e}")
        return False


def auto_post(reddit, post_type=None):
    """Create an original post in a suitable subreddit."""
    post_log = load_log(POSTED_FILE)

    # Check weekly limit
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    week_posts = sum(
        1 for item in post_log.get("items", [])
        if item.get("date", "") >= week_start
    )
    if week_posts >= config.REDDIT_MAX_POSTS_PER_WEEK:
        print(f"Weekly post limit reached ({config.REDDIT_MAX_POSTS_PER_WEEK}/week)")
        return False

    # Get a post template
    if post_type is None:
        post_type = random.choice(["educational", "discussion", "build_in_public"])

    post_data = get_reddit_post(post_type)
    if not post_data:
        print("No post templates available")
        return False

    # Pick a subreddit (avoiding cooldown and blacklist)
    available_subs = []
    for sub in post_data["subreddits"]:
        if sub in config.REDDIT_BLACKLISTED_SUBREDDITS:
            continue
        last_post_time = post_log.get("subreddit_last_post", {}).get(sub)
        if last_post_time:
            cooldown = timedelta(hours=config.REDDIT_SUBREDDIT_COOLDOWN_HOURS)
            if datetime.fromisoformat(last_post_time) + cooldown > datetime.now():
                continue
        available_subs.append(sub)

    if not available_subs:
        print("No subreddits available (all on cooldown or blacklisted)")
        return False

    # Reddit policy: "Bots must not engage in spamming activity...
    # This includes posting identical or substantially similar content
    # across subreddits." — Pick ONE subreddit only per post.
    target_sub = random.choice(available_subs)

    # Also check we haven't posted this same template type to ANY sub recently
    recent_types = [
        item.get("type") for item in post_log.get("items", [])[-10:]
    ]
    if post_type in recent_types:
        # Skip if we recently used this template type (avoids similar content)
        print(f"  Skipping: recently posted '{post_type}' type content")
        return False

    # Append bot disclosure to post body (Reddit bot transparency requirement)
    post_body = post_data["body"] + config.REDDIT_BOT_DISCLOSURE

    print(f"\n  Creating post in r/{target_sub} (only this subreddit):")
    print(f"  Title: {post_data['title']}")
    print(f"  Body preview: {post_data['body'][:150]}...")

    try:
        subreddit = reddit.subreddit(target_sub)
        submission = subreddit.submit(
            title=post_data["title"],
            selftext=post_body,
        )
        print(f"  Post created! ID: {submission.id}")
        print(f"  URL: https://reddit.com{submission.permalink}")

        # Log it
        post_log["items"].append({
            "post_id": submission.id,
            "subreddit": target_sub,
            "title": post_data["title"],
            "type": post_type,
            "date": date.today().isoformat(),
            "timestamp": datetime.now().isoformat(),
            "url": f"https://reddit.com{submission.permalink}",
        })
        post_log.setdefault("subreddit_last_post", {})
        post_log["subreddit_last_post"][target_sub] = datetime.now().isoformat()
        save_log(POSTED_FILE, post_log)
        return True

    except Exception as e:
        print(f"  Failed to post: {e}")
        return False


def monitor_and_comment(reddit):
    """Main monitoring loop: find relevant posts and auto-comment."""
    comment_log = load_log(COMMENTED_FILE)
    today_count = get_today_count(comment_log)

    if today_count >= config.REDDIT_MAX_COMMENTS_PER_DAY:
        print(f"Daily comment limit reached ({config.REDDIT_MAX_COMMENTS_PER_DAY}/day)")
        return

    remaining = config.REDDIT_MAX_COMMENTS_PER_DAY - today_count
    print(f"Comments remaining today: {remaining}")

    print("\nScanning subreddits for relevant posts...")
    relevant = find_relevant_posts(reddit)

    if not relevant:
        print("No new relevant posts found.")
        return

    print(f"Found {len(relevant)} relevant posts.\n")

    commented = 0
    for post_data in relevant:
        if commented >= remaining:
            break

        # Random delay between comments
        if commented > 0:
            delay = random.randint(
                config.REDDIT_COMMENT_COOLDOWN_MINS * 30,
                config.REDDIT_COMMENT_COOLDOWN_MINS * 90,
            )
            print(f"\n  Waiting {delay}s before next comment...")
            time.sleep(delay)

        success = auto_comment(reddit, post_data)
        if success:
            commented += 1

    print(f"\nPosted {commented} comments this session.")


def run_full_cycle(reddit):
    """Run a full cycle: monitor + comment + possibly create a post."""
    print("=" * 50)
    print(f"  REDDIT BOT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # Auto-comment on relevant posts
    monitor_and_comment(reddit)

    # Maybe create an original post (if within weekly limit)
    post_log = load_log(POSTED_FILE)
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    week_posts = sum(
        1 for item in post_log.get("items", [])
        if item.get("date", "") >= week_start
    )

    if week_posts < config.REDDIT_MAX_POSTS_PER_WEEK:
        # 30% chance to create a post in each cycle
        if random.random() < 0.3:
            print("\n--- Creating original post ---")
            auto_post(reddit)
    else:
        print(f"\nWeekly post limit reached ({week_posts}/{config.REDDIT_MAX_POSTS_PER_WEEK})")


def continuous_monitor(reddit, interval_mins=30):
    """Run continuous monitoring loop."""
    print(f"Starting continuous monitoring (every {interval_mins} mins)")
    print("Press Ctrl+C to stop.\n")

    while True:
        try:
            run_full_cycle(reddit)
            print(f"\nNext scan in {interval_mins} minutes...")
            time.sleep(interval_mins * 60)
        except KeyboardInterrupt:
            print("\nStopping monitor.")
            break
        except Exception as e:
            print(f"\nError in cycle: {e}")
            print("Retrying in 5 minutes...")
            time.sleep(300)


def status():
    """Show current Reddit bot status."""
    comment_log = load_log(COMMENTED_FILE)
    post_log = load_log(POSTED_FILE)

    today = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    today_comments = get_today_count(comment_log)
    total_comments = len(comment_log.get("items", []))
    week_posts = sum(
        1 for item in post_log.get("items", [])
        if item.get("date", "") >= week_start
    )
    total_posts = len(post_log.get("items", []))

    print(f"\n{'='*40}")
    print(f"  REDDIT BOT STATUS")
    print(f"{'='*40}")
    print(f"  Comments today: {today_comments}/{config.REDDIT_MAX_COMMENTS_PER_DAY}")
    print(f"  Posts this week: {week_posts}/{config.REDDIT_MAX_POSTS_PER_WEEK}")
    print(f"  Total comments: {total_comments}")
    print(f"  Total posts: {total_posts}")
    print(f"  Blacklisted subs: {', '.join(config.REDDIT_BLACKLISTED_SUBREDDITS)}")
    print()

    # Recent activity
    recent = sorted(
        comment_log.get("items", [])[-5:] + post_log.get("items", [])[-5:],
        key=lambda x: x.get("timestamp", ""),
        reverse=True,
    )[:5]

    if recent:
        print("  Recent activity:")
        for item in recent:
            ts = item.get("timestamp", "")[:16]
            sub = item.get("subreddit", "?")
            if "comment_id" in item:
                print(f"    [{ts}] Comment on r/{sub}: {item.get('post_title', '')[:50]}")
            else:
                print(f"    [{ts}] Post in r/{sub}: {item.get('title', '')[:50]}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NexoraFuture Reddit Bot")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--cycle", action="store_true", help="Run one cycle")
    parser.add_argument("--post", type=str, help="Create a post (educational/discussion/build_in_public)")
    parser.add_argument("--status", action="store_true", help="Show status")
    args = parser.parse_args()

    if args.status:
        status()
    elif args.monitor or args.cycle or args.post:
        reddit = get_reddit()
        if reddit:
            if args.monitor:
                continuous_monitor(reddit)
            elif args.cycle:
                run_full_cycle(reddit)
            elif args.post:
                auto_post(reddit, post_type=args.post)
    else:
        status()
