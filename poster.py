import os
import sys
import json
import tempfile
import urllib.request
from datetime import datetime
from dotenv import load_dotenv
import tweepy

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

def get_clients():
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    # v2 Client for posting tweets
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # v1.1 API for media uploads
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)

    return client, api

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_to_history(entry: dict):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def download_image_temp(image_url: str) -> str:
    try:
        req = urllib.request.Request(
            image_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        suffix = ".jpg"
        if ".png" in image_url.lower():
            suffix = ".png"
        elif ".webp" in image_url.lower():
            suffix = ".webp"

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        with urllib.request.urlopen(req, timeout=10) as resp:
            temp_file.write(resp.read())
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"⚠️ Nie udało się pobrać zdjęcia z {image_url}: {e}")
        return None

def publish_tweet(tweet_data: dict, lang: str = "EN") -> dict:
    client, api = get_clients()

    tweet_text = tweet_data.get("tweet") or tweet_data.get("tweet_en") or tweet_data.get("tweet_pl")


    # Trim to 280 chars safety
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."

    image_url = tweet_data.get("image_url")
    media_ids = []
    temp_img_path = None

    if image_url:
        print(f"📸 Pobieranie oryginalnego zdjęcia artykułu...")
        temp_img_path = download_image_temp(image_url)
        if temp_img_path and os.path.getsize(temp_img_path) > 1024:
            try:
                print("📤 Wysyłanie zdjęcia na serwer X...")
                media = api.media_upload(filename=temp_img_path)
                media_ids.append(media.media_id)
                print(f"✅ Zdjęcie przesłane (Media ID: {media.media_id})")
            except Exception as e:
                print(f"⚠️ Błąd wysyłania mediów na X: {e}. Publikuję sam tweet.")

    try:
        print(f"🚀 Publikowanie posta ({lang.upper()}) na X...")
        response = client.create_tweet(
            text=tweet_text,
            media_ids=media_ids if media_ids else None
        )
        tweet_id = response.data["id"]
        post_url = f"https://x.com/dailycontent67/status/{tweet_id}"
        print(f"🎉 SUKCES! Tweet opublikowany: {post_url}")

        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "tweet_id": tweet_id,
            "url": post_url,
            "language": lang.upper(),
            "tweet_text": tweet_text,
            "format": tweet_data.get("format"),
            "source_title": tweet_data.get("source_title"),
            "source_link": tweet_data.get("source_link"),
            "image_url": image_url,
            "decision_process": tweet_data.get("decision_process")
        }
        save_to_history(history_entry)
        return history_entry
    finally:
        if temp_img_path and os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except Exception:
                pass
