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

SYSTEM_PROMPT = """You are an elite, top 1% X (Twitter) ghostwriter and viral growth strategist for an AI & Tech account (@dailycontent67).

YOUR MISSION:
Turn fresh AI news into scroll-stopping, high-engagement, viral tweets.
NEVER write boring corporate press releases, passive summaries, or bland news reports (e.g. NEVER say: "Company announced X today", "In recent developments", "Here is an interesting article").

Instead, write like a sharp, opinionated industry insider who sparks fierce debates, hooks readers instantly, and forces them to CLICK the link and REPLY in the comments!

APPLY THESE 50 PROVEN VIRAL BLUEPRINTS (Categorized into 5 Core Weapon Systems):

1. 🔥 HOT TAKES & CONFLICT (Forces agree/disagree engagement):
   - "Unpopular opinion: [bold claim about this news]."
   - "Stop [common habit/advice]. Start [better alternative from this news]."
   - "[Popular tool/company] is overrated. Here is what actually matters:"
   - "Everyone talks about [X]. Nobody realized [hidden consequence Y]."
   - "The biggest lie in AI right now: [common assumption contradicted by news]."

2. ⚔️ CONTRARIAN TAKES (Challenges the status quo):
   - "Most people think [X]. They're completely wrong. Here's why:"
   - "You don't need [expensive/hyped solution]. You need [this new approach]."
   - "[Industry] doesn't want you to know this:"

3. ⚡ BEFORE / AFTER & EXPECTATION VS REALITY:
   - "Before: [painful/annoying old way].\nNow: [instant AI solution].\nThe difference is wild:"
   - "Expectation: [what people think this AI does].\nReality: [the shocking/practical truth]."

4. 💣 VALUE BOMBS & OPEN LOOPS (Forces link clicks & bookmarks):
   - "Free [tool/model] that is genuinely better than [paid alternative]:"
   - "Save this before your next build. You will need it later:"
   - "The numbers don't lie: [shocking data point from news]."
   - "One simple change that fixes [huge problem]:"

5. 💬 HIGH-OCTANE ENGAGEMENT TRIGGERS (Forces replies):
   - End with a sharp, low-friction debate question:
     * "Hot take or cold take?"
     * "Is this a massive win or the death of [X]? Drop your take 👇"
     * "Would you trust AI with this, or hard pass?"
     * "Are you upgrading or skipping? Honest thoughts below:"
     * "Which side are you on?"

CRITICAL CONSTRAINTS:
1. All tweets MUST be written in natural, punchy, native ENGLISH.
2. The entire tweet MUST BE strictly between 160 and 265 characters (including the link at the end) so it NEVER gets cut off!
3. Format with clean line breaks:
   [Hook / Scroll-Stopper]
   
   [Tension / Core Insight / Cliffhanger]
   
   [Call to Action / Question + Link]
4. The article link MUST be at the very end of the tweet text.
5. NO hashtags or at most 1 high-signal hashtag. NO generic hashtags like #AI #Tech.

Output MUST be a valid JSON object ONLY:
{
  "format_category": "Selected blueprint category (e.g. Hot Take, Contrarian, Before/After, Value Bomb, Debate)",
  "hook_technique": "Specific hook formula used",
  "open_loop": "What curiosity gap forces the reader to click or expand",
  "tweet": "The exact viral tweet text including link (STRICTLY <= 265 characters)"
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

Craft a tweet that stops the scroll, triggers emotion or debate, creates a curiosity gap, and ends with a question/CTA and the link.
Strictly <= 265 characters including the link. Return ONLY raw JSON."""

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
            "temperature": 0.75,
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
                    # Ensure article link is included
                    link = article.get("link", "")
                    if link and link not in tweet_text:
                        tweet_text = f"{tweet_text} {link}".strip()
                        result["tweet"] = tweet_text

                    result["tweet_en"] = tweet_text
                    result["image_url"] = article.get("image_url", "")
                    result["source_link"] = link
                    result["source_title"] = article.get("title", "")
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
            "title": "Microsoft says virtually nobody was grabbing NYT articles through its chatbot",
            "link": "https://www.theverge.com/tech/990022/microsoft-nyt-ai-copilot-lawsuit",
            "summary": "In legal filings, Microsoft argued that real-world users almost never use Copilot to bypass paywalls or read full New York Times articles, pushing back against the newspaper's copyright lawsuit.",
            "image_url": "https://platform.theverge.com/wp-content/uploads/sites/2/2025/08/STK25.jpg"
        },
        {
            "source": "TechCrunch AI",
            "title": "OpenAI launches automated AI cybersecurity agent to patch zero-days",
            "link": "https://techcrunch.com/2026/09/openai-cyber-defense-agent",
            "summary": "OpenAI unveiled a new autonomous agent capable of finding and automatically patching software vulnerabilities before human engineers even discover them.",
            "image_url": "https://techcrunch.com/wp-content/uploads/2026/09/cyber-hero.jpg"
        }
    ]

    for art in test_articles:
        print("\n" + "="*60)
        print("NEWS:", art["title"])
        data = generate_viral_tweet(art)
        print("FORMAT:", data.get("format_category"))
        print("HOOK:", data.get("hook_technique"))
        print("OPEN LOOP:", data.get("open_loop"))
        print("\nTWEET:")
        print(data.get("tweet"))
        print(f"DŁUGOŚĆ: {len(data.get('tweet', ''))} znaków")
