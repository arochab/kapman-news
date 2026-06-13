"""
Envoie la notification push pour une nouvelle issue.
Usage : python tools/send_push.py --issue 09 --title "KAPMAN SIGNAL N°09" --body "Ce qu'on entend quand personne regarde"
Appelé par GitHub Actions à chaque push sur main.
"""
import argparse, os, sys
import requests
from dotenv import load_dotenv

load_dotenv()

RENDER_URL  = os.environ.get("RENDER_URL", "https://kapman-news.onrender.com")
PUSH_SECRET = os.environ.get("PUSH_SECRET", "")

def send(issue: str, title: str, body: str):
    url = f"{RENDER_URL}/notify"
    payload = {
        "title": title,
        "body": body,
        "url": f"/issues/{issue}/",
        "issue": issue,
    }
    headers = {"X-Push-Secret": PUSH_SECRET, "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    print(f"✓ Push envoyé — {data['sent']} abonnés, {data['failed']} échecs, {data['cleaned']} nettoyés")
    for e in data.get("errors", []):
        print(f"  ↳ échec status={e.get('status')} detail={e.get('detail','')!r}")
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue",  required=True, help="Numéro de l'issue ex: 09")
    parser.add_argument("--title",  required=True)
    parser.add_argument("--body",   required=True)
    args = parser.parse_args()
    send(args.issue, args.title, args.body)
