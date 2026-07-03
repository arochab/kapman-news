// Disque vinyle 3D pour le hero de la home. Rendu procedural (aucune texture
// image) : sillons par shader, matiere glossy via specular a deux lobes.
// Depend uniquement de pwa/vendor/three.module.min.js.

import * as THREE from './vendor/three.module.min.js';

const RPM = 2;
const ANGULAR_SPEED = (RPM * Math.PI * 2) / 60; // rad/s
const TILT_X = THREE.MathUtils.degToRad(28);
const TILT_Z = THREE.MathUtils.degToRad(-6);
const PARALLAX_MAX = THREE.MathUtils.degToRad(3);
const POINTER_EASE = 0.045;

const DISC_RADIUS = 1;
const DISC_THICKNESS = 0.055;
const LABEL_RADIUS = 0.3;
const RING_WIDTH = 0.02;
const RADIAL_SEGMENTS = 220; // ~880 triangles au total, tres sous le budget 12k

const VERTEX_SHADER = `
varying vec3 vLocalPos;
varying vec3 vLocalNormal;
varying vec3 vWorldPos;

void main() {
  vLocalPos = position;
  vLocalNormal = normal;
  vec4 worldPos = modelMatrix * vec4(position, 1.0);
  vWorldPos = worldPos.xyz;
  gl_Position = projectionMatrix * viewMatrix * worldPos;
}
`;

const FRAGMENT_SHADER = `
precision highp float;

varying vec3 vLocalPos;
varying vec3 vLocalNormal;
varying vec3 vWorldPos;

uniform mat4 uModelMatrix;
uniform vec3 uCameraPos;
uniform vec3 uKeyDir;
uniform vec3 uKeyColor;
uniform vec3 uRimDir;
uniform vec3 uRimColor;
uniform float uLabelRadius;
uniform float uRingOuter;
uniform float uGrooveFreq;
uniform float uGrooveAmp;
uniform float uSpiralTwist;

void main() {
  float r = length(vLocalPos.xz);
  float isCap = step(0.5, abs(vLocalNormal.y));

  vec2 rd = r > 0.0001 ? vLocalPos.xz / r : vec2(1.0, 0.0);
  vec3 radialDir = vec3(rd.x, 0.0, rd.y);
  float theta = atan(vLocalPos.z, vLocalPos.x);

  // Bump procedural des sillons : bandes concentriques modulant la normale.
  // Un leger vrillage en spirale (comme le sillon reel d'un disque) casse la
  // symetrie de rotation : sans lui, des anneaux parfaitement concentriques
  // rendraient un rendu identique a chaque instant de la rotation.
  float phase = r * uGrooveFreq + theta * uSpiralTwist;
  float dPhase = fwidth(phase);
  float aaFade = clamp(1.15 - dPhase / 2.2, 0.0, 1.0);
  float grooveZone = smoothstep(uRingOuter, uRingOuter + 0.012, r) * isCap;
  float slope = cos(phase) * uGrooveFreq * uGrooveAmp;
  float perturb = slope * aaFade * grooveZone;

  vec3 bumpedNormal = normalize(vLocalNormal + radialDir * perturb);
  vec3 N = normalize(mat3(uModelMatrix) * bumpedNormal);
  vec3 V = normalize(uCameraPos - vWorldPos);
  vec3 L = normalize(uKeyDir);
  vec3 H = normalize(L + V);

  // Zones : label graphite mat, anneau laiton, champ de sillons noir glossy.
  float labelMask = 1.0 - smoothstep(uLabelRadius - 0.006, uLabelRadius, r);
  float ringMask = smoothstep(uLabelRadius, uLabelRadius + 0.004, r)
    * (1.0 - smoothstep(uRingOuter - 0.004, uRingOuter, r));
  float discMask = clamp(1.0 - labelMask - ringMask, 0.0, 1.0);

  vec3 graphite = vec3(0.078, 0.078, 0.09);
  vec3 laiton = vec3(0.761, 0.639, 0.42);
  vec3 vinylBlack = vec3(0.016, 0.016, 0.02);

  vec3 baseColor = isCap > 0.5
    ? graphite * labelMask + laiton * ringMask + vinylBlack * discMask
    : vinylBlack;

  // Roughness modulee par bandes lentes, pour rompre l'uniformite du noir.
  float bandPhase = r * uGrooveFreq * 0.05;
  float bandVar = 0.5 + 0.5 * sin(bandPhase);
  float discShininess = mix(30.0, 70.0, bandVar);
  float discSpecStrength = mix(1.4, 2.0, bandVar);

  float shininess = mix(discShininess, 48.0, labelMask + ringMask);
  float specStrength = mix(discSpecStrength, 0.9, labelMask * 0.85 + ringMask * 0.3);
  float diffuseStrength = mix(0.3, 0.65, labelMask + ringMask * 0.7);

  float NdotL = max(dot(N, L), 0.0);
  float NdotH = max(dot(N, H), 0.0);
  vec3 ambient = vec3(0.09, 0.093, 0.108);
  vec3 diffuse = uKeyColor * NdotL * diffuseStrength * 1.4;
  // Lobe large (matiere) + lobe etroit et vif (le glint qui balaie les sillons).
  float glintExponent = mix(110.0, 220.0, discMask) * mix(1.0, 0.35, labelMask + ringMask);
  vec3 specular = uKeyColor * specStrength * 0.8 * pow(NdotH, shininess)
    + uKeyColor * discMask * 3.4 * pow(NdotH, glintExponent);

  float fresnel = pow(1.0 - max(dot(N, V), 0.0), 3.0);
  float rimDot = max(dot(N, normalize(uRimDir)), 0.0);
  vec3 rim = uRimColor * (fresnel * 0.5 + pow(rimDot, 4.0) * 0.5) * 0.4;

  vec3 color = baseColor * (ambient + diffuse) + specular + rim;
  color = color / (color + vec3(1.0));

  gl_FragColor = vec4(color, 1.0);
}
`;

