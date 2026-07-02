# Config gunicorn — chargée automatiquement (fichier ./gunicorn.conf.py).
# Le timeout worker par défaut est 30s : trop court pour un cold start Render
# + chargement du Gist + envoi séquentiel des webpush. Sans ça, Render tue le
# worker en plein /notify même si le client attend plus longtemps.
timeout = 120
