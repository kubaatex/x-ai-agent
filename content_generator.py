import os
import sys
import json
import time
import urllib.request
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SYSTEM_PROMPT = """You are an elite X (Twitter) growth strategist and AI news curator.
Your task is to analyze fresh AI news and craft a viral, high-engagement tweet in English.

You MUST apply the following 6 Decision Questions:
1. What PROBLEM does this news highlight or solve?
2. Who is the AUDIENCE (developers, founders, creators, everyday users)?
3. What is the key BENEFIT/IMPACT?
4. What is the PROMISE/HOOK to stop users from scrolling?
5. What EMOTIONS should this evoke (curiosity, urgency, FOMO, excitement, contrarian insight)?
6. What ACTION should they take (read the link, share their take)?

Select the best VIRAL FORMAT from these templates:
- Before/After (e.g. "Before: ... Now: ...")
- Hot Takes & Unpopular Opinions
- Contrarian Angle
- Framework & Playbook
- Statistics / Shocking data
- Pure Engagement / Question hook

CRITICAL RULES:
1. All tweets MUST be written in natural, punchy ENGLISH.
2. The tweet MUST include the article link at the end!
3. Maximum tweet length: 270 characters (including link).
4. No excessive hashtags (maximum 1 or 2 high-signal tags, or none).
5. Output MUST be valid JSON only.

Output Format:
{
  "format": "Selected format name",
  "decision_process": {
    "problem": "...",
    "audience": "...",
    "benefits": "...",
    "promise": "...",
    "emotions": "...",
    "action": "..."
  },
  "tweet": "The viral English tweet (STRICTLY <= 270 characters including the link)"
}
"""

def generate_viral_tweet(article: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env file!")

    models_to_try = [
        os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        "gemini-flash-latest",
        "gemini-3.6-flash"
    ]

    prompt = f"""Analyze this fresh AI news article and produce an English viral tweet:
Title: {article.get('title')}
Source: {article.get('source')}
Summary: {article.get('summary')}
Article Link: {article.get('link')}

Remember:
1. Write ONLY in English.
2. The entire tweet MUST BE <= 270 characters including the article link!
3. Return ONLY raw JSON.
"""

    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
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
                    
                    result["tweet_en"] = result.get("tweet")
                    result["image_url"] = article.get("image_url", "")
                    result["source_link"] = article.get("link", "")
                    result["source_title"] = article.get("title", "")
                    return result
            except (urllib.error.HTTPError, TimeoutError, Exception) as e:
                last_err = e
                print(f"⚠️ Chwilowy błąd Gemini ({model}, próba {attempt+1}/3): {e}. Ponawiam za 2s...")
                time.sleep(2)

    raise last_err or RuntimeError("Nie udało się wygenerować tweeta przez Gemini.")

if __name__ == "__main__":
    test_article = {
        "source": "The Verge AI",
        "title": "Amazon's AI assistant can now spot fake emails from the company",
        "link": "https://www.theverge.com/tech/988518/amazon-alexa-for-shopping-verify-emails",
        "summary": "Amazon is trying to combat impersonation scams with a new feature that allows you to use its AI assistant to determine whether an email, text message, or phone call actually came from the company.",
        "image_url": "https://example.com/test.jpg"
    }
    print("Testing generate_viral_tweet...")
    data = generate_viral_tweet(test_article)
    print(json.dumps(data, indent=2))
