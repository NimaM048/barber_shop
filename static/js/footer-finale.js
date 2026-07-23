/**
 * Footer Finale — cinematic closing chapter
 * Full tier: GSAP reveal. Balanced/lite: IntersectionObserver fades.
 */
(() => {
  "use strict";

  const root = document.querySelector("[data-footer-finale]");
  if (!root) return;

  const perf = window.__sitePerf || {
    reduce: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    lite: true,
    full: false,
    allowFilterFx: false,
    allowScrub: false,
    allowGsapScroll: false,
  };
  const reduceMotion = !!perf.reduce;
  const useCinema = !!perf.full && !!perf.allowGsapScroll;
  const hasGsap =
    useCinema &&
    typeof gsap !== "undefined" &&
    typeof ScrollTrigger !== "undefined";

  const qa = (sel) => [...root.querySelectorAll(sel)];
  const bgWord = root.querySelector("[data-ff-bg-word]");
  const glow = root.querySelector("[data-ff-glow]");
  const reveals = qa("[data-ff-reveal]");

  const showAll = () => {
    root.classList.add("is-static", "is-revealed");
    reveals.forEach((el) => el.classList.add("is-inview"));
  };

  /* ── Balanced / lite / reduced: cheap IO reveals ── */
  if (reduceMotion || !hasGsap) {
    root.classList.add("is-static");

    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-inview");
            io.unobserve(entry.target);
          });
        },
        { threshold: 0.08, rootMargin: "0px 0px -4% 0px" }
      );
      reveals.forEach((el) => io.observe(el));

      if (bgWord) {
        const bgIo = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (!entry.isIntersecting) return;
              bgWord.classList.add("is-inview");
              bgIo.unobserve(bgWord);
            });
          },
          { threshold: 0.05 }
        );
        bgIo.observe(root);
      }
      if (glow) glow.style.opacity = "1";
    } else {
      showAll();
    }
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  const useBlur = !!perf.allowFilterFx;
  gsap.set(reveals, {
    opacity: 0,
    y: 28,
    ...(useBlur ? { filter: "blur(6px)" } : {}),
  });
  if (bgWord) gsap.set(bgWord, { opacity: 0, scale: 1.04, y: 40 });
  if (glow) gsap.set(glow, { opacity: 0, scale: 0.92 });

  const tl = gsap.timeline({
    defaults: {
      ease: "power3.out",
      duration: 1.35,
    },
    scrollTrigger: {
      trigger: root,
      start: "top 82%",
      once: true,
    },
  });

  if (glow) {
    tl.to(glow, { opacity: 1, scale: 1, duration: 2.2, ease: "power2.out" }, 0);
  }

  if (bgWord) {
    tl.to(
      bgWord,
      {
        opacity: 0.035,
        scale: 1,
        y: 0,
        duration: 2.4,
        ease: "power2.out",
      },
      0.15
    );
  }

  reveals.forEach((el) => {
    const delay = Number(el.getAttribute("data-ff-delay") || 0) * 0.14;
    const to = {
      opacity: 1,
      y: 0,
      duration: 1.25,
    };
    if (useBlur) {
      to.filter = "blur(0px)";
      to.clearProps = "filter";
    }
    tl.to(el, to, 0.35 + delay);
  });

  if (perf.allowScrub && bgWord) {
    gsap.to(bgWord, {
      yPercent: -8,
      ease: "none",
      scrollTrigger: {
        trigger: root,
        start: "top bottom",
        end: "bottom top",
        scrub: 1.4,
      },
    });
  }

  if (perf.allowScrub && glow) {
    gsap.to(glow, {
      yPercent: -6,
      ease: "none",
      scrollTrigger: {
        trigger: root,
        start: "top bottom",
        end: "bottom top",
        scrub: 1.8,
      },
    });
  }
})();
