const CACHE = 'kapman-v1';
const OFFLINE_URL = '/offline.html';

// Install — cache les assets essentiels
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache =>
      cache.addAll(['/', '/issues/09/', OFFLINE_URL])
    )
  );
  self.skipWaiting();
});

// Activate — nettoie les vieux caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch — network first, cache fallback
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const clone = res.clone();
        caches.open(CACHE).then(cache => cache.put(e.request, clone));
        return res;
      })
      .catch(() => caches.match(e.request).then(r => r || caches.match(OFFLINE_URL)))
  );
});

// Push notification reçue
self.addEventListener('push', e => {
  const data = e.data ? e.data.json() : {};
  const title = data.title || 'KAPMAN SIGNAL';
  const options = {
    body: data.body || 'Nouvelle issue disponible',
    icon: '/pwa/icon-192.png',
    badge: '/pwa/badge-72.png',
    data: { url: data.url || '/issues/' + (data.issue || '') },
    actions: [
      { action: 'open', title: 'Lire →' },
      { action: 'dismiss', title: 'Plus tard' }
    ],
    vibrate: [100, 50, 100],
    tag: 'kapman-issue',
    renotify: true
  };
  e.waitUntil(self.registration.showNotification(title, options));
});

// Tap sur la notification
self.addEventListener('notificationclick', e => {
  e.notification.close();
  if (e.action === 'dismiss') return;
  const url = e.notification.data?.url || '/';
  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(wins => {
      const existing = wins.find(w => w.url.includes(url));
      if (existing) return existing.focus();
      return clients.openWindow(url);
    })
  );
});
