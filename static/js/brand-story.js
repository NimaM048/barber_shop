/**
 * Brand Story — quiet reveal + portrait load
 */
(() => {
  "use strict";

  const root = document.querySelector("[data-brand-story]");
  if (!root) return;

  const perf = window.__sitePerf || {
    reduce: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  };
  const reduceMotion = !!perf.reduce;

  const portraitImg = root.querySelector("[data-bs-portrait-img]");
  if (portraitImg) {
    const markLoaded = () => root.classList.add("is-portrait-loaded");
    if (portraitImg.complete && portraitImg.naturalWidth) markLoaded();
    else portraitImg.addEventListener("load", markLoaded, { once: true });
  }

  const nodes = [...root.querySelectorAll("[data-bs-reveal]")];
  if (!nodes.length) return;

  if (reduceMotion) {
    nodes.forEach((el) => el.classList.add("is-visible"));
    return;
  }

  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      });
    },
    { threshold: 0.05, rootMargin: "0px 0px 12% 0px" }
  );

  nodes.forEach((el, index) => {
    el.style.transitionDelay = `${Math.min(index * 0.06, 0.3)}s`;
    io.observe(el);
  });

  /* Ensure already-visible nodes never stay faded */
  requestAnimationFrame(() => {
    nodes.forEach((el) => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight * 0.95 && rect.bottom > 0) {
        el.classList.add("is-visible");
        io.unobserve(el);
      }
    });
  });
})();
