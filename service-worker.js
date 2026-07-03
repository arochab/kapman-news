// CIRCUIT FERMÉ — Service Worker
// Servi depuis la racine du repo pour que son scope couvre tout /kapman-news/.
// Tous les chemins sont résolus relativement à self.registration.scope
// (ex. https://arochab.github.io/kapman-news/) — jamais d'absolu "/" qui
// pointerait vers la racine du domaine (hors site sur GitHub Pages).

// Bump à chaque changement de DA/template — force le remplacement du cache.
const CACHE = 'cf-v8';

// URL du serveur Render — même valeur que pwa/push-client.js (RENDER).
const RENDER = 'https://kapman-news.onrender.com';

// URL absolue résolue depuis le scope du SW
const fromScope = (path) => new URL(path, self.registration.scope).toString();

// Install — cache les pages clés (chemins relatifs au scope)
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll([
        fromScope('./'),
      ]))
      .catch((err) => console.warn('[SW] cache warm-up partiel:', err)) // ne bloque pas l'install
  );
  self.skipWaiting();
});

// Activate — purge les vieux caches
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch — network first, fallback cache, puis réponse offline explicite
// (jamais `undefined` : un respondWith(undefined) casse la requête au lieu
// d'afficher un message lisible).
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const clone = res.clone();
        caches.open(CACHE).then((cache) => cache.put(e.request, clone));
        return res;
      })
      .catch(() =>
        caches.match(e.request).then(
          (cached) =>
            cached ||
            new Response('Hors ligne. Revenez quand vous aurez du réseau.', {
              status: 503,
              headers: { 'Content-Type': 'text/plain; charset=utf-8' },
            })
        )
      )
  );
});

// Push reçue — défensif : affiche TOUJOURS une notif, même si le payload
// est illisible (déchiffrement raté). On ne perd jamais une notif silencieusement.
self.addEventListener('push', (e) => {
  let data = {};
  try {
    if (e.data) data = e.data.json();
  } catch (err) {
    // payload non-JSON ou non déchiffrable : on garde les valeurs par défaut
    data = {};
  }

  const title = data.title || 'CIRCUIT FERMÉ';
  const targetUrl = data.url
    ? fromScope(String(data.url).replace(/^\//, ''))
    : fromScope('./');

  const options = {
    body: data.body || 'Nouvelle issue disponible',
    icon: fromScope('pwa/icon-192.png'),
    badge: fromScope('pwa/badge-72.png'),
    data: { url: targetUrl },
    actions: [{ action: 'open', title: 'Lire' }],
    vibrate: [100, 50, 100],
    tag: 'kapman-issue',
    renotify: true,
    requireInteraction: false,
  };
  e.waitUntil(self.registration.showNotification(title, options));
});

// Tap sur la notif → ouvre/refocus la page cible
self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  if (e.action === 'dismiss') return;
  const url = e.notification.data && e.notification.data.url
    ? e.notification.data.url
    : fromScope('./');
  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((wins) => {
      const existing = wins.find((w) => w.url === url);
      if (existing) return existing.focus();
      return clients.openWindow(url);
    })
  );
});

// Le navigateur peut invalider un abonnement push (rotation interne côté
// pusher) et déclenche cet event pour qu'on s'y resouscrive nous-mêmes.
// Sans ce handler, l'abonné arrête silencieusement de recevoir des push.
function urlBase64ToUint8Array(b64) {
  const pad = '='.repeat((4 - (b64.length % 4)) % 4);
  const base = (b64 + pad).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base);
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
}

self.addEventListener('pushsubscriptionchange', (e) => {
  const oldKey =
    e.oldSubscription && e.oldSubscription.options
      ? e.oldSubscription.options.applicationServerKey
      : null;

  // Fallback : l'ancienne clé n'est pas toujours exposée par le navigateur.
  // On va la rechercher auprès du serveur (même source que push-client.js) —
  // pas de clé publique en dur ici : elle est gérée côté Render et peut
  // tourner, donc mieux vaut la relire que risquer une valeur obsolète.
  const keyPromise = oldKey
    ? Promise.resolve(oldKey)
    : fetch(RENDER + '/vapid-public-key')
        .then((r) => r.json())
        .then((j) => urlBase64ToUint8Array(j.publicKey));

  e.waitUntil(
    keyPromise
      .then((applicationServerKey) =>
        self.registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey,
        })
      )
      .then((sub) =>
        fetch(RENDER + '/subscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(sub),
        })
      )
      .catch((err) => console.warn('[SW] pushsubscriptionchange re-subscribe échoué:', err))
  );
});
