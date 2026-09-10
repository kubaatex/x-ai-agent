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

ALL_PILLARS = [
    "VALUE_BOMB_LIST",         # 5 tools, cheat sheets, framework breakdowns (high bookmarks)
    "COMMUNITY_POLL_QUESTION",  # A/B/C/D polls, constraints, low-friction reply magnets
    "BEFORE_AFTER",            # Old workflow vs new AI workflow
    "CONTRARIAN_STOP_START",   # Stop doing X, start doing Y (opinionated advice)
    "DATA_BENCHMARK",          # Shocking stats, developer numbers, speed metrics
    "BREAKING_TECH_TAKE"       # Industry shifts from fresh news (without generic summary)
]

PILLAR_PROMPTS = {
    "VALUE_BOMB_LIST": """
ROLE: Curated AI Toolstack & Framework Creator.
FORMAT:
- Hook: "[Number] underrated AI tools [that solve a specific pain/save 10 hours]:"
- Body: 3 to 4 punchy bullet points. Format:
  1. [Tool/Model] — [exact superpower or use case]
  2. [Tool/Model] — [exact superpower or use case]
  3. [Tool/Model] — [exact superpower or use case]
  4. [Tool/Model] — [exact superpower or use case]
- Closing: "Bookmark this for your next build." OR "Which one are you testing first?"
CRITICAL: NO HTTP links. Strictly practical, actionable tools (e.g. Cursor, Claude, v0, Bolt, NotebookLM, Perplexity, Whisper, Ollama, ElevenLabs, etc.).
""",

    "COMMUNITY_POLL_QUESTION": """
ROLE: Master Community Engagement Driver.
FORMAT:
- Hook: A sharp, impossible-choice question or provocative question.
- Body: 3-4 distinct lettered options (A, B, C, D) or a creative constraint:
  "If you could only keep ONE AI tool for the rest of 2026, which one survives?

  A) Claude 3.5 Sonnet
  B) Cursor IDE
  C) ChatGPT Pro
  D) Midjourney

  You can only pick one."
OR:
  "Name an AI tool that actually delivered 100% on the hype.

  I'll start: Cursor."
CRITICAL: Zero fluff. Make replying take less than 3 seconds for the user.
""",

    "BEFORE_AFTER": """
ROLE: Workflow Transformation Storyteller.
FORMAT:
- Hook: "The speed of shipping has completely detached from team size." OR a direct contrast.
- Body:
  "Before: [relatable struggle / 3 days spent building an MVP / manual boilerplate].

  Now: [10-minute AI workflow / single prompt to deployment].

  [1 sentence concluding insight on why the gap is widening fast]."
- Closing: A thoughtful closing thought (DO NOT use "Drop your take 👇").
""",

    "CONTRARIAN_STOP_START": """
ROLE: Elite Developer Strategist & Hard Truth Teller.
FORMAT:
- Hook: "Stop [common bad habit/hype obsession in AI/coding]."
- Body:
  "Start [the real, boring, high-leverage alternative that actually works].

  [2 sentences explaining why 90% of builders get this backwards]."
- Closing: "Depth beats breadth every single time." OR a sharp, confident closing remark.
CRITICAL: DO NOT start with "Unpopular opinion:". DO NOT end with "Drop your take 👇".
""",

    "DATA_BENCHMARK": """
ROLE: Tech Data Analyst & Market Observer.
FORMAT:
- Hook: "The numbers don't lie:" OR a shocking statistic.
- Body:
  - 2 to 3 surprising data points, adoption percentages, or coding speed benchmarks.
  - 1 sentence punchline interpreting what this means for human developers or creators.
- Closing: "Are you seeing this in your day-to-day work?" OR "The shift is happening faster than expected."
""",

    "BREAKING_TECH_TAKE": """
ROLE: Deep Industry Insider & Strategic Analyst.
FORMAT:
- Hook: A captivating headline exposing a recent move, tension, or conflict in the AI industry.
- Body: 2 short punchy sentences giving the hidden implication that most people missed.
- Closing: A nuanced question forcing readers to pick a side.
CRITICAL: DO NOT say "Drop your take 👇". DO NOT summarize like a newspaper. DO NOT start with "Unpopular opinion:".
"""
}

def select_next_pillar(recent_history: list) -> str:
    """Wybiera kolejny filar tak, aby nigdy nie powtarzać tego samego formatu z rzędu."""
    used_pillars = []
    for entry in recent_history[-5:]:
        p = entry.get("format") or entry.get("archetype") or entry.get("pillar")
        if p:
            used_pillars.append(p)
    
    # Znajdź filary, które nie były używane w ostatnich 3 postach
    candidates = [p for p in ALL_PILLARS if p not in used_pillars[-3:]]
    if not candidates:
        candidates = [p for p in ALL_PILLARS if p != (used_pillars[-1] if used_pillars else "")]
    
    return random.choice(candidates) if candidates else ALL_PILLARS[0]

