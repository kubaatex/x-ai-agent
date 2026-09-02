# 🤖 Viral AI Twitter/X Agent (@dailycontent67)

Autonomiczny agent AI odpowiedzialny za wyszukiwanie najświeższych newsów ze świata sztucznej inteligencji (z ostatnich 24–48 godzin), przekładanie ich na viralowe posty według psychologicznych ram i automatyczne publikowanie na Twoim profilu X z dołączeniem prawdziwych zdjęć z artykułów.

---

## 🚀 Szybki Start

W folderze masz przygotowane skróty:

1. **`start_scheduler.bat`** – Uruchamia agenta w trybie ciągłym (**10 postów dziennie** o zróżnicowanych, naturalnych godzinach między 8:00 a 22:00).
2. **`post_now.bat`** – Od razu wyszukuje najświeższy news i publikuje 1 post na X.

Możesz też używać terminala:
```bash
# Test generowania posta bez publikowania (podgląd 6 pytań decyzyjnych)
python agent.py --test

# Publikacja pojedynczego posta po angielsku (domyślnie)
python agent.py --post-now --lang EN

# Publikacja pojedynczego posta po polsku
python agent.py --post-now --lang PL

# Ciągły harmonogram (10 postów na dobę)
python agent.py --schedule
```

---

## 🧠 Zaimplementowana Strategia i Dyrektywy

Agent realizuje pełen proces tworzenia treści:

### 1. Filtr 6 Pytań Decyzyjnych:
Przed stworzeniem każdego wpisu model odpowiada na pytania:
1. *Jaką trudność rozwiązujesz?*
2. *Kogo dotyczy ten problem?*
3. *Jakie są korzyści z jego rozwiązania?*
4. *Co obiecujesz czytelnikowi?*
5. *Jakie emocje chcesz wywołać?*
6. *Jaką akcję ma podjąć czytelnik?*

Zasada przewodnia: **"Sprzedawaj ludziom to, czego chcą, ale dawaj im to, czego potrzebują."**

### 2. Sprawdzone Formaty Viralowych Hooków:
* **Przed/Po:** "Przed: [stare]. Po: [nowe]. Różnica: [wynik]."
* **Hot Takes:** "Niepopularna opinia: ..." lub "Zatrzymaj [X]. Zacznij [Y]."
* **Contrarian:** "Większość uważa [X]. Mylą się. Oto dlaczego:"
* **Dane i statystyki:** "Przeanalizowałem [fakt/liczbę]. Oto co to oznacza:"
* **Frameworks:** "[Liczba] rzeczy, które musisz wiedzieć..."
* **Angażowanie:** Prowokujące, otwarte pytania do społeczności.

### 3. Prawdziwe zdjęcia i linki źródłowe:
Agent automatycznie parsuje metadane `og:image` z oryginalnych artykułów i przesyła oryginalną fotografię bezpośrednio na serwery Twittera.

---

## ⚙️ Konfiguracja (`.env`)

Plik `.env` zawiera:
* `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` – Twoje klucze konta X.
* `GEMINI_API_KEY` – Klucz Gemini API.
* `POST_LANGUAGE=EN` – Domyślny język publikacji (`EN` dla globalnego zasięgu lub `PL`).
