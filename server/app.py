import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from pywebpush import webpush, WebPushException

app = Flask(__name__)
CORS(app, origins=["https://arochab.github.io", "http://localhost:*"])

VAPID_PRIVATE_KEY = os.environ["VAPID_PRIVATE_KEY"]
VAPID_PUBLIC_KEY  = os.environ["VAPID_PUBLIC_KEY"]
VAPID_CLAIMS      = {"sub": "mailto:adam.chabbi94@gmail.com"}
PUSH_SECRET       = os.environ.get("PUSH_SECRET", "")  # pour sécuriser /notify

SUBS_FILE = "/tmp/subscriptions.json"


def load_subs():
    try:
        with open(SUBS_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def save_subs(subs):
    with open(SUBS_FILE, "w") as f:
        json.dump(subs, f)


@app.route("/")
def health():
    subs = load_subs()
    return jsonify({"status": "ok", "subscribers": len(subs)})


@app.route("/vapid-public-key")
def vapid_key():
    return jsonify({"publicKey": VAPID_PUBLIC_KEY})


@app.route("/subscribe", methods=["POST"])
def subscribe():
    sub = request.get_json()
    if not sub or "endpoint" not in sub:
        return jsonify({"error": "invalid subscription"}), 400
    subs = load_subs()
    endpoints = [s["endpoint"] for s in subs]
    if sub["endpoint"] not in endpoints:
        subs.append(sub)
        save_subs(subs)
    return jsonify({"ok": True, "total": len(subs)}), 201


@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    data = request.get_json()
    endpoint = data.get("endpoint") if data else None
    if not endpoint:
        return jsonify({"error": "missing endpoint"}), 400
    subs = load_subs()
    subs = [s for s in subs if s["endpoint"] != endpoint]
    save_subs(subs)
    return jsonify({"ok": True})


@app.route("/notify", methods=["POST"])
def notify():
    # Sécurisé par secret header
    if request.headers.get("X-Push-Secret") != PUSH_SECRET:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json()
    title   = payload.get("title", "KAPMAN SIGNAL")
    body    = payload.get("body", "Nouvelle issue disponible")
    url     = payload.get("url", "/")
    issue   = payload.get("issue", "")

    message = json.dumps({
        "title": title,
        "body": body,
        "url": url,
        "issue": issue
    })

    subs = load_subs()
    sent, failed, dead = 0, 0, []

    for sub in subs:
        try:
            webpush(
                subscription_info=sub,
                data=message,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
            sent += 1
        except WebPushException as ex:
            status = ex.response.status_code if ex.response else 0
            if status in (404, 410):
                dead.append(sub["endpoint"])
            else:
                failed += 1

    # Nettoie les subs mortes
    if dead:
        subs = [s for s in subs if s["endpoint"] not in dead]
        save_subs(subs)

    return jsonify({"sent": sent, "failed": failed, "cleaned": len(dead)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
