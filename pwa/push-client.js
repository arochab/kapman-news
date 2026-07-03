// CIRCUIT FERMÉ · Client Web Push partagé
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
  const SW_READY_TIMEOUT_MS = 10000;
  const UNSUB_ARM_MS = 4000;

  const PERMISSION_BLOCKED_GUIDE =
    '1. Icône 🔒 dans la barre d’adresse → Notifications → Autoriser. ' +
    '2. Toujours rien ? Réglages Android → Applications → Chrome → Notifications.';

  // Warm-up fire-and-forget : Render (free tier) s'endort après inactivité.
  // On tape /health dès le chargement de la page pour amortir le cold start
  // avant même que la lectrice ait touché le bouton d'abonnement.
  fetch(RENDER + '/health').catch(() => {});

  // État courant de l'abonnement (rempli au chargement via getSubscription()).
  let currentSub = null;
  let unsubArmed = false;
  let unsubTimer = null;

  // Libellé d'origine du bouton (dépend de la page : accueil vs issue) —
  // on le capture une fois pour pouvoir y revenir après désabonnement /
  // expiration de l'armement de désabonnement.
  const subBtnEl = document.getElementById('sub-btn');
  const INITIAL_LABEL = subBtnEl ? subBtnEl.textContent : '↓ S’abonner';

  // Affiche un état lisible sous le bouton. Plus jamais d'échec silencieux.
  function setStatus(msg, kind) {
    const el = document.getElementById('sub-status');
    if (!el) return;
    el.textContent = msg;
    el.dataset.kind = kind || 'info'; // info | ok | err
  }

  // Contrôle complet du bouton : libellé, état "actif" (classe .on),
  // et disponibilité (disabled). Remplace l'ancien setBtn qui ne savait
  // qu'ajouter la classe .on, jamais la retirer.
  function setBtn(label, opts) {
    const btn = document.getElementById('sub-btn');
    if (!btn) return;
    const o = opts || {};
    btn.textContent = label;
    btn.classList.toggle('on', !!o.on);
    btn.disabled = !!o.disabled;
  }

  function resetBtnToInitial() {
    setBtn(INITIAL_LABEL, { on: false, disabled: false });
  }

  function setBtnBlocked() {
    setBtn('Notifications bloquées', { on: false, disabled: true });
    setStatus(PERMISSION_BLOCKED_GUIDE, 'err');
  }

  function setBtnSubscribed() {
    setBtn('✓ Abonné', { on: true, disabled: false });
  }

  function clearUnsubArm() {
    if (unsubTimer) {
      clearTimeout(unsubTimer);
      unsubTimer = null;
    }
    unsubArmed = false;
  }

  function urlBase64ToUint8Array(b64) {
    const pad = '='.repeat((4 - (b64.length % 4)) % 4);
    const base = (b64 + pad).replace(/-/g, '+').replace(/_/g, '/');
    const raw = atob(base);
    return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
  }

  // navigator.serviceWorker.ready peut rester en attente indéfiniment sur
  // certains Android/Chrome dégradés (SW jamais activé). On borne l'attente
  // à ~10s pour toujours retomber sur un message d'erreur exploitable
  // plutôt qu'un bouton figé sans feedback.
  function swReadyWithTimeout() {
    const timeout = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('le service worker met trop de temps à démarrer')), SW_READY_TIMEOUT_MS);
    });
    return Promise.race([navigator.serviceWorker.ready, timeout]);
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

  // Détermine l'état réel du bouton au chargement : bloqué (permission
  // refusée), déjà abonné, ou état initial (rien à faire, le markup a déjà
  // le bon libellé).
  async function initButtonState(reg) {
    if (!document.getElementById('sub-btn')) return;

    if ('Notification' in window && Notification.permission === 'denied') {
      setBtnBlocked();
      return;
    }

    if (!reg) return;

    try {
      const sub = await reg.pushManager.getSubscription();
      if (sub) {
        currentSub = sub;
        setBtnSubscribed();
        setStatus('Tu es bien abonné · tu recevras les prochaines issues.', 'ok');
      }
    } catch (err) {
      console.warn('[KAPMAN] getSubscription au chargement a échoué:', err);
    }
  }

  // Désabonnement effectif : sub.unsubscribe() côté navigateur + purge côté
  // serveur (le payload attendu par /unsubscribe est { endpoint }).
  async function performUnsubscribe() {
    if (!currentSub) return;
    setStatus('Désabonnement…', 'info');
    const endpoint = currentSub.endpoint;
    try {
      await currentSub.unsubscribe();
    } catch (err) {
      console.warn('[KAPMAN] unsubscribe() navigateur a échoué:', err);
      // on continue quand même : on veut au moins purger le serveur.
    }
    try {
      await fetch(RENDER + '/unsubscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint }),
      });
    } catch (err) {
      console.warn('[KAPMAN] POST /unsubscribe a échoué:', err);
    }
    currentSub = null;
    resetBtnToInitial();
    setStatus('Désabonnement confirmé. Tu peux te réabonner quand tu veux.', 'ok');
  }

  // Flux d'abonnement / désabonnement, appelé par le bouton. Le même
  // bouton sert aux deux : s'il est déjà abonné, un premier tap arme le
  // désabonnement ("Se désabonner ?" pendant 4s), un second tap dans ce
  // délai le confirme.
  async function subscribePush() {
    if (!('Notification' in window) || !('serviceWorker' in navigator) || !('PushManager' in window)) {
      setStatus('Ton navigateur ne supporte pas les notifications push. Utilise Chrome sur Android.', 'err');
      return;
    }

    // Permission bloquée : on ne relance JAMAIS requestPermission() dans ce
    // cas (Chrome ne le redemande plus, ça ne ferait qu'échouer en silence).
    if (Notification.permission === 'denied') {
      setBtnBlocked();
      return;
    }

    // Déjà abonné → ce tap concerne le désabonnement, pas un nouvel abonnement.
    if (currentSub) {
      if (!unsubArmed) {
        unsubArmed = true;
        setBtn('Se désabonner ?', { on: true });
        setStatus('Retape pour confirmer le désabonnement (4s).', 'info');
        unsubTimer = setTimeout(() => {
          clearUnsubArm();
          setBtnSubscribed();
          setStatus('Tu es bien abonné · tu recevras les prochaines issues.', 'ok');
        }, UNSUB_ARM_MS);
        return;
      }
      clearUnsubArm();
      try {
        await performUnsubscribe();
      } catch (e) {
        console.error('[KAPMAN] unsubscribe failed:', e);
        setStatus('Erreur désabonnement : ' + e.message, 'err');
      }
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
    if (perm === 'denied') {
      setBtnBlocked();
      return;
    }
    if (perm !== 'granted') {
      setStatus('Permission refusée. Active les notifications dans les réglages du site puis réessaie.', 'err');
      return;
    }

    let reg;
    try {
      reg = await swReadyWithTimeout(); // attend l'activation, borné à ~10s
    } catch (e) {
      setStatus('Service worker pas prêt : ' + e.message, 'err');
      return;
    }

    try {
      const existing = await reg.pushManager.getSubscription();
      if (existing) {
        currentSub = existing;
        setBtnSubscribed();
        setStatus('Tu es bien abonné · tu recevras les prochaines issues.', 'ok');
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

      currentSub = sub;
      setBtnSubscribed();
      setStatus('C’est bon. Notification à chaque nouvelle issue.', 'ok');
    } catch (e) {
      console.error('[KAPMAN] subscribe failed:', e);
      setStatus('Erreur : ' + e.message + '. Réessaie dans un instant (le serveur se réveille peut-être).', 'err');
    }
  }

  // Partage natif — bouton optionnel, absent sur les pages en cache tant
  // qu'elles n'ont pas été régénérées : garde null systématique.
  function initShareButton() {
    const btn = document.querySelector('#share-btn');
    if (!btn) return;
    if (!('share' in navigator)) return;
    btn.hidden = false;
    btn.addEventListener('click', () => {
      navigator.share({
        title: 'CIRCUIT FERMÉ',
        text: 'La newsletter underground electronic, sélection sous chiffrement client',
        url: ROOT,
      }).catch((err) => {
        // AbortError si la lectrice annule le partage : rien à signaler.
        if (err && err.name !== 'AbortError') console.warn('[KAPMAN] share failed:', err);
      });
    });
  }

  // Expose le handler au onclick du bouton et auto-register au load.
  window.subscribePush = subscribePush;
  initShareButton();
  registerSW().then(initButtonState);
})();