def generate_viral_tweet(article: dict = None, forced_pillar: str = None, recent_tweets: list = None) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in .env file!")

    pillar = forced_pillar or random.choice(ALL_PILLARS)
    pillar_instructions = PILLAR_PROMPTS.get(pillar, PILLAR_PROMPTS["VALUE_BOMB_LIST"])

    # Zbierz ostatnie tweety do weryfikacji unikalności
    recent_context = ""
    if recent_tweets:
        recent_snippets = [t.get("tweet_text", "")[:80].replace("\n", " ") for t in recent_tweets[-6:] if t.get("tweet_text")]
        if recent_snippets:
            recent_context = "RECENT TWEETS YOU MUST NOT REPEAT OR SOUND SIMILAR TO:\n" + "\n".join(f"- {s}..." for s in recent_snippets)

    news_context = ""
    if article and pillar == "BREAKING_TECH_TAKE":
        news_context = f"""
ARTICLE CONTEXT (Use as inspiration for the industry shift):
Title: {article.get('title')}
Summary: {article.get('summary')}
Source: {article.get('source')}
"""

    system_instruction = f"""You are a world-class X ghostwriter for @dailycontent67.
Your tweets consistently achieve 50,000+ impressions because they NEVER sound like bots or news summaries.

CURRENT TASK:
Generate a tweet strictly adhering to the following SPECIFIC PILLAR:
=== PILLAR: {pillar} ===
{pillar_instructions}

{recent_context}

BANNED CLICHÉS (NEVER USE THESE UNDER ANY CIRCUMSTANCE):
- NEVER use the phrase "Drop your take 👇"
- NEVER start with "Unpopular opinion:" unless the pillar explicitly permits it
- NEVER put HTTP links in the tweet text
- NEVER summarize news like a newspaper ("Company announced...", "In legal filings...")
- NEVER repeat the same opening hook or closing CTA from the recent tweets

CRITICAL CONSTRAINTS:
1. Native, punchy, rhythmic, natural English.
2. Character count: strictly between 150 and 265 characters.
3. Clean line spacing on mobile.
4. Output JSON ONLY:
{{
  "pillar": "{pillar}",
  "hook": "The first line hook",
  "tweet": "The full tweet text (strictly <= 265 chars, NO LINKS)"
}}
"""

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {
                "parts": [{"text": f"Generate a {pillar} tweet now. {news_context}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.85,
            "responseMimeType": "application/json"
        }
    }

    models_to_try = [
        os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        "gemini-flash-latest",
        "gemini-3.6-flash"
    ]

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
                    result["tweet_en"] = tweet_text
                    result["tweet"] = tweet_text
                    result["format"] = pillar
                    result["pillar"] = pillar
                    
                    # Decydowanie o grafice:
                    # Dla list, pytań, before/after - tekstowe tweety radzą sobie najlepiej (brak nudnych grafik)
                    if pillar == "BREAKING_TECH_TAKE" and article:
                        img = article.get("image_url", "")
                        # Ignoruj nudne loga (OpenAI, Copilot, itp.)
                        if img and any(bad in img.lower() for bad in ["logo", "icon", "stk155", "stk259", "copilot", "open_ai"]):
                            img = ""
                        result["image_url"] = img
                        result["source_link"] = article.get("link", "")
                        result["source_title"] = article.get("title", "")
                    else:
                        result["image_url"] = ""
                        result["source_link"] = ""
                        result["source_title"] = f"Pillar: {pillar}"
                        
                    return result
            except Exception as e:
                last_err = e
                print(f"⚠️ Chwilowy błąd Gemini ({model}, próba {attempt+1}/3): {e}. Ponawiam za 2s...")
                time.sleep(2)

    raise last_err or RuntimeError("Nie udało się wygenerować tweeta przez Gemini.")

if __name__ == "__main__":
    print("=== TESTOWANIE WSZYSTKICH 6 FILARÓW TEMATYCZNYCH ===")
    for pil in ALL_PILLARS:
        print("\n" + "="*50)
        print("FILAR:", pil)
        res = generate_viral_tweet(forced_pillar=pil)
        print("TWEET:")
        print(res.get("tweet"))
        print(f"DŁUGOŚĆ: {len(res.get('tweet', ''))} znaków | GRAFIKA: {'Brak (Czysty tekst)' if not res.get('image_url') else res.get('image_url')}")