function supportsWebGL() {
  try {
    const probe = document.createElement('canvas');
    return Boolean(probe.getContext('webgl2') || probe.getContext('webgl'));
  } catch (err) {
    return false;
  }
}

function buildScene() {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 10);
  camera.position.set(0, 0.12, 3.25);
  camera.lookAt(0, -0.02, 0);

  const rig = new THREE.Group();
  rig.position.y = 0.08;
  rig.rotation.x = TILT_X;
  rig.rotation.z = TILT_Z;
  scene.add(rig);

  const spinner = new THREE.Group();
  rig.add(spinner);

  const geometry = new THREE.CylinderGeometry(
    DISC_RADIUS,
    DISC_RADIUS,
    DISC_THICKNESS,
    RADIAL_SEGMENTS,
    1,
    false
  );

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uModelMatrix: { value: new THREE.Matrix4() },
      uCameraPos: { value: new THREE.Vector3() },
      uKeyDir: { value: new THREE.Vector3(0.48, 0.8, 0.82).normalize() },
      uKeyColor: { value: new THREE.Color(1.15, 0.95, 0.68) },
      uRimDir: { value: new THREE.Vector3(-0.6, 0.25, -0.75).normalize() },
      uRimColor: { value: new THREE.Color(0.55, 0.68, 0.92) },
      uLabelRadius: { value: LABEL_RADIUS },
      uRingOuter: { value: LABEL_RADIUS + RING_WIDTH },
      uGrooveFreq: { value: 210.0 },
      uGrooveAmp: { value: 0.0024 },
      uSpiralTwist: { value: 9.0 },
    },
    vertexShader: VERTEX_SHADER,
    fragmentShader: FRAGMENT_SHADER,
    extensions: { derivatives: true },
  });

  const mesh = new THREE.Mesh(geometry, material);
  spinner.add(mesh);
  material.uniforms.uModelMatrix.value = mesh.matrixWorld;

  return { scene, camera, rig, spinner, geometry, material };
}

