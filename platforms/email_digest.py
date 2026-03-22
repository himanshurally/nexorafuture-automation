"""
NexoraFuture Email Digest Generator
Generates daily HTML digest with all content to post across platforms.
Copyright 2026 NexoraFuture. All rights reserved.
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from content_engine import (
    get_daily_twitter_posts,
    get_all_reddit_posts,
    get_daily_quora_answers,
    get_reddit_comment,
)

# Common Reddit post types that appear near MTD deadline
REDDIT_COMMENT_OPPORTUNITIES = [
    {
        "likely_title": "Do I need to sign up for MTD? My income is around [X]",
        "subreddits": "r/UKPersonalFinance, r/SelfEmployedUK",
        "search_terms": "MTD income threshold sole trader",
        "suggested_comment_keywords": ["MTD", "Making Tax Digital", "what do I need"],
    },
    {
        "likely_title": "What software should I use for Making Tax Digital?",
        "subreddits": "r/UKPersonalFinance, r/freelanceUK",
        "search_terms": "MTD software sole trader",
        "suggested_comment_keywords": ["MTD", "Making Tax Digital"],
    },
    {
        "likely_title": "Just heard about MTD - what do I need to do?",
        "subreddits": "r/SelfEmployedUK, r/freelanceUK",
        "search_terms": "Making Tax Digital what do I do",
        "suggested_comment_keywords": ["MTD", "confused", "help"],
    },
    {
        "likely_title": "How do I track expenses as a sole trader?",
        "subreddits": "r/freelanceUK, r/SelfEmployedUK",
        "search_terms": "sole trader expense tracking",
        "suggested_comment_keywords": ["expense", "tracking", "categories"],
    },
    {
        "likely_title": "First year self-employed - tax advice?",
        "subreddits": "r/UKPersonalFinance, r/freelanceUK",
        "search_terms": "first year self employed tax",
        "suggested_comment_keywords": ["self assessment", "tax return", "first time"],
    },
    {
        "likely_title": "What tools/apps do freelancers use to stay organised?",
        "subreddits": "r/freelanceUK, r/Entrepreneur",
        "search_terms": "freelance tools organised",
        "suggested_comment_keywords": ["tools", "freelance", "organise"],
    },
    {
        "likely_title": "Overwhelmed by freelance admin - any tips?",
        "subreddits": "r/freelanceUK, r/SelfEmployedUK",
        "search_terms": "freelance admin overwhelmed",
        "suggested_comment_keywords": ["overwhelmed", "admin", "too much"],
    },
    {
        "likely_title": "How much should I set aside for tax as a sole trader?",
        "subreddits": "r/UKPersonalFinance, r/SelfEmployedUK",
        "search_terms": "sole trader tax set aside how much",
        "suggested_comment_keywords": ["tax", "sole trader", "how much", "set aside"],
    },
]


def generate_html_digest():
    """Generate the full HTML email digest."""
    today = date.today()
    days_left = config.days_until_deadline()

    # Get all content
    tweets = get_daily_twitter_posts(config.TWITTER_MAX_POSTS_PER_DAY)
    reddit_posts = get_all_reddit_posts()[:3]
    quora_answers = get_daily_quora_answers(config.QUORA_ANSWERS_PER_DAY)

    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f0; margin: 0; padding: 20px; color: #2d2d2d; }}
  .container {{ max-width: 700px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: #c9a96e; padding: 30px; text-align: center; }}
  .header h1 {{ margin: 0; font-size: 24px; letter-spacing: 1px; }}
  .header p {{ margin: 8px 0 0; color: #e0d5c1; font-size: 14px; }}
  .deadline {{ background: #fff3cd; border-left: 4px solid #c9a96e; padding: 15px 20px; margin: 20px; border-radius: 0 8px 8px 0; }}
  .deadline strong {{ color: #856404; font-size: 18px; }}
  .section {{ padding: 20px; border-bottom: 1px solid #eee; }}
  .section-title {{ font-size: 18px; font-weight: bold; color: #1a1a2e; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #c9a96e; }}
  .platform-badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }}
  .badge-twitter {{ background: #e8f4fd; color: #1da1f2; }}
  .badge-reddit {{ background: #fff0e6; color: #ff4500; }}
  .badge-quora {{ background: #fce4ec; color: #b92b27; }}
  .content-card {{ background: #fafaf8; border: 1px solid #e8e8e4; border-radius: 8px; padding: 15px; margin-bottom: 12px; }}
  .content-card h4 {{ margin: 0 0 8px; color: #1a1a2e; }}
  .content-text {{ white-space: pre-wrap; font-size: 13px; line-height: 1.5; color: #444; }}
  .chars {{ font-size: 11px; color: #888; margin-top: 5px; }}
  .comment-opp {{ background: #f0f7ff; border: 1px solid #cce0ff; border-radius: 8px; padding: 15px; margin-bottom: 12px; }}
  .comment-opp h4 {{ margin: 0 0 5px; color: #1a1a2e; font-size: 14px; }}
  .search-link {{ font-size: 12px; color: #1da1f2; }}
  .suggested {{ background: #f8f8f5; border-left: 3px solid #c9a96e; padding: 10px 15px; margin-top: 8px; font-size: 13px; line-height: 1.5; color: #555; }}
  .footer {{ background: #1a1a2e; color: #999; padding: 20px; text-align: center; font-size: 11px; }}
  .footer a {{ color: #c9a96e; }}
  .how-to {{ background: #e8f5e9; border-radius: 8px; padding: 15px; margin: 15px 20px; font-size: 13px; }}
  .how-to code {{ background: #d4edda; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">

<div class="header">
  <h1>NEXORAFUTURE</h1>
  <p>Daily Content Digest &mdash; {today.strftime('%A, %B %d, %Y')}</p>
</div>

<div class="deadline">
  <strong>{days_left} days until MTD deadline (April 6)</strong><br>
  <span style="font-size:13px; color:#856404;">Peak engagement window &mdash; every post counts right now.</span>
</div>

<!-- TWITTER SECTION -->
<div class="section">
  <div class="section-title">Twitter/X &mdash; Today's Tweets</div>
  <p style="font-size:13px; color:#666; margin-top:0;">Copy each tweet and paste into X. Aim to post at: 8am, 12pm, 5pm, 8pm UK time.</p>
"""

    for i, tweet in enumerate(tweets, 1):
        text_escaped = tweet["full_text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html += f"""
  <div class="content-card">
    <span class="platform-badge badge-twitter">Tweet {i} &mdash; {tweet['category']}</span>
    <div class="content-text">{text_escaped}</div>
    <div class="chars">{len(tweet['full_text'])}/280 characters</div>
  </div>
"""

    html += """
</div>

<!-- REDDIT COMMENT OPPORTUNITIES -->
<div class="section">
  <div class="section-title">Reddit &mdash; Comment Opportunities</div>
  <p style="font-size:13px; color:#666; margin-top:0;">Search for these post types on Reddit and reply with the suggested comments. Be genuine, be helpful, build trust.</p>
"""

    for opp in REDDIT_COMMENT_OPPORTUNITIES:
        comment = get_reddit_comment(opp["suggested_comment_keywords"])
        if comment:
            # Truncate for email readability
            comment_preview = comment[:400] + "..." if len(comment) > 400 else comment
            comment_escaped = comment_preview.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

            search_url = f"https://www.reddit.com/search/?q={opp['search_terms'].replace(' ', '+')}&sort=new&t=week"

            html += f"""
  <div class="comment-opp">
    <h4>{opp['likely_title']}</h4>
    <div style="font-size:12px; color:#666; margin-bottom:8px;">Look in: {opp['subreddits']}</div>
    <a class="search-link" href="{search_url}">Search Reddit for this &rarr;</a>
    <div class="suggested">{comment_escaped}</div>
  </div>
"""

    html += """
</div>

<!-- REDDIT POSTS -->
<div class="section">
  <div class="section-title">Reddit &mdash; Original Posts (1-2 per week)</div>
  <p style="font-size:13px; color:#666; margin-top:0;">Post ONE of these to a single subreddit. Do not cross-post.</p>
"""

    for post in reddit_posts:
        title_escaped = post["title"].replace("&", "&amp;").replace("<", "&lt;")
        body_preview = post["body"][:300] + "..." if len(post["body"]) > 300 else post["body"]
        body_escaped = body_preview.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

        html += f"""
  <div class="content-card">
    <span class="platform-badge badge-reddit">{post['type']}</span>
    <h4>{title_escaped}</h4>
    <div style="font-size:12px; color:#666; margin-bottom:8px;">Subreddits: r/{', r/'.join(post['subreddits'])}</div>
    <div class="content-text" style="font-size:12px;">{body_escaped}</div>
  </div>
"""

    html += """
</div>

<!-- QUORA SECTION -->
<div class="section">
  <div class="section-title">Quora &mdash; Answers to Post</div>
  <p style="font-size:13px; color:#666; margin-top:0;">Find matching questions on Quora and paste these answers.</p>
"""

    for i, answer in enumerate(quora_answers, 1):
        q_escaped = answer["question"].replace("&", "&amp;").replace("<", "&lt;")
        a_preview = answer["answer"][:400] + "..." if len(answer["answer"]) > 400 else answer["answer"]
        a_escaped = a_preview.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

        html += f"""
  <div class="content-card">
    <span class="platform-badge badge-quora">Answer {i}</span>
    <h4>Q: {q_escaped}</h4>
    <div class="content-text" style="font-size:12px;">{a_escaped}</div>
  </div>
"""

    html += f"""
</div>

<div class="how-to">
  <strong>Quick commands:</strong><br>
  <code>python run.py --tweet-copy 1</code> &mdash; Copy tweet 1 to clipboard<br>
  <code>python run.py --tweet-batch</code> &mdash; Regenerate all tweets<br>
  <code>python run.py --quora</code> &mdash; Get full Quora answers<br>
  <code>python run.py --dashboard</code> &mdash; See posting stats
</div>

<div class="footer">
  {config.COPYRIGHT}<br>
  {config.DISCLAIMER_SHORT}<br><br>
  <a href="https://{config.WEBSITE_URL}">nexorafuture.co.uk</a> &mdash;
  <a href="https://github.com/himanshurally/nexorafuture-automation">Source Code</a>
</div>

</div>
</body>
</html>"""

    return html


def generate_plaintext_digest():
    """Generate plain text version of the digest."""
    today = date.today()
    days_left = config.days_until_deadline()

    tweets = get_daily_twitter_posts(config.TWITTER_MAX_POSTS_PER_DAY)
    quora_answers = get_daily_quora_answers(config.QUORA_ANSWERS_PER_DAY)

    text = f"""NEXORAFUTURE DAILY CONTENT DIGEST
{today.strftime('%A, %B %d, %Y')}
{'='*50}

MTD DEADLINE: {days_left} days remaining (April 6)

--- TWITTER/X (post at 8am, 12pm, 5pm, 8pm UK) ---

"""
    for i, tweet in enumerate(tweets, 1):
        text += f"[Tweet {i} - {tweet['category']}]\n{tweet['full_text']}\n[{len(tweet['full_text'])}/280 chars]\n\n"

    text += """--- REDDIT COMMENT OPPORTUNITIES ---
Search these on Reddit (sort by New, past week) and reply helpfully:

"""
    for opp in REDDIT_COMMENT_OPPORTUNITIES:
        text += f"Post type: {opp['likely_title']}\n"
        text += f"Look in: {opp['subreddits']}\n"
        text += f"Search: https://www.reddit.com/search/?q={opp['search_terms'].replace(' ', '+')}&sort=new&t=week\n\n"

    text += """--- QUORA ANSWERS ---

"""
    for answer in quora_answers:
        text += f"Q: {answer['question']}\nA: {answer['answer'][:300]}...\n\n"

    text += f"""{'='*50}
{config.COPYRIGHT}
{config.DISCLAIMER_SHORT}
"""
    return text


if __name__ == "__main__":
    html = generate_html_digest()
    output_path = os.path.join(config.OUTPUT_DIR, "daily_digest.html")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)
    print(f"Digest saved to: {output_path}")

    plain = generate_plaintext_digest()
    print("\n" + plain)
