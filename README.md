# NexoraFuture Promotion Automation

Open-source automation toolkit for promoting [NexoraFuture](https://nexorafuture.co.uk) across social platforms.

NexoraFuture builds simple, affordable digital tools for UK sole traders and freelancers — starting with MTD (Making Tax Digital) compliance and expanding into a full business operations platform.

## What This Does

- **Twitter/X Bot** — Auto-posts educational content about MTD, freelancer tips, and NexoraFuture updates (via Tweepy, free tier API)
- **Reddit Bot** — Monitors relevant subreddits for questions about MTD/tax/freelancing and posts helpful, non-promotional comments (via PRAW)
- **Quora Generator** — Generates ready-to-paste answers for Quora questions

All content is template-based (no AI API calls needed for daily operation).

## Reddit Bot Compliance

This bot complies with [Reddit's Data API Terms](https://www.redditinc.com/policies/data-api-terms) and [Developer Terms](https://www.redditinc.com/policies/developer-terms):

- **Bot transparency**: Every comment and post includes a clear bot disclosure
- **No spam**: Rate-limited to 5 comments/day and 2 posts/week
- **No cross-posting**: Each post goes to one subreddit only
- **No vote manipulation**: The bot only posts comments and submissions
- **Non-promotional comments**: Comments provide genuine help with no links or product mentions
- **Source code is public**: You're reading it right now

## Setup

### Requirements
```bash
pip install -r requirements.txt
```

### API Credentials (environment variables)

**Twitter/X** (free tier at developer.twitter.com):
```bash
export NF_TWITTER_API_KEY="..."
export NF_TWITTER_API_SECRET="..."
export NF_TWITTER_ACCESS_TOKEN="..."
export NF_TWITTER_ACCESS_SECRET="..."
export NF_TWITTER_BEARER_TOKEN="..."
```

**Reddit** (free at reddit.com/prefs/apps, "script" type):
```bash
export NF_REDDIT_CLIENT_ID="..."
export NF_REDDIT_CLIENT_SECRET="..."
export NF_REDDIT_USERNAME="..."
export NF_REDDIT_PASSWORD="..."
```

## Usage

```bash
python run.py                    # Show dashboard
python run.py --preview          # Preview today's content
python run.py --start            # Start full automation
python run.py --tweet            # Post one tweet
python run.py --reddit-monitor   # Start Reddit bot
python run.py --quora            # Generate Quora answers
python run.py --help             # All commands
```

## Disclaimer

NexoraFuture provides tools for tracking and organisation only. We are not tax advisors, accountants, or legal professionals. Always consult a qualified tax professional for advice specific to your situation.

## License

Copyright 2026 NexoraFuture. All rights reserved.
