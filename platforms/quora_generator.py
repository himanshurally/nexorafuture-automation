"""
NexoraFuture Quora Content Generator
Generates ready-to-paste answers for Quora (no API available).
Copyright 2026 NexoraFuture. All rights reserved.
"""

import json
import os
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from content_engine import get_daily_quora_answers, get_quora_answer

OUTPUT_DIR = os.path.join(config.OUTPUT_DIR, "quora")


def generate_daily():
    """Generate today's Quora answers and save to files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    answers = get_daily_quora_answers(config.QUORA_ANSWERS_PER_DAY)
    today = date.today().isoformat()

    print(f"\n{'='*50}")
    print(f"  QUORA ANSWERS - {today}")
    print(f"{'='*50}\n")

    for i, answer in enumerate(answers, 1):
        # Save to file
        filename = f"{today}_answer_{i}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        content = f"QUESTION: {answer['question']}\n"
        content += f"{'='*50}\n\n"
        content += answer["answer"]
        content += f"\n\n---\n{config.DISCLAIMER_SHORT}"

        with open(filepath, "w") as f:
            f.write(content)

        # Print preview
        print(f"[Answer {i}] Saved to: {filename}")
        print(f"Q: {answer['question']}")
        print(f"A: {answer['answer'][:200]}...")
        print()

    print(f"\nGenerated {len(answers)} answers in {OUTPUT_DIR}/")
    print("Copy-paste these to Quora when you find matching questions.")


def generate_for_topic(topic):
    """Generate an answer for a specific topic."""
    answer = get_quora_answer(topic)
    if not answer:
        print(f"No template found for topic: {topic}")
        return

    print(f"\nQ: {answer['question']}")
    print(f"\n{answer['answer']}")
    print(f"\n---\n{config.DISCLAIMER_SHORT}")


def list_topics():
    """List available answer topics."""
    templates = json.load(open(os.path.join(config.TEMPLATES_DIR, "quora_answers.json")))
    print("\nAvailable topics:")
    for topic in templates:
        count = len(templates[topic])
        print(f"  - {topic} ({count} answers)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NexoraFuture Quora Generator")
    parser.add_argument("--generate", action="store_true", help="Generate daily answers")
    parser.add_argument("--topic", type=str, help="Generate for specific topic")
    parser.add_argument("--topics", action="store_true", help="List available topics")
    args = parser.parse_args()

    if args.topics:
        list_topics()
    elif args.topic:
        generate_for_topic(args.topic)
    else:
        generate_daily()
