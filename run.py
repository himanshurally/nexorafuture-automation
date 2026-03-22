#!/usr/bin/env python3
"""
NexoraFuture Promotion Automation
Main CLI entry point.

Usage:
    python run.py --help              Show all commands
    python run.py --dashboard         Show status dashboard
    python run.py --preview           Preview today's content
    python run.py --start             Start full automation scheduler

    python run.py --tweet             Post a single tweet
    python run.py --tweet-batch       Post all daily tweets
    python run.py --tweet-preview     Preview tweets without posting

    python run.py --reddit-monitor    Start continuous Reddit monitoring
    python run.py --reddit-cycle      Run one Reddit cycle
    python run.py --reddit-post TYPE  Create a Reddit post (educational/discussion/build_in_public)
    python run.py --reddit-status     Show Reddit bot status

    python run.py --quora             Generate Quora answers
    python run.py --quora-topic TOPIC Generate answer for specific topic

Copyright 2026 NexoraFuture. All rights reserved.

DISCLAIMER: NexoraFuture provides tools for tracking and organisation only.
We are not tax advisors, accountants, or legal professionals.
Always consult a qualified tax professional for advice specific to your situation.
"""

import argparse
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


def main():
    parser = argparse.ArgumentParser(
        description="NexoraFuture Promotion Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python run.py --dashboard         Show status overview
  python run.py --preview           Preview all content for today
  python run.py --start             Start full automation
  python run.py --tweet             Post one tweet now
  python run.py --reddit-monitor    Start Reddit bot

{config.COPYRIGHT}
{config.DISCLAIMER_SHORT}
        """,
    )

    # General
    parser.add_argument("--dashboard", action="store_true", help="Show status dashboard")
    parser.add_argument("--preview", action="store_true", help="Preview today's content (all platforms)")
    parser.add_argument("--start", action="store_true", help="Start full automation scheduler")
    parser.add_argument("--generate", action="store_true", help="Generate all content for today")

    # Twitter
    parser.add_argument("--tweet", action="store_true", help="Generate a tweet and copy to clipboard")
    parser.add_argument("--tweet-batch", action="store_true", help="Generate all daily tweets")
    parser.add_argument("--tweet-preview", action="store_true", help="Preview tweets")
    parser.add_argument("--tweet-copy", type=int, metavar="N", help="Copy tweet N to clipboard")
    parser.add_argument("--tweet-category", type=str, help="Tweet category")

    # Reddit
    parser.add_argument("--reddit-monitor", action="store_true", help="Start continuous Reddit monitoring")
    parser.add_argument("--reddit-cycle", action="store_true", help="Run one Reddit cycle")
    parser.add_argument("--reddit-post", type=str, help="Create Reddit post (educational/discussion/build_in_public)")
    parser.add_argument("--reddit-status", action="store_true", help="Show Reddit status")

    # Quora
    parser.add_argument("--quora", action="store_true", help="Generate Quora answers")
    parser.add_argument("--quora-topic", type=str, help="Generate for specific topic")
    parser.add_argument("--quora-topics", action="store_true", help="List available topics")

    # Email
    parser.add_argument("--send-digest", action="store_true", help="Send daily digest email")
    parser.add_argument("--digest-to", type=str, help="Override digest recipient email")

    args = parser.parse_args()

    # If no args, show dashboard
    if len(sys.argv) == 1:
        from dashboard import show_dashboard
        show_dashboard()
        return

    # Dashboard
    if args.dashboard:
        from dashboard import show_dashboard
        show_dashboard()

    # Preview
    elif args.preview:
        from content_engine import preview_all
        preview_all()

    # Generate all content
    elif args.generate:
        print("Generating today's content...\n")
        from content_engine import preview_all
        preview_all()
        print("\n--- Generating Quora answers ---\n")
        from platforms.quora_generator import generate_daily
        generate_daily()

    # Start scheduler
    elif args.start:
        from scheduler import run_scheduler
        run_scheduler()

    # Twitter commands
    elif args.tweet_copy:
        from platforms.twitter_bot import copy_tweet_by_number
        copy_tweet_by_number(args.tweet_copy)
    elif args.tweet:
        from platforms.twitter_bot import post_tweet
        post_tweet(category=args.tweet_category)
    elif args.tweet_batch:
        from platforms.twitter_bot import post_daily_batch
        post_daily_batch()
    elif args.tweet_preview:
        from platforms.twitter_bot import preview
        preview()

    # Reddit commands
    elif args.reddit_monitor:
        from platforms.reddit_bot import get_reddit, continuous_monitor
        reddit = get_reddit()
        if reddit:
            continuous_monitor(reddit)
    elif args.reddit_cycle:
        from platforms.reddit_bot import get_reddit, run_full_cycle
        reddit = get_reddit()
        if reddit:
            run_full_cycle(reddit)
    elif args.reddit_post:
        from platforms.reddit_bot import get_reddit, auto_post
        reddit = get_reddit()
        if reddit:
            auto_post(reddit, post_type=args.reddit_post)
    elif args.reddit_status:
        from platforms.reddit_bot import status
        status()

    # Quora commands
    elif args.quora:
        from platforms.quora_generator import generate_daily
        generate_daily()
    elif args.quora_topic:
        from platforms.quora_generator import generate_for_topic
        generate_for_topic(args.quora_topic)
    elif args.quora_topics:
        from platforms.quora_generator import list_topics
        list_topics()

    # Email commands
    elif args.send_digest:
        from platforms.email_sender import send_digest
        recipients = [args.digest_to] if args.digest_to else None
        send_digest(recipients=recipients)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
