import os, json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from pywebpush import webpush, WebPushException

app = Flask(__name__)
CORS(app, origins=["https://arochab.github.io", "http://localhost:*"])

VAPID_PRIVATE_KEY = os.environ["VAPID_PRIVATE_KEY"]
VAPID_PUBLIC_KEY  = os.environ["VAPID_PUBLIC_KEY"]
VAPID_CLAIMS      = {"sub": "mailto:adam.chabbi94@gmail.com"}
PUSH_SECRET       = os.environ.get("PUSH_SECRET", "")

# Persistance durable via GitHub Gist (gratuit). Si non configuré, fallback /tmp.
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GIST_ID      = os.environ.get("GIST_ID", "")
GIST_FILE    = "subscriptions.json"
TMP_FILE     = "/tmp/subscriptions.json"

# Cache mémoire : évite de taper l'API Gist à chaque requête + résilience.
_cache = {"subs": None}


# ─────────────────────────── Persistance ───────────────────────────

def _gist_enabled():
    return bool(GITHUB_TOKEN and GIST_ID)


def _gist_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def _load_from_gist():
    r = requests.get(f"https://api.github.com/gists/{GIST_ID}",
                     headers=_gist_headers(), timeout=10)
    r.raise_for_status()
    content = r.json()["files"][GIST_FILE]["content"]
    return json.loads(content) if content.strip() else []


def _save_to_gist(subs):
    payload = {"files": {GIST_FILE: {"content": json.dumps(subs, indent=2)}}}
    r = requests.patch(f"https://api.github.com/gists/{GIST_ID}",
                       headers=_gist_headers(), json=payload, timeout=10)
    r.raise_for_status()


def _load_from_tmp():
    try:
        with open(TMP_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _save_to_tmp(subs):
    try:
        with open(TMP_FILE, "w") as f:
            json.dump(subs, f)
    except Exception:
        pass


def load_subs():
    if _cache["subs"] is not None:
        return _cache["subs"]
    subs = []
    if _gist_enabled():
        try:
            subs = _load_from_gist()
        except Exception as e:
            app.logger.warning(f"Gist load failed, fallback /tmp: {e}")
            subs = _load_from_tmp()
    else:
        subs = _load_from_tmp()
    _cache["subs"] = subs
    return subs


def save_subs(subs):
    _cache["subs"] = subs
    if _gist_enabled():
        try:
            _save_to_gist(subs)
            return
        except Exception as e:
            app.logger.warning(f"Gist save failed, fallback /tmp: {e}")
    _save_to_tmp(subs)


# ─────────────────────────── Routes ───────────────────────────

@app.route("/")
def health():
    return jsonify({
        "status": "ok",
        "subscribers": len(load_subs()),
        "persistence": "gist" if _gist_enabled() else "tmp",
    })


@app.route("/vapid-public-key")
def vapid_key():
    return jsonify({"publicKey": VAPID_PUBLIC_KEY})


@app.route("/subscribe", methods=["POST"])
def subscribe():
    sub = request.get_json()
    if not sub or "endpoint" not in sub:
        return jsonify({"error": "invalid subscription"}), 400
    subs = load_subs()
    if sub["endpoint"] not in [s["endpoint"] for s in subs]:
        subs.append(sub)
        save_subs(subs)
    return jsonify({"ok": True, "total": len(subs)}), 201


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.get_json()
    endpoint = data.get("endpoint") if data else None
    if not endpoint:
        return jsonify({"error": "missing endpoint"}), 400
    subs = [s for s in load_subs() if s["endpoint"] != endpoint]
    save_subs(subs)
    return jsonify({"ok": True})


@app.route("/notify", methods=["POST"])
def notify():
    if request.headers.get("X-Push-Secret") != PUSH_SECRET:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json()
    message = json.dumps({
        "title": payload.get("title", "KAPMAN SIGNAL"),
        "body":  payload.get("body", "Nouvelle issue disponible"),
        "url":   payload.get("url", "/"),
        "issue": payload.get("issue", ""),
    })

    subs = load_subs()
    sent, failed, dead = 0, 0, []

    for sub in subs:
        try:
            webpush(
                subscription_info=sub,
                data=message,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=dict(VAPID_CLAIMS),  # copie : pywebpush mute le dict
            )
            sent += 1
        except WebPushException as ex:
            status = ex.response.status_code if ex.response else 0
            if status in (404, 410):
                dead.append(sub["endpoint"])
            else:
                failed += 1

    if dead:
        subs = [s for s in subs if s["endpoint"] not in dead]
        save_subs(subs)

    return jsonify({"sent": sent, "failed": failed, "cleaned": len(dead)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
