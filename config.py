"""
NexoraFuture Promotion Automation - Configuration
Copyright 2026 NexoraFuture. All rights reserved.
"""

import os
from datetime import datetime, date

# ============================================================
# API CREDENTIALS - Fill these in before running
# ============================================================

# Twitter/X API (Free tier - 1500 tweets/month)
# Get yours at: https://developer.twitter.com
TWITTER_API_KEY = os.environ.get("NF_TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("NF_TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("NF_TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.environ.get("NF_TWITTER_ACCESS_SECRET", "")
TWITTER_BEARER_TOKEN = os.environ.get("NF_TWITTER_BEARER_TOKEN", "")

# Reddit API (Free - create app at https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID = os.environ.get("NF_REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("NF_REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.environ.get("NF_REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.environ.get("NF_REDDIT_PASSWORD", "")
REDDIT_USER_AGENT = "NexoraFuture Bot v1.0 (by /u/{})".format(REDDIT_USERNAME or "NexoraFuture")

# ============================================================
# BRAND
# ============================================================

BRAND_NAME = "NexoraFuture"
WEBSITE_URL = "nexorafuture.co.uk"
GUMROAD_URL = "https://nexora74.gumroad.com/l/mtd-quartertrack-uk"
PRODUCT_NAME = "MTD QuarterTrack UK"
PRODUCT_PRICE = "19"

COPYRIGHT = "\u00a9 2026 NexoraFuture. All rights reserved."

DISCLAIMER = (
    "NexoraFuture provides tools for tracking and organisation only. "
    "We are not tax advisors, accountants, or legal professionals. "
    "Always consult a qualified tax professional for advice specific to your situation."
)

DISCLAIMER_SHORT = "Not tax advice. Consult a qualified professional."

# Reddit bot transparency disclosure (required by Reddit Data API Terms)
# "Bots must clearly disclose to users that they are engaging with a bot."
REDDIT_BOT_DISCLOSURE = (
    "\n\n---\n"
    "^(Hi! I'm a bot by )[^(NexoraFuture)](https://nexorafuture.co.uk) "
    "^(— we're building simple tools for UK sole traders. "
    "This reply was auto-generated but the info is researched and reviewed. "
    "Not tax advice - always consult a qualified professional. "
    "Feedback welcome!)"
)

# ============================================================
# MTD DEADLINE
# ============================================================

MTD_DEADLINE = date(2026, 4, 6)

def days_until_deadline():
    delta = MTD_DEADLINE - date.today()
    return max(delta.days, 0)

# ============================================================
# TWITTER SETTINGS
# ============================================================

TWITTER_POST_TIMES_UTC = ["07:00", "11:00", "16:00", "19:00"]  # ~UK peak times
TWITTER_MAX_POSTS_PER_DAY = 4
TWITTER_HASHTAGS = {
    "mtd": ["#MakingTaxDigital", "#MTD", "#HMRC", "#UKTax"],
    "freelancer": ["#Freelancer", "#SoleTrader", "#UKBusiness", "#SelfEmployed"],
    "brand": ["#NexoraFuture", "#Automation", "#Productivity", "#BuildInPublic"],
}

# ============================================================
# REDDIT SETTINGS
# ============================================================

# Subreddits to actively post in (safe ones first)
REDDIT_ACTIVE_SUBREDDITS = [
    "SelfEmployedUK",
    "freelanceUK",
    "smallbusinessuk",
    "Entrepreneur",
    "startups",
    "productivity",
    "Notion",
]

# Monitor-only subreddits (comment but don't create posts)
REDDIT_MONITOR_SUBREDDITS = [
    "HMRC",
    "Accounting",
    "UKPersonalFinance",  # blacklisted for posts, but monitor for comment opportunities
]

# Subreddits blacklisted from auto-posting (30-day cooldown)
REDDIT_BLACKLISTED_SUBREDDITS = ["UKPersonalFinance"]

REDDIT_KEYWORDS = [
    "MTD", "Making Tax Digital", "sole trader tax", "HMRC quarterly",
    "tax return freelance", "self assessment", "freelance tax UK",
    "freelance tools", "business automation", "notion template",
    "tax tracking", "quarterly tax", "expense tracking freelance",
    "sole trader expenses", "HMRC deadline",
]

REDDIT_MAX_COMMENTS_PER_DAY = 5
REDDIT_MAX_POSTS_PER_WEEK = 2
REDDIT_COMMENT_COOLDOWN_MINS = 30  # min time between comments
REDDIT_SUBREDDIT_COOLDOWN_HOURS = 12  # min time between posts in same subreddit

# ============================================================
# QUORA SETTINGS
# ============================================================

QUORA_ANSWERS_PER_DAY = 2

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
POSTED_LOG = os.path.join(LOGS_DIR, "posted.json")
REDDIT_COMMENTED_LOG = os.path.join(LOGS_DIR, "reddit_commented.json")