/**
 * Monte le disque vinyle 3D dans `container`. Retourne { destroy() } en cas
 * de succes, ou false si le rendu n'est pas monte (mouvement reduit demande,
 * ou WebGL indisponible) : le fallback CSS de la home reste alors visible.
 * N'emet jamais d'erreur console.
 */
export function mountDisque(container) {
  try {
    return mountDisqueInner(container);
  } catch (err) {
    return false;
  }
}

function mountDisqueInner(container) {
  if (!container) return false;

  const reducedMotion = Boolean(
    window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
  if (reducedMotion) return false;
  if (!supportsWebGL()) return false;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: 'low-power',
    });
  } catch (err) {
    return false;
  }
  if (!renderer) return false;

  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  const canvas = renderer.domElement;
  canvas.style.display = 'block';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.pointerEvents = 'none';
  container.appendChild(canvas);

  const { scene, camera, rig, spinner, geometry, material } = buildScene();

  let rafId = null;
  let lastTime = performance.now();
  let visible = false;
  let pageVisible = !document.hidden;

  const pointerTarget = { x: 0, y: 0 };
  const pointerCurrent = { x: 0, y: 0 };

  function onPointerMove(event) {
    const nx = (event.clientX / window.innerWidth) * 2 - 1;
    const ny = (event.clientY / window.innerHeight) * 2 - 1;
    pointerTarget.x = nx;
    pointerTarget.y = ny;
  }
  window.addEventListener('pointermove', onPointerMove, { passive: true });

  function resize() {
    const w = Math.max(container.clientWidth, 1);
    const h = Math.max(container.clientHeight, 1);
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }

  let resizeObserver = null;
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);
  } else {
    window.addEventListener('resize', resize);
  }
  resize();

  function updateRunning() {
    const shouldRun = visible && pageVisible;
    if (shouldRun && rafId === null) {
      lastTime = performance.now();
      rafId = requestAnimationFrame(frame);
    } else if (!shouldRun && rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
  }

  let io = null;
  if (typeof IntersectionObserver !== 'undefined') {
    io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          visible = entry.isIntersecting;
        }
        updateRunning();
      },
      { threshold: 0.01 }
    );
    io.observe(container);
  } else {
    visible = true;
    updateRunning();
  }

  function onVisibilityChange() {
    pageVisible = !document.hidden;
    updateRunning();
  }
  document.addEventListener('visibilitychange', onVisibilityChange);

  function frame(now) {
    rafId = requestAnimationFrame(frame);
    const dt = Math.min((now - lastTime) / 1000, 0.1);
    lastTime = now;

    spinner.rotation.y += ANGULAR_SPEED * dt;

    pointerCurrent.x += (pointerTarget.x - pointerCurrent.x) * POINTER_EASE;
    pointerCurrent.y += (pointerTarget.y - pointerCurrent.y) * POINTER_EASE;
    rig.rotation.x = TILT_X + pointerCurrent.y * PARALLAX_MAX;
    rig.rotation.y = pointerCurrent.x * PARALLAX_MAX;

    material.uniforms.uCameraPos.value.copy(camera.position);

    try {
      renderer.render(scene, camera);
    } catch (err) {
      if (rafId !== null) {
        cancelAnimationFrame(rafId);
        rafId = null;
      }
    }
  }

  function destroy() {
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    if (io) io.disconnect();
    if (resizeObserver) resizeObserver.disconnect();
    else window.removeEventListener('resize', resize);
    document.removeEventListener('visibilitychange', onVisibilityChange);
    window.removeEventListener('pointermove', onPointerMove);
    geometry.dispose();
    material.dispose();
    renderer.dispose();
    if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
  }

  return { destroy };
}
