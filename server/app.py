import os, json, base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from pywebpush import webpush, WebPushException
from cryptography.hazmat.primitives.serialization import load_pem_private_key

app = Flask(__name__)
CORS(app, origins=["https://arochab.github.io", "http://localhost:*"])

VAPID_PUBLIC_KEY = os.environ["VAPID_PUBLIC_KEY"]
VAPID_CLAIMS     = {"sub": "mailto:adam.chabbi94@gmail.com"}
PUSH_SECRET      = os.environ.get("PUSH_SECRET", "")


def _vapid_private_key():
    """
    pywebpush (py_vapid.from_raw) attend la clé privée EC en base64url du
    scalaire BRUT (32 bytes), pas le PEM ni le DER PKCS8.
    On accepte un PEM (multi-lignes ou avec \\n échappés via env var) et on
    en extrait le scalaire brut une fois au démarrage.
    """
    raw = os.environ["VAPID_PRIVATE_KEY"].strip()
    if "\\n" in raw and "\n" not in raw:        # Render: \n littéraux
        raw = raw.replace("\\n", "\n")
    if "BEGIN" in raw:                           # PEM → scalaire brut base64url
        key = load_pem_private_key(raw.encode(), password=None)
        scalar = key.private_numbers().private_value.to_bytes(32, "big")
        return base64.urlsafe_b64encode(scalar).decode().rstrip("=")
    return raw                                   # déjà en base64url brut


VAPID_PRIVATE_KEY = _vapid_private_key()

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


@app.route("/health")
def health_light():
    """Cible de warm-up ultra-légère : ne touche ni au Gist ni à rien de coûteux."""
    return jsonify({"ok": True})


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
    errors = []  # détail des échecs (status + extrait) pour le diagnostic

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
            body = ""
            try:
                body = (ex.response.text or "")[:200] if ex.response else ""
            except Exception:
                pass
            # pywebpush range parfois le code dans le message au lieu de ex.response
            # (status=0) → on détecte 404/410 dans le texte pour bien purger l'abonné mort.
            msg = str(ex)[:300]
            gone = status in (404, 410) or "410 Gone" in msg or "404 Not Found" in msg \
                or "unsubscribed or expired" in msg
            app.logger.warning(f"webpush failed: status={status} gone={gone} msg={msg!r} endpoint={sub.get('endpoint','')[:60]}")
            errors.append({"status": status, "detail": body or msg})
            if gone:
                dead.append(sub["endpoint"])
            else:
                failed += 1
        except Exception as ex:  # erreur hors HTTP (ValueError clé, chiffrement…)
            msg = f"{type(ex).__name__}: {ex}"[:300]
            app.logger.warning(f"webpush crashed: {msg} endpoint={sub.get('endpoint','')[:60]}")
            errors.append({"status": -1, "detail": msg})
            failed += 1

    if dead:
        subs = [s for s in subs if s["endpoint"] not in dead]
        save_subs(subs)

    return jsonify({"sent": sent, "failed": failed, "cleaned": len(dead), "errors": errors})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
