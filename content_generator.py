import os
import sys
import json
import time
import random
import urllib.request
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

VIRAL_PROMPT = """You are an elite, top 1% X (Twitter) ghostwriter and growth hacker for a modern AI & Tech brand (@dailycontent67).

CRITICAL RULE #1: NEVER BE A BORING RSS BOT!
- DO NOT summarize news like a newspaper ("Company announced X today", "In a new filing...").
- DO NOT put external links (like theverge.com or techcrunch.com) in the main tweet text! External links murder reach on X because the algorithm suppresses them, and they make the account look like a spammy bot.
- If referencing a source, use: "(Full breakdown in the reply 👇)" or "(Link in comments 👇)" or omit the link completely!

YOUR MISSION:
Write punchy, high-voltage, scroll-stopping tweets that maximize REPLIES, RETWEETS, and BOOKMARKS.

CHOOSE FROM THESE 5 PROVEN VIRAL ARCHETYPES:

1. 🔥 THE UNPOPULAR OPINION / HOT TAKE (Drives controversy & replies):
   "Unpopular opinion: [bold, controversial claim about AI/dev/tools]."
   [1-2 sentences explaining why the mainstream is wrong]
   "Agree or disagree? Drop your take 👇"

2. ⚔️ THE "STOP DOING X / START DOING Y" (Actionable & authoritative):
   "Stop [common mistake people make with AI/coding/productivity]."
   "Start [specific, counter-intuitive alternative]."
   "The difference in output is night and day. What's your current stack?"

3. ⚡ THE BEFORE / AFTER TRANSFORMATION (Relatable & viral):
   "Before: [relatable frustration / 4 hours of tedious work].\nNow: [10-second AI workflow].\n\nThe gap between people using AI and people ignoring it is widening fast."
   "Where do you stand? 👇"

4. 📦 THE CURATED LIST / VALUE BOMB (Drives bookmarks & shares):
   "[Number] underrated AI tools that will save you 10+ hours this week:\n\n1. [Tool] — [one-line superpower]\n2. [Tool] — [one-line superpower]\n3. [Tool] — [one-line superpower]\n\nBookmark this before you lose it. Which one is your favorite?"

5. 🎙️ THE SHOCKING INSIDER TAKE (Open Loop & Debate):
   [Hook exposing a crazy reality or recent industry scandal/shift]
   [Tension / Conflict: What everyone missed]
   "Is this a massive win or a catastrophic risk? Honest thoughts below 👇"

FORMATTING & CONSTRAINTS:
- 100% natural, punchy, conversational native ENGLISH.
- Clean line breaks (Hook -> Context -> Engaging Question / CTA).
- NO external URLs in the tweet text.
- Under 270 characters (easy to read on mobile without clicking 'Show more').
- Zero corporate fluff. Zero generic hashtags (#AI #Tech).

Output JSON format ONLY:
{
  "archetype": "Selected archetype name",
  "hook": "The first line scroll-stopper",
  "engagement_trigger": "Why people will comment or retweet",
  "tweet": "The full viral tweet text (strictly <= 270 chars, NO HTTP LINKS)"
}
"""

def generate_viral_tweet(article: dict = None) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env file!")

    models_to_try = [
        os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        "gemini-flash-latest",
        "gemini-3.6-flash"
    ]

    context = ""
    if article:
        context = f"""
Current AI context to spark ideas:
Title: {article.get('title')}
Summary: {article.get('summary')}
Source: {article.get('source')}
"""

    prompt = f"""Generate a high-engagement viral tweet for @dailycontent67.
{context}

Remember:
- Pick the best archetype (Hot Take, Stop/Start, Before/After, Value Bomb, or Debate).
- DO NOT paste any external links in the tweet text.
- Make it polarizing, relatable, or immediately bookmarkable.
- End with a question or call to action that forces people to comment.
- Return valid JSON only."""

    payload = {
        "systemInstruction": {
            "parts": [{"text": VIRAL_PROMPT}]
        },
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.85,
            "responseMimeType": "application/json"
        }
    }

    last_err = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    res = json.loads(response.read().decode("utf-8"))
                    text_content = res["candidates"][0]["content"]["parts"][0]["text"]
                    result = json.loads(text_content)
                    
                    tweet_text = result.get("tweet", "").strip()
                    
                    # We do NOT append external links to the main tweet!
                    # Only keep image if available and relevant
                    result["tweet_en"] = tweet_text
                    result["tweet"] = tweet_text
                    
                    # If image is a boring corporate logo, don't attach it
                    img = article.get("image_url", "") if article else ""
                    if img and ("logo" in img.lower() or "copilot" in img.lower() and "icon" in img.lower()):
                        img = "" # Skip boring logos
                    result["image_url"] = img
                    result["source_link"] = article.get("link", "") if article else ""
                    result["source_title"] = article.get("title", "") if article else ""
                    return result
            except Exception as e:
                last_err = e
                print(f"⚠️ Chwilowy błąd Gemini ({model}, próba {attempt+1}/3): {e}. Ponawiam za 2s...")
                time.sleep(2)

    raise last_err or RuntimeError("Nie udało się wygenerować tweeta przez Gemini.")

if __name__ == "__main__":
    test_articles = [
        {
            "source": "The Verge AI",
            "title": "OpenAI hid rogue AI agents hijacking websites for weeks",
            "link": "https://www.theverge.com/ai-agents-scandal",
            "summary": "Researchers discovered AI agents independently coordinated on external forums without human oversight.",
            "image_url": "https://example.com/robot.jpg"
        },
        {
            "source": "TechCrunch",
            "title": "Cursor AI reaches 100M ARR as devs abandon traditional IDEs",
            "link": "https://techcrunch.com/cursor-growth",
            "summary": "Developers are shifting completely to AI-native IDEs, threatening VS Code extensions.",
            "image_url": ""
        }
    ]

    for art in test_articles:
        print("\n" + "="*60)
        print("TEMAT:", art["title"])
        data = generate_viral_tweet(art)
        print("ARCHETYPE:", data.get("archetype"))
        print("HOOK:", data.get("hook"))
        print("\nTWEET:")
        print(data.get("tweet"))
        print(f"DŁUGOŚĆ: {len(data.get('tweet', ''))} znaków | CZY MA LINK: {'http' in data.get('tweet', '')}")
