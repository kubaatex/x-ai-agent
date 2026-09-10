import os
import sys
import json
import time
import random
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from news_fetcher import fetch_latest_ai_news, extract_og_image
from content_generator import ALL_PILLARS, generate_viral_tweet, select_next_pillar
from poster import publish_tweet, load_history

# Domyślny język publikacji
DEFAULT_LANG = os.getenv("POST_LANGUAGE", "EN")

def get_already_posted_links():
    history = load_history()
    posted = set()
    for h in history:
        if "source_link" in h and h["source_link"]:
            posted.add(h["source_link"])
    return posted

def run_single_cycle(dry_run: bool = False, lang: str = DEFAULT_LANG, forced_pillar: str = None):
    print("\n" + "="*60)
    print(f"🤖 AGENT AI START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    history = load_history()
    pillar = forced_pillar or select_next_pillar(history)
    print(f"🎯 WYBRANY FILAR TREŚCI: [{pillar}]")

    candidate = None
    if pillar == "BREAKING_TECH_TAKE":
        print("1️⃣ Pobieranie najświeższych wiadomości ze świata AI...")
        news_items = fetch_latest_ai_news(limit=25)
        if news_items:
            already_posted = get_already_posted_links()
            for item in news_items:
                if item["link"] not in already_posted:
                    candidate = item
                    break
            if not candidate:
                candidate = news_items[0]

            print(f"📰 Wybrano news do inspiracji: {candidate['title']} ({candidate['source']})")
            if not candidate.get("image_url"):
                candidate["image_url"] = extract_og_image(candidate["link"])
    else:
        print(f"💡 Generowanie postu autorskiego z bazy wiedzy bota (Pillar: {pillar})...")

    print(f"2️⃣ Generowanie viralowego wpisu w formacie {pillar} (z wykluczeniem powtórzeń)...")
    tweet_data = generate_viral_tweet(
        article=candidate,
        forced_pillar=pillar,
        recent_tweets=history
    )

    tweet_text = tweet_data.get("tweet") or tweet_data.get("tweet_en", "")
    print(f"\n🔥 VIRAL TWEET (Format: {pillar} | {len(tweet_text)} znaków):")
    print("-" * 50)
    print(tweet_text)
    print("-" * 50)
    print(f"📸 IMAGE: {tweet_data.get('image_url') or 'Brak (Czysty tekst - wysoki zasięg)'}")

    if dry_run:
        print("\n🧪 [TRYB TESTOWY / DRY-RUN] Post NIE został wysłany na X.")
        return tweet_data

    print(f"\n3️⃣ Wysyłanie posta na X (język: {lang.upper()})...")
    result = publish_tweet(tweet_data, lang=lang)
    return result

def generate_daily_schedule(posts_per_day: int = 10, start_hour: int = 8, end_hour: int = 22):
    """Generuje 10 losowych godzin w naturalnych odstępach w ciągu dnia"""
    now = datetime.now()
    total_minutes = (end_hour - start_hour) * 60
    interval = total_minutes // posts_per_day
    
    schedule = []
    for i in range(posts_per_day):
        base_minute = (start_hour * 60) + (i * interval)
        jitter = random.randint(-12, 12)
        target_min = max(start_hour * 60, min(end_hour * 60, base_minute + jitter))
        
        target_time = now.replace(
            hour=target_min // 60,
            minute=target_min % 60,
            second=random.randint(0, 59),
            microsecond=0
        )
        schedule.append(target_time)
        
    schedule.sort()
    return schedule

def run_continuous_scheduler(posts_per_day: int = 10, lang: str = DEFAULT_LANG):
    print(f"🚀 Uruchamianie agenta w trybie ciągłym: {posts_per_day} postów dziennie (Język: {lang}).")
    while True:
        today_schedule = generate_daily_schedule(posts_per_day)
        print(f"\n📅 Wygenerowano harmonogram na dzień {datetime.now().strftime('%Y-%m-%d')}:")
        for idx, t in enumerate(today_schedule, 1):
            status = "⏳ oczekuje" if t > datetime.now() else "⏭️ minęła"
            print(f"  {idx}. {t.strftime('%H:%M:%S')} - {status}")

        for target_time in today_schedule:
            now = datetime.now()
            if target_time > now:
                wait_seconds = (target_time - now).total_seconds()
                print(f"\n💤 Czekam do następnego wpisu o {target_time.strftime('%H:%M:%S')} ({int(wait_seconds//60)} min {int(wait_seconds%60)} s)...")
                time.sleep(wait_seconds)
                try:
                    run_single_cycle(dry_run=False, lang=lang)
                except Exception as e:
                    print(f"❌ Błąd podczas cyklu publikacji: {e}")

        tomorrow_8am = (datetime.now() + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
        sleep_until_morning = (tomorrow_8am - datetime.now()).total_seconds()
        if sleep_until_morning > 0:
            print(f"🌙 Zakończono posty na dzisiaj. Śpię do jutra do 08:00 ({int(sleep_until_morning//3600)}h)...")
            time.sleep(sleep_until_morning)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent AI Twitter/X do publikowania zróżnicowanych postów o AI")
    parser.add_argument("--test", action="store_true", help="Tryb testowy: generuje post, ale NIE publikuje")
    parser.add_argument("--post-now", action="store_true", help="Natychmiast generuje i publikuje 1 post na X")
    parser.add_argument("--lang", type=str, default=DEFAULT_LANG, choices=["EN", "PL"], help="Język posta do publikacji")
    parser.add_argument("--pillar", type=str, choices=ALL_PILLARS, help="Wymuszenie konkretnego filaru")
    parser.add_argument("--schedule", action="store_true", help="Uruchamia harmonogram 10 postów dziennie w tle")
    
    args = parser.parse_args()

    if args.test:
        run_single_cycle(dry_run=True, lang=args.lang, forced_pillar=args.pillar)
    elif args.post_now:
        run_single_cycle(dry_run=False, lang=args.lang, forced_pillar=args.pillar)
    elif args.schedule:
        run_continuous_scheduler(posts_per_day=10, lang=args.lang)
    else:
        run_single_cycle(dry_run=True, lang=args.lang, forced_pillar=args.pillar)
