import os
import sys
from dotenv import load_dotenv
import tweepy

# Załaduj zmienne środowiskowe z .env w tym samym katalogu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

def get_twitter_client():
    api_key = os.getenv('X_API_KEY')
    api_secret = os.getenv('X_API_SECRET')
    access_token = os.getenv('X_ACCESS_TOKEN')
    access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')

    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError("Brakujące klucze API w pliku .env!")

    return tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

def post_tweet(text: str):
    client = get_twitter_client()
    try:
        response = client.create_tweet(text=text)
        tweet_id = response.data['id']
        url = f"https://x.com/dailycontent67/status/{tweet_id}"
        print(f"✅ SUKCES! Tweet opublikowany.")
        print(f"ID: {tweet_id}")
        print(f"Link: {url}")
        return response
    except tweepy.errors.Forbidden as e:
        print(f"❌ BŁĄD UPRAWNIEŃ (403 Forbidden): {e}")
        print("💡 Wskazówka: Jeśli widzisz ten błąd, w panelu developer.x.com w 'User authentication settings' musisz zmienić uprawnienia na 'Read and Write', a następnie wygenerować PONOWNIE 'Access Token' i 'Access Token Secret'.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ BŁĄD podczas publikacji: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tweet_text = " ".join(sys.argv[1:])
    else:
        tweet_text = "Test automatyzacji X z poziomu AI! 🚀 #AI #Tech"

    print(f"Publikowanie tweeta: \"{tweet_text}\"...")
    post_tweet(tweet_text)
