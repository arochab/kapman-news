// KAPMAN SIGNAL — Service Worker
// Servi depuis la racine du repo pour que son scope couvre tout /kapman-news/.
// Tous les chemins sont résolus relativement à self.registration.scope
// (ex. https://arochab.github.io/kapman-news/) — jamais d'absolu "/" qui
// pointerait vers la racine du domaine (hors site sur GitHub Pages).

const CACHE = 'kapman-v2';

// URL absolue résolue depuis le scope du SW
const fromScope = (path) => new URL(path, self.registration.scope).toString();

// Install — cache les pages clés (chemins relatifs au scope)
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll([
        fromScope('./'),
        fromScope('issues/09/'),
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

// Fetch — network first, fallback cache (sans page offline dédiée)
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const clone = res.clone();
        caches.open(CACHE).then((cache) => cache.put(e.request, clone));
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});

// Push reçue
self.addEventListener('push', (e) => {
  const data = e.data ? e.data.json() : {};
  const title = data.title || 'KAPMAN SIGNAL';
  const targetUrl = data.url
    ? fromScope(data.url.replace(/^\//, ''))   // tolère "/issues/09/" ou "issues/09/"
    : fromScope('./');

  const options = {
    body: data.body || 'Nouvelle issue disponible',
    icon: fromScope('pwa/icon-192.png'),
    badge: fromScope('pwa/badge-72.png'),
    data: { url: targetUrl },
    actions: [
      { action: 'open', title: 'Lire' },
      { action: 'dismiss', title: 'Plus tard' },
    ],
    vibrate: [100, 50, 100],
    tag: 'kapman-issue',
    renotify: true,
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
