"""
NexoraFuture Content Engine
Template-based content generator - no AI API calls needed.
Copyright 2026 NexoraFuture. All rights reserved.
"""

import json
import os
import random
from datetime import datetime, date

import config


def load_templates(filename):
    path = os.path.join(config.TEMPLATES_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)


def get_dynamic_vars():
    """Variables that get substituted into templates."""
    today = date.today()
    days = config.days_until_deadline()
    week_num = (today - date(2026, 1, 1)).days // 7 + 1
    return {
        "days": str(days),
        "date": today.strftime("%B %d, %Y"),
        "date_short": today.strftime("%d %b"),
        "week": str(week_num),
        "year": str(today.year),
        "product_price": config.PRODUCT_PRICE,
        "brand": config.BRAND_NAME,
        "website": config.WEBSITE_URL,
    }


def fill_template(text, variables=None):
    """Replace {placeholder} variables in template text."""
    if variables is None:
        variables = get_dynamic_vars()
    for key, val in variables.items():
        text = text.replace("{" + key + "}", val)
    return text


# ============================================================
# TWITTER
# ============================================================

def get_twitter_post(category=None, used_indices=None):
    """
    Get a random twitter post from templates.
    Returns (category, index, formatted_text, hashtags)
    """
    templates = load_templates("twitter_posts.json")
    if used_indices is None:
        used_indices = {}

    if category is None:
        # Weight categories: more educational/value, less CTA
        weights = {
            "mtd_deadline": 20,
            "mtd_educational": 25,
            "freelancer_tips": 20,
            "productivity": 15,
            "nexorafuture_brand": 10,
            "stats_and_facts": 5,
            "soft_cta": 5,
        }
        available = [c for c in weights if c in templates]
        category = random.choices(
            available, weights=[weights[c] for c in available], k=1
        )[0]

    posts = templates.get(category, [])
    if not posts:
        return None

    # Avoid recently used posts
    used = used_indices.get(category, [])
    available_indices = [i for i in range(len(posts)) if i not in used]
    if not available_indices:
        # Reset if all used
        available_indices = list(range(len(posts)))
        used_indices[category] = []

    idx = random.choice(available_indices)
    post = posts[idx]
    variables = get_dynamic_vars()
    text = fill_template(post["text"], variables)
    hashtags = post.get("hashtags", [])

    return {
        "category": category,
        "index": idx,
        "text": text,
        "hashtags": hashtags,
        "full_text": text + "\n\n" + " ".join(hashtags),
    }


def get_daily_twitter_posts(count=4):
    """Generate a set of unique posts for today."""
    posts = []
    used_indices = {}
    used_categories = []

    for _ in range(count):
        # Try to vary categories
        post = get_twitter_post(used_indices=used_indices)
        if post:
            used_indices.setdefault(post["category"], []).append(post["index"])
            posts.append(post)
    return posts


# ============================================================
# REDDIT
# ============================================================

def get_reddit_comment(keywords_found):
    """
    Find the best matching comment template for given keywords.
    Returns the comment text or None.
    """
    templates = load_templates("reddit_comments.json")
    variables = get_dynamic_vars()
    best_match = None
    best_score = 0

    for category, comments in templates.items():
        for comment in comments:
            template_keywords = [k.lower() for k in comment["keywords"]]
            found_lower = [k.lower() for k in keywords_found]
            score = sum(1 for k in template_keywords if any(k in f for f in found_lower))
            if score > best_score:
                best_score = score
                best_match = comment

    if best_match:
        return fill_template(best_match["comment"], variables)
    return None


def get_reddit_post(post_type="educational"):
    """Get a random reddit post template."""
    templates = load_templates("reddit_posts.json")
    posts = templates.get(post_type, [])
    if not posts:
        return None

    post = random.choice(posts)
    variables = get_dynamic_vars()
    return {
        "title": fill_template(post["title"], variables),
        "body": fill_template(post["body"], variables),
        "subreddits": post["subreddits"],
        "flair": post.get("flair"),
    }


def get_all_reddit_posts():
    """Get all available reddit post templates."""
    templates = load_templates("reddit_posts.json")
    variables = get_dynamic_vars()
    all_posts = []
    for post_type, posts in templates.items():
        for post in posts:
            all_posts.append({
                "type": post_type,
                "title": fill_template(post["title"], variables),
                "body": fill_template(post["body"], variables),
                "subreddits": post["subreddits"],
            })
    return all_posts


# ============================================================
# QUORA
# ============================================================

def get_quora_answer(topic=None):
    """Get a random quora answer template."""
    templates = load_templates("quora_answers.json")
    variables = get_dynamic_vars()

    if topic:
        answers = templates.get(topic, [])
    else:
        all_answers = []
        for cat_answers in templates.values():
            all_answers.extend(cat_answers)
        answers = all_answers

    if not answers:
        return None

    answer = random.choice(answers)
    return {
        "question": fill_template(answer["question_pattern"], variables),
        "answer": fill_template(answer["answer"], variables),
    }


def get_daily_quora_answers(count=2):
    """Generate quora answers for today."""
    templates = load_templates("quora_answers.json")
    variables = get_dynamic_vars()
    all_answers = []
    for cat_answers in templates.values():
        for a in cat_answers:
            all_answers.append({
                "question": fill_template(a["question_pattern"], variables),
                "answer": fill_template(a["answer"], variables),
            })

    random.shuffle(all_answers)
    return all_answers[:count]


# ============================================================
# PREVIEW
# ============================================================

def preview_all():
    """Print a preview of today's generated content."""
    print("=" * 60)
    print(f"  NEXORAFUTURE CONTENT PREVIEW - {date.today()}")
    print(f"  Days until MTD deadline: {config.days_until_deadline()}")
    print("=" * 60)

    print("\n--- TWITTER (4 posts) ---\n")
    tweets = get_daily_twitter_posts(4)
    for i, t in enumerate(tweets, 1):
        print(f"[Tweet {i}] ({t['category']})")
        print(t["full_text"])
        print()

    print("\n--- REDDIT POSTS ---\n")
    posts = get_all_reddit_posts()
    for p in posts[:3]:
        print(f"[{p['type']}] r/{', r/'.join(p['subreddits'])}")
        print(f"Title: {p['title']}")
        print(f"Body: {p['body'][:150]}...")
        print()

    print("\n--- QUORA ANSWERS ---\n")
    answers = get_daily_quora_answers(2)
    for a in answers:
        print(f"Q: {a['question']}")
        print(f"A: {a['answer'][:200]}...")
        print()


if __name__ == "__main__":
    preview_all()
