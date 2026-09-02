import os
import sys
import json
import urllib.request
from datetime import datetime
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
BUFFER_API_URL = "https://api.buffer.com"

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

def publish_tweet(tweet_data: dict, lang: str = "EN") -> dict:
    buffer_key = os.getenv("BUFFER_API_KEY")
    channel_id = os.getenv("BUFFER_CHANNEL_ID")

    if not buffer_key or not channel_id:
        raise ValueError("Brak BUFFER_API_KEY lub BUFFER_CHANNEL_ID w pliku .env!")

    tweet_text = tweet_data.get("tweet") or tweet_data.get("tweet_en") or tweet_data.get("tweet_pl")

    # Trim to 280 chars safety
    if len(tweet_text) > 280:
        tweet_text = tweet_text[:277] + "..."

    image_url = tweet_data.get("image_url")

    mutation = """
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        __typename
        ... on PostActionSuccess {
          post {
            id
            text
            status
          }
        }
        ... on MutationError {
          message
        }
      }
    }
    """

    post_input = {
        "channelId": channel_id,
        "text": tweet_text,
        "schedulingType": "automatic",
        "mode": "shareNow"
    }

    if image_url and (image_url.startswith("http://") or image_url.startswith("https://")):
        post_input["assets"] = [
            {
                "image": {
                    "url": image_url
                }
            }
        ]

    req = urllib.request.Request(
        BUFFER_API_URL,
        data=json.dumps({"query": mutation, "variables": {"input": post_input}}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {buffer_key}"
        }
    )

    print(f"🚀 Publikowanie posta na X (przez darmowe Buffer API)...")
    with urllib.request.urlopen(req, timeout=20) as resp:
        res = json.loads(resp.read().decode("utf-8"))

    action_data = res.get("data", {}).get("createPost", {})
    if action_data.get("__typename") == "PostActionSuccess":
        post_obj = action_data.get("post", {})
        post_id = post_obj.get("id")
        status = post_obj.get("status")
        print(f"🎉 SUKCES! Post wysłany do publikacji na profil @dailycontent67!")
        print(f"ID Buffer: {post_id} | Status: {status}")

        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "post_id": post_id,
            "status": status,
            "channel": "@dailycontent67",
            "tweet_text": tweet_text,
            "format": tweet_data.get("format"),
            "source_title": tweet_data.get("source_title"),
            "source_link": tweet_data.get("source_link"),
            "image_url": image_url,
            "decision_process": tweet_data.get("decision_process")
        }
        save_to_history(history_entry)
        return history_entry
    else:
        err_msg = action_data.get("message") or str(res)
        print(f"❌ Błąd publikacji Buffer: {err_msg}")
        raise RuntimeError(f"Buffer API error: {err_msg}")
