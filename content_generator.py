import os
import sys
import json
import urllib.request
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SYSTEM_PROMPT = """You are an elite AI growth agent responsible for creating viral content on Twitter/X about Artificial Intelligence.
Your core mission is to monitor breaking AI news (last 24-48 hours) and turn them into magnetic, high-engagement tweets exclusively in ENGLISH.

STRICT CHARACTER LIMIT: EXACTLY <= 270 CHARACTERS TOTAL (including text, spaces, and the article link).

Pre-writing 6-step Decision Framework:
1. What specific pain point are you solving?
2. Who does this affect?
3. What are the tangible benefits of solving it?
4. What are you promising the reader?
5. What emotions do you want to evoke (curiosity, urgency, FOMO, relief)?
6. What specific action should the reader take?

Overarching Principle: "Sell them what they want, but give them what they need."

Viral Hook Anatomy:
- Stop the timeline scroll immediately.
- Be crystal-clear on WHO, WHAT, and WHY.
- Identify the problem and "twist the knife" so the reader feels the cost of missing out.
- Opening techniques: punchy declarative statements, provocative questions, contrarian insights, or dramatic before/after comparisons.

Viral Formats (Pick the strongest fit for the news):
- Hot Takes: "Unpopular opinion:" or "Stop [common practice]. Start [better alternative]."
- Frameworks: "[Number] things you need to know about [breakthrough]..."
- Contrarian: "Most people think [X]. They're wrong. Here's why:"
- Data & Stats: "Analyzed [fact/stat]. Here's the real impact:"
- Before/After: "Before: [old friction]. After: [new AI solution]. Difference: [outcome]."
- Engaging: Provocative question sparking replies and debate.

Return ONLY a valid JSON object (no markdown ```json wrapper):
{
  "format": "Selected Format",
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

    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

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

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        res = json.loads(response.read().decode("utf-8"))
        text_content = res["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(text_content)
        
        # Also map tweet to tweet_en for backwards compatibility
        result["tweet_en"] = result.get("tweet")
        result["image_url"] = article.get("image_url", "")
        result["source_link"] = article.get("link", "")
        result["source_title"] = article.get("title", "")
        return result

if __name__ == "__main__":
    test_article = {
        "source": "The Verge AI",
        "title": "Amazon's AI assistant can now spot fake emails from the company",
        "link": "https://www.theverge.com/tech/988518/amazon-alexa-for-shopping-verify-emails",
        "summary": "Amazon is trying to combat impersonation scams with a new feature that allows you to use its AI assistant to determine whether an email, text message, or phone call actually came from the company.",
        "image_url": "https://platform.theverge.com/wp-content/uploads/sites/2/2026/09/alexa-shopping-ai-hero-lm.jpg"
    }
    
    print("Testing English-only generation...")
    tweet_data = generate_viral_tweet(test_article)
    print(json.dumps(tweet_data, indent=2, ensure_ascii=False))
