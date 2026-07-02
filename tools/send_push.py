"""
Envoie la notification push pour une nouvelle issue.
Usage : python tools/send_push.py --issue 09 --title "CIRCUIT FERMÉ N°09" --body "Ce qu'on entend quand personne regarde"
Appelé par GitHub Actions à chaque push sur main.
"""
import argparse, os, sys, time
import requests
from dotenv import load_dotenv

load_dotenv()

RENDER_URL  = os.environ.get("RENDER_URL", "https://kapman-news.onrender.com")
PUSH_SECRET = os.environ.get("PUSH_SECRET", "")

WARMUP_MAX_WAIT = 180          # secondes max pour réveiller le serveur (Render free tier cold start)
WARMUP_TIMEOUT  = 10           # timeout par tentative de warm-up
NOTIFY_TIMEOUT  = 120          # /notify charge le Gist + envoie les pushes, peut être lent au réveil
NOTIFY_BACKOFF  = [5, 15, 45]  # secondes entre tentatives POST /notify (backoff exponentiel)


def warmup(base_url: str = None, max_wait: int = WARMUP_MAX_WAIT):
    """
    Réveille le serveur Render (free tier, cold start ~20-30s) avant d'appeler
    /notify. Boucle sur GET /health (fallback GET / si /health n'existe pas)
    avec une pause croissante entre les tentatives, jusqu'à obtenir une
    réponse HTTP < 500 ou jusqu'à expiration de max_wait.
    Retourne True si le serveur a répondu, False si on a abandonné.
    """
    base_url = (base_url or RENDER_URL).rstrip("/")
    start = time.time()
    attempt = 0
    pause = 5
    while True:
        attempt += 1
        elapsed = time.time() - start
        woke = False
        for path in ("/health", "/"):
            url = f"{base_url}{path}"
            try:
                r = requests.get(url, timeout=WARMUP_TIMEOUT)
                print(f"  warm-up tentative {attempt} ({url}) → status={r.status_code} (elapsed={elapsed:.1f}s)")
                if r.status_code < 500:
                    woke = True
                    break
            except requests.RequestException as e:
                print(f"  warm-up tentative {attempt} ({url}) → erreur: {e} (elapsed={elapsed:.1f}s)")
        if woke:
            print(f"✓ Serveur réveillé après {elapsed:.1f}s ({attempt} tentative(s))")
            return True
        if time.time() - start >= max_wait:
            print(f"✗ Warm-up abandonné après {max_wait}s — le serveur n'a pas répondu")
            return False
        time.sleep(pause)
        pause += 5


def send(issue: str, title: str, body: str):
    warmup()

    url = f"{RENDER_URL}/notify"
    payload = {
        "title": title,
        "body": body,
        "url": f"/issues/{issue}/",
        "issue": issue,
    }
    headers = {"X-Push-Secret": PUSH_SECRET, "Content-Type": "application/json"}

    last_exc = None
    for attempt in range(1, len(NOTIFY_BACKOFF) + 1):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=NOTIFY_TIMEOUT)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            last_exc = e
            status = r.status_code
            retriable = status in (502, 503, 504)
            if retriable and attempt < len(NOTIFY_BACKOFF):
                wait = NOTIFY_BACKOFF[attempt - 1]
                print(f"  ✗ tentative {attempt}/{len(NOTIFY_BACKOFF)} échouée (status={status}) — nouvelle tentative dans {wait}s")
                time.sleep(wait)
                continue
            raise
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            if attempt < len(NOTIFY_BACKOFF):
                wait = NOTIFY_BACKOFF[attempt - 1]
                print(f"  ✗ tentative {attempt}/{len(NOTIFY_BACKOFF)} échouée ({e}) — nouvelle tentative dans {wait}s")
                time.sleep(wait)
                continue
            raise
        else:
            data = r.json()
            print(f"✓ Push envoyé — {data['sent']} abonnés, {data['failed']} échecs, {data['cleaned']} nettoyés")
            for e in data.get("errors", []):
                print(f"  ↳ échec status={e.get('status')} detail={e.get('detail','')!r}")
            return data

    raise last_exc

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue",  required=True, help="Numéro de l'issue ex: 09")
    parser.add_argument("--title",  required=True)
    parser.add_argument("--body",   required=True)
    args = parser.parse_args()
    send(args.issue, args.title, args.body)
