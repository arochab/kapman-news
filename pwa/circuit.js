// CIRCUIT FERMÉ · client du verrou membre (contenu chiffré embarqué,
// déverrouillé côté navigateur par un code, jamais transmis à un serveur).
// Chargé uniquement sur les issues qui portent un bloc `circuit` (voir
// templates/issue.html.j2). Zéro dépendance.

(function () {
  'use strict';

  // Racine du site (même calcul que pwa/push-client.js) : gardée pour la
  // cohérence entre scripts partagés, même si ce module ne construit
  // aujourd'hui aucune URL absolue.
  function siteRoot() {
    var parts = location.pathname.split('/').filter(Boolean);
    if (location.hostname.endsWith('github.io') && parts.length > 0) {
      return location.origin + '/' + parts[0] + '/';
    }
    return location.origin + '/';
  }
  var ROOT = siteRoot();

  var KEYRING_KEY = 'cf_circuit_keyring';

  function loadKeyring() {
    try {
      var raw = localStorage.getItem(KEYRING_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function saveKeyCode(kid, code) {
    try {
      var kr = loadKeyring();
      kr[kid] = code;
      localStorage.setItem(KEYRING_KEY, JSON.stringify(kr));
    } catch (e) {
      // Stockage indisponible (navigation privée, quota...) : le
      // déverrouillage de cette session reste valide, juste pas mémorisé.
    }
  }

  function b64ToBytes(b64) {
    var bin = atob(b64);
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return bytes;
  }

  // Dérivation de clé compatible avec l'outil Python (cf docs/) :
  // PBKDF2-HMAC-SHA256(code strip + minuscule, salt, 310000 itérations, 256 bits).
  function deriveKey(code, saltB64) {
    var enc = new TextEncoder();
    var codeNorm = String(code || '').trim().toLowerCase();
    return crypto.subtle
      .importKey('raw', enc.encode(codeNorm), { name: 'PBKDF2' }, false, ['deriveKey'])
      .then(function (keyMaterial) {
        return crypto.subtle.deriveKey(
          { name: 'PBKDF2', salt: b64ToBytes(saltB64), iterations: 310000, hash: 'SHA-256' },
          keyMaterial,
          { name: 'AES-GCM', length: 256 },
          false,
          ['decrypt']
        );
      });
  }

  // AES-256-GCM : iv 12 octets, tag inclus en fin de ct (comportement natif
  // WebCrypto). Un mauvais code fait échouer decrypt() (tag invalide) :
  // c'est notre seul signal d'erreur, pas de vérification à part.
  function decryptBlob(blob, code) {
    return deriveKey(code, blob.salt).then(function (key) {
      var iv = b64ToBytes(blob.iv);
      var ct = b64ToBytes(blob.ct);
      return crypto.subtle.decrypt({ name: 'AES-GCM', iv: iv }, key, ct);
    }).then(function (plainBuf) {
      var text = new TextDecoder().decode(plainBuf);
      return JSON.parse(text);
    });
  }

  // Insère les nœuds top-level de `html` juste après `refEl` (afterend).
  // Retourne la liste ordonnée des nœuds insérés (le dernier sert d'ancre
  // pour chaîner un autre fragment ciblant la même position).
  function insertAfter(refEl, html) {
    var tpl = document.createElement('template');
    tpl.innerHTML = html;
    var nodes = Array.prototype.slice.call(tpl.content.childNodes);
    var anchor = refEl;
    var inserted = [];
    nodes.forEach(function (node) {
      anchor.parentNode.insertBefore(node, anchor.nextSibling);
      inserted.push(node);
      anchor = node;
    });
    return inserted;
  }

  // Le contenu injecté doit être visible immédiatement (il arrive après le
  // scan initial de l'IntersectionObserver de la page). Filet de sécurité :
  // si un fragment porte malgré tout la classe .reveal, on la révèle direct.
  function revealAll(nodes) {
    nodes.forEach(function (node) {
      if (node.nodeType !== 1) return;
      if (node.classList && node.classList.contains('reveal')) node.classList.add('in');
      if (node.querySelectorAll) {
        Array.prototype.forEach.call(node.querySelectorAll('.reveal'), function (el) {
          el.classList.add('in');
        });
      }
    });
  }

  // Méta discographique d'une piste, même format que la macro meta() de
  // templates/_track.j2 (label catno · format · place · année). Purement
  // cosmétique : sert à compléter les lignes du registre au déverrouillage.
  function trackMeta(t) {
    if (t.label || t.catno || t.year) {
      var s = t.label || '';
      if (t.catno) s += (s ? ' ' : '') + t.catno;
      if (t.format) s += ' · ' + t.format;
      if (t.place) s += ' · ' + t.place;
      if (t.year) s += ' · ' + t.year;
      return s;
    }
    return t.meta || '';
  }

  // Complète les lignes caviardées du registre avec le nom et la méta réels
  // (depuis le clair déchiffré), AVANT la cascade : le retrait de chaque
  // barre révèle alors le nom à sa place (transition pilotée par --i dans le
  // CSS du template). L'ordre DOM des .line-locked suit l'idx global
  // croissant, identique à l'ordre des pistes membres du clair (blocs triés
  // par position, pistes dans l'ordre : cf compute_pieces, tools/circuit.py).
  function fillRegistreLines(data) {
    try {
      var rows = document.querySelectorAll('#circuit-lock .line-locked');
      if (!rows.length || !data || !data.source || !Array.isArray(data.source.blocks)) return;
      var blocks = data.source.blocks.slice().sort(function (a, b) {
        return (a.position || 0) - (b.position || 0);
      });
      var tracks = [];
      blocks.forEach(function (b) {
        (b.tracks || []).forEach(function (t) { tracks.push(t); });
      });
      for (var i = 0; i < rows.length && i < tracks.length; i++) {
        var t = tracks[i];
        if (!t || !t.name) continue;
        var bar = rows[i].querySelector('.redact-bar');
        if (!bar || rows[i].querySelector('.line-name--reveal')) continue;
        var nameEl = document.createElement('div');
        nameEl.className = 'line-name line-name--reveal';
        nameEl.textContent = t.name;
        bar.parentNode.insertBefore(nameEl, bar);
        var metaEl = rows[i].querySelector('.line-meta');
        var meta = trackMeta(t);
        if (metaEl && meta) metaEl.textContent = meta;
      }
    } catch (e) {
      // Cosmétique uniquement : ne bloque jamais le déverrouillage.
    }
  }

  // Insère chaque fragment après le bon [data-flow], triés par position puis
  // par ordre d'origine (tri stable) pour un rendu déterministe même en cas
  // de collision de position.
  function applyFragments(data) {
    if (!data || !Array.isArray(data.fragments)) return;
    var entries = data.fragments.map(function (f, i) {
      return { f: f, i: i };
    });
    entries.sort(function (a, b) {
      if (a.f.position !== b.f.position) return a.f.position - b.f.position;
      return a.i - b.i;
    });
    var tails = {};
    entries.forEach(function (entry) {
      var frag = entry.f;
      var pos = frag.position;
      var anchor = tails[pos] || document.querySelector('[data-flow="' + pos + '"]');
      if (!anchor || !frag.html) return;
      var inserted = insertAfter(anchor, frag.html);
      if (inserted.length) tails[pos] = inserted[inserted.length - 1];
      revealAll(inserted);
    });
  }

  function init() {
    var blobEl = document.getElementById('circuit-blob');
    if (!blobEl) return; // pas de blob sur cette page : no-op

    var blob;
    try {
      blob = JSON.parse(blobEl.textContent);
    } catch (e) {
      return;
    }
    if (!blob || !blob.kid || !('crypto' in window) || !crypto.subtle) return;

    var lockEl = document.getElementById('circuit-lock');
    var errorEl = document.querySelector('#circuit-lock .circuit-error');
    var form = document.getElementById('circuit-form');
    var input = document.getElementById('circuit-code');
    var unlocked = false;

    function showError() {
      if (errorEl) errorEl.classList.add('show');
    }
    function hideError() {
      if (errorEl) errorEl.classList.remove('show');
    }

    // Idempotent : un second appel une fois ouvert ne réinjecte rien.
    function attemptUnlock(code, silent) {
      if (unlocked) return Promise.resolve(true);
      return decryptBlob(blob, code)
        .then(function (data) {
          // v5 « Index de sélection » : .registre-open déclenche la cascade
          // CSS de retrait des barres de caviardage (ligne à ligne, voir
          // templates/issue.html.j2 .registre-open .line-locked .redact-bar)
          // AVANT l'injection des fragments, pour que le retrait des barres
          // et l'apparition du contenu membre restent deux temps distincts.
          // Les noms réels sont posés dans les lignes juste avant : chaque
          // barre qui s'essuie révèle le nom à sa place.
          fillRegistreLines(data);
          if (lockEl) lockEl.classList.add('registre-open');
          applyFragments(data);
          unlocked = true;
          if (lockEl) lockEl.classList.add('is-open');
          saveKeyCode(blob.kid, code);
          hideError();
          return true;
        })
        .catch(function () {
          if (!silent) showError();
          return false;
        });
    }

    if (form) {
      form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        var code = input ? input.value : '';
        if (!code) return;
        attemptUnlock(code, false);
      });
    }

    // Lien magique : #c=<code> dans l'URL. Le hash ne part jamais au
    // serveur, c'est tout l'intérêt. Priorité sur le keyring au chargement :
    // s'il y a un hash, on ne regarde même pas le keyring. Succès -> le
    // code est nettoyé de l'URL (replaceState) pour ne rester ni dans la
    // barre d'adresse ni dans un copier-coller ultérieur. Échec -> même
    // traitement qu'un mauvais code tapé à la main (le formulaire reste).
    var hashCode = getHashCode();
    if (hashCode) {
      attemptUnlock(hashCode, false).then(function (ok) {
        if (ok) cleanHash();
      });
      return;
    }

    // Sinon, auto-unlock silencieux si un code pour ce kid est déjà en mémoire.
    var keyring = loadKeyring();
    var savedCode = keyring[blob.kid];
    if (savedCode) attemptUnlock(savedCode, true);
  }

  // Extrait le code d'un lien magique #c=<code> (URL-decodé). null si absent.
  function getHashCode() {
    var h = location.hash || '';
    if (h.charAt(0) === '#') h = h.slice(1);
    var m = /(?:^|&)c=([^&]*)/.exec(h);
    if (!m || !m[1]) return null;
    try {
      return decodeURIComponent(m[1]);
    } catch (e) {
      return null;
    }
  }

  // Retire le hash de l'URL sans recharger la page ni laisser d'entrée
  // d'historique (replaceState, pas pushState).
  function cleanHash() {
    try {
      history.replaceState(null, '', location.pathname + location.search);
    } catch (e) {}
  }

  try {
    init();
  } catch (e) {
    console.warn('[CIRCUIT] init a échoué:', e);
  }
})();
