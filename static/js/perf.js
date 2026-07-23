/**
 * Site performance tiers — early, shared by all page scripts.
 *
 * Tiers:
 *   reduce   — prefers-reduced-motion
 *   lite     — weakest / mobile / laggy (IO fades only)
 *   balanced — DEFAULT for most machines (light fades, no Lenis/scrub/filter)
 *   full     — high-end desktop only, or ?motion=full
 *
 * Overrides: ?motion=full | ?motion=balanced | ?motion=lite
 * Runtime: FPS probe can downgrade full/balanced → lite if frames drop.
 */
(function (global) {
  "use strict";

  var html = document.documentElement;
  var reduce =
    typeof matchMedia === "function" &&
    matchMedia("(prefers-reduced-motion: reduce)").matches;

  var coarse =
    typeof matchMedia === "function" && matchMedia("(pointer: coarse)").matches;
  var narrow =
    typeof matchMedia === "function" && matchMedia("(max-width: 900px)").matches;
  var fine =
    typeof matchMedia === "function" && matchMedia("(pointer: fine)").matches;

  function conn() {
    return navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  }

  function detectTier() {
    if (reduce) return "reduce";

    try {
      var q = new URLSearchParams(location.search).get("motion");
      if (q === "full" || q === "balanced" || q === "lite") return q;
    } catch (_e) {
      /* ignore */
    }

    var cores = navigator.hardwareConcurrency || 4;
    var memory = typeof navigator.deviceMemory === "number" ? navigator.deviceMemory : null;
    var c = conn();
    var saveData = !!(c && c.saveData);
    var slowNet =
      c &&
      (c.effectiveType === "slow-2g" ||
        c.effectiveType === "2g" ||
        c.effectiveType === "3g");

    /* Weak / constrained → lite */
    if (saveData || slowNet) return "lite";
    if (cores <= 4) return "lite";
    if (memory !== null && memory <= 4) return "lite";
    if (coarse) return "lite";
    if (narrow) return "lite";

    /*
     * Full cinematic only when clearly strong.
     * Missing deviceMemory (Firefox) → never assume full.
     */
    var strong =
      fine &&
      !coarse &&
      cores >= 8 &&
      memory !== null &&
      memory >= 8 &&
      !saveData;

    if (strong) return "full";

    /* Mid desktop without proven headroom → still lite (smooth first) */
    if (fine && cores >= 6 && memory !== null && memory >= 8) return "balanced";

    return "lite";
  }

  var tier = detectTier();

  function applyTier(next) {
    tier = next;
    html.classList.remove(
      "is-reduce-motion",
      "is-lite-motion",
      "is-balanced-motion",
      "is-full-motion"
    );
    if (next === "reduce") html.classList.add("is-reduce-motion", "is-lite-motion");
    else if (next === "lite") html.classList.add("is-lite-motion");
    else if (next === "balanced") html.classList.add("is-balanced-motion", "is-lite-motion");
    else html.classList.add("is-full-motion");
  }

  applyTier(tier);

  var isFull = function () {
    return tier === "full";
  };
  var isLiteLike = function () {
    return tier === "lite" || tier === "balanced" || tier === "reduce";
  };

  var api = {
    tier: tier,
    reduce: reduce || tier === "reduce",
    lite: isLiteLike(),
    full: isFull(),
    allowSmoothScroll: false, /* Lenis off by default — major RAF tax */
    allowParallax: false,
    allowFilterFx: false,
    allowScrub: false,
    allowInfiniteCss: false,
    allowMagnetic: false,
    allowGsapScroll: false,
    allowHeroDraw: false,
  };

  function syncFlags() {
    api.tier = tier;
    api.reduce = reduce || tier === "reduce";
    api.lite = isLiteLike();
    api.full = isFull();
    /* Heavy features only on explicit full tier */
    api.allowSmoothScroll = isFull();
    api.allowParallax = isFull();
    api.allowFilterFx = isFull();
    api.allowScrub = isFull();
    api.allowInfiniteCss = isFull();
    api.allowMagnetic = isFull();
    api.allowGsapScroll = isFull();
    api.allowHeroDraw = isFull();
  }

  syncFlags();
  global.__sitePerf = api;

  /* Pause decorative loops when tab hidden */
  document.addEventListener("visibilitychange", function () {
    html.classList.toggle("is-tab-hidden", document.hidden);
  });

  /*
   * Runtime FPS probe — if the machine can't hold ~40fps for 1.2s,
   * force lite so remaining work stays light.
   */
  if (tier === "full" || tier === "balanced") {
    var frames = 0;
    var start = 0;
    var probeId = 0;

    function probe(now) {
      if (!start) start = now;
      frames += 1;
      var elapsed = now - start;
      if (elapsed < 1200) {
        probeId = requestAnimationFrame(probe);
        return;
      }
      var fps = (frames / elapsed) * 1000;
      if (fps < 40 && tier !== "lite" && tier !== "reduce") {
        applyTier("lite");
        syncFlags();
        try {
          html.dispatchEvent(new CustomEvent("siteperf:downgrade", { detail: { fps: fps } }));
        } catch (_e2) {
          /* ignore */
        }
      }
    }

    if (typeof requestAnimationFrame === "function") {
      probeId = requestAnimationFrame(probe);
    }
  }
})(typeof window !== "undefined" ? window : this);
