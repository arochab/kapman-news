// KAPMAN SIGNAL — Client Web Push partagé
// Inclus par index.html (racine) ET issues/NN/index.html (sous-dossier).
// Calcule la racine du site dynamiquement pour enregistrer le SW au bon scope.

(function () {
  'use strict';

  // Racine du site GitHub Pages : on isole le 1er segment de path (/kapman-news/).
  // En local (file:// ou localhost à la racine) ça retombe sur "/".
  function siteRoot() {
    const parts = location.pathname.split('/').filter(Boolean);
    // Sur github.io le 1er segment est le nom du repo ; sinon racine.
    if (location.hostname.endsWith('github.io') && parts.length > 0) {
      return location.origin + '/' + parts[0] + '/';
    }
    return location.origin + '/';
  }

  const ROOT = siteRoot();
  const RENDER = 'https://kapman-news.onrender.com';

  // Affiche un état lisible sous le bouton. Plus jamais d'échec silencieux.
  function setStatus(msg, kind) {
    const el = document.getElementById('sub-status');
    if (!el) return;
    el.textContent = msg;
    el.dataset.kind = kind || 'info'; // info | ok | err
  }

  function setBtn(label, on) {
    const btn = document.getElementById('sub-btn');
    if (!btn) return;
    btn.textContent = label;
    if (on) btn.classList.add('on');
  }

  function urlBase64ToUint8Array(b64) {
    const pad = '='.repeat((4 - (b64.length % 4)) % 4);
    const base = (b64 + pad).replace(/-/g, '+').replace(/_/g, '/');
    const raw = atob(base);
    return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
  }

  // Enregistre le SW à la RACINE du site (scope large) dès le chargement.
  async function registerSW() {
    if (!('serviceWorker' in navigator)) return null;
    try {
      const reg = await navigator.serviceWorker.register(ROOT + 'service-worker.js', {
        scope: ROOT,
      });
      console.log('[KAPMAN] SW registered, scope =', reg.scope);
      return reg;
    } catch (err) {
      console.error('[KAPMAN] SW register failed:', err);
      setStatus('Service worker indisponible : ' + err.message, 'err');
      return null;
    }
  }

  // Flux d'abonnement, appelé par le bouton.
  async function subscribePush() {
    if (!('Notification' in window) || !('serviceWorker' in navigator) || !('PushManager' in window)) {
      setStatus('Ton navigateur ne supporte pas les notifications push. Utilise Chrome sur Android.', 'err');
      return;
    }

    setStatus('Demande de permission…', 'info');
    let perm;
    try {
      perm = await Notification.requestPermission();
    } catch (e) {
      setStatus('Erreur permission : ' + e.message, 'err');
      return;
    }
    if (perm !== 'granted') {
      setStatus('Permission refusée. Active les notifications dans les réglages du site puis réessaie.', 'err');
      return;
    }

    let reg;
    try {
      reg = await navigator.serviceWorker.ready; // attend l'activation
    } catch (e) {
      setStatus('Service worker pas prêt : ' + e.message, 'err');
      return;
    }

    try {
      const existing = await reg.pushManager.getSubscription();
      if (existing) {
        setBtn('✓ Déjà abonné', true);
        setStatus('Tu es bien abonné — tu recevras les prochaines issues.', 'ok');
        return;
      }

      setStatus('Récupération de la clé…', 'info');
      const keyRes = await fetch(RENDER + '/vapid-public-key');
      if (!keyRes.ok) throw new Error('serveur clé HTTP ' + keyRes.status);
      const { publicKey } = await keyRes.json();

      setStatus('Abonnement…', 'info');
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey),
      });

      const saveRes = await fetch(RENDER + '/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sub),
      });
      if (!saveRes.ok) throw new Error('enregistrement HTTP ' + saveRes.status);

      setBtn('✓ Abonné', true);
      setStatus('C’est bon. Notification à chaque nouvelle issue.', 'ok');
    } catch (e) {
      console.error('[KAPMAN] subscribe failed:', e);
      setStatus('Erreur : ' + e.message + '. Réessaie dans un instant (le serveur se réveille peut-être).', 'err');
    }
  }

  // Expose le handler au onclick du bouton et auto-register au load.
  window.subscribePush = subscribePush;
  registerSW();
})();
