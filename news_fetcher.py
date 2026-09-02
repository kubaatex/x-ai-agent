import urllib.request
import xml.etree.ElementTree as ET
import re
import json
import html

FEEDS = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
    }
]

def clean_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = re.sub(r"<[^>]+>", "", raw_html)
    return html.unescape(text).strip()

def extract_og_image(article_url: str) -> str:
    """Extracts the real preview/featured photo URL from the article webpage."""
    try:
        req = urllib.request.Request(
            article_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            m = re.search(r'<meta\s+(?:property|name)=["\']og:image["\']\s+content=["\']([^"\']+)["\']', content, re.IGNORECASE)
            if not m:
                m = re.search(r'<meta\s+content=["\']([^"\']+)["\']\s+(?:property|name)=["\']og:image["\']', content, re.IGNORECASE)
            if m:
                return m.group(1)
    except Exception:
        pass
    return ""

def fetch_latest_ai_news(limit: int = 15):
    articles = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for feed in FEEDS:
        try:
            req = urllib.request.Request(feed["url"], headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                
                # Check RSS 2.0 or Atom
                items = root.findall(".//item")
                if not items:
                    items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

                for item in items[:6]:
                    title_elem = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
                    link_elem = item.find("link") or item.find("{http://www.w3.org/2005/Atom}link")
                    desc_elem = item.find("description") or item.find("{http://www.w3.org/2005/Atom}summary")
                    
                    title = clean_text(title_elem.text if title_elem is not None else "")
                    
                    if link_elem is not None:
                        link = link_elem.attrib.get("href") if "href" in link_elem.attrib else link_elem.text
                    else:
                        link = ""

                    desc = clean_text(desc_elem.text if desc_elem is not None else "")

                    # Check image in enclosure
                    image_url = ""
                    enclosure = item.find("enclosure")
                    if enclosure is not None and "image" in enclosure.attrib.get("type", ""):
                        image_url = enclosure.attrib.get("url", "")

                    if title and link:
                        articles.append({
                            "source": feed["name"],
                            "title": title,
                            "link": link,
                            "summary": desc[:300],
                            "image_url": image_url
                        })
        except Exception as e:
            print(f"Warning: Failed to fetch {feed['name']}: {e}")

    return articles[:limit]

if __name__ == "__main__":
    news = fetch_latest_ai_news(5)
    print(f"Pobrano {len(news)} artykułów:")
    for n in news[:2]:
        if not n["image_url"]:
            n["image_url"] = extract_og_image(n["link"])
        print(json.dumps(n, indent=2, ensure_ascii=False))
