/**
 * Brand Story — editorial scroll storytelling
 * Slow, expensive motion. Respects prefers-reduced-motion + lite-motion.
 */
(() => {
  "use strict";

  const root = document.querySelector("[data-brand-story]");
  if (!root) return;

  const perf = window.__sitePerf || {
    reduce: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    lite: true,
    full: false,
    allowScrub: false,
    allowGsapScroll: false,
  };
  const reduceMotion = !!perf.reduce;
  const liteMotion = !!perf.lite;
  const hasGsap =
    !!perf.full &&
    !!perf.allowGsapScroll &&
    typeof gsap !== "undefined" &&
    typeof ScrollTrigger !== "undefined";

  const q = (sel) => root.querySelector(sel);
  const qa = (sel) => [...root.querySelectorAll(sel)];

  const portrait = q("[data-bs-portrait]");
  const portraitMedia = q("[data-bs-portrait-media]");
  const portraitImg = q("[data-bs-portrait-img]");
  const progress = q("[data-bs-timeline-progress]");
  const steps = qa("[data-bs-step]");
  const bgWords = qa("[data-bs-bg-word]");

  let activeEffect = "none";
  let activeIndex = -1;

  const setEffect = (effect) => {
    const next = effect || "none";
    if (next === activeEffect || !portrait) return;
    /* Portrait CSS filters are costly while scrolling on weak GPUs */
    if (liteMotion) {
      activeEffect = "none";
      portrait.setAttribute("data-effect", "none");
      return;
    }
    activeEffect = next;
    portrait.setAttribute("data-effect", next);
  };

  const activateStep = (index, { fromUser = false } = {}) => {
    if (index === activeIndex && !fromUser) return;
    activeIndex = index;

    steps.forEach((step, i) => {
      const on = i === index;
      const trigger = step.querySelector("[data-bs-step-trigger]");
      const desc = step.querySelector(".bs-step-desc");

      step.classList.toggle("is-active", on);
      step.classList.toggle("is-passed", i < index);

      if (trigger) trigger.setAttribute("aria-expanded", on ? "true" : "false");
      if (desc) {
        if (on) desc.removeAttribute("hidden");
        else desc.setAttribute("hidden", "");
      }
      if (on) setEffect(step.getAttribute("data-effect") || "none");
    });

    /* Progress is scroll-owned via ScrollTrigger; only nudge on explicit user intent */
    if (fromUser && progress && steps.length && !progress.hasAttribute("data-bs-scrubbing")) {
      const ratio = steps.length <= 1 ? 1 : index / (steps.length - 1);
      progress.style.transform = `scaleY(${Math.max(0.1, ratio)})`;
    }
  };

  steps.forEach((step, index) => {
    const trigger = step.querySelector("[data-bs-step-trigger]") || step;

    const engage = () => activateStep(index, { fromUser: true });

    trigger.addEventListener("mouseenter", engage);
    trigger.addEventListener("focus", engage);
    trigger.addEventListener("click", engage);
  });

  if (portraitImg) {
    const markLoaded = () => root.classList.add("is-portrait-loaded");
    if (portraitImg.complete && portraitImg.naturalWidth) markLoaded();
    else portraitImg.addEventListener("load", markLoaded, { once: true });
  }

  /* ── Reduced motion / no GSAP ── */
  if (reduceMotion || !hasGsap) {
    root.classList.add("is-static");
    activateStep(0);

    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-inview");
            io.unobserve(entry.target);
          });
        },
        { threshold: 0.12, rootMargin: "0px 0px -6% 0px" }
      );
      qa("[data-bs-reveal], [data-bs-step], [data-bs-value], [data-bs-portrait]").forEach(
        (el) => io.observe(el)
      );

      const stepIo = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const idx = Number(entry.target.getAttribute("data-index") || 0);
            activateStep(idx);
          });
        },
        { threshold: 0.55, rootMargin: "-18% 0px -28% 0px" }
      );
      steps.forEach((step) => stepIo.observe(step));
    } else {
      qa("[data-bs-reveal], [data-bs-step], [data-bs-value], [data-bs-portrait]").forEach(
        (el) => el.classList.add("is-inview")
      );
    }
    return;
  }

  gsap.registerPlugin(ScrollTrigger);

  const allowScrub = perf.allowScrub !== false;
  const durScale = liteMotion ? 0.72 : 1;

  /* Use opacity (not autoAlpha) so content stays in a11y tree */
  const reveals = qa("[data-bs-reveal]");
  gsap.set(reveals, { opacity: 0, y: liteMotion ? 16 : 28 });

  const mask = q("[data-bs-portrait-mask]");
  if (portraitMedia) {
    gsap.set(portraitMedia, {
      scale: allowScrub ? 1.08 : 1,
      yPercent: allowScrub ? 4 : 0,
    });
  }
  if (mask) {
    gsap.set(mask, {
      clipPath: allowScrub ? "inset(10% 14% 14% 10%)" : "inset(0% 0% 0% 0%)",
    });
  }
  if (portrait) gsap.set(portrait, { opacity: allowScrub ? 0.4 : 0 });
  gsap.set(steps, { opacity: 0, y: liteMotion ? 14 : 22 });
  if (progress) {
    gsap.set(progress, { scaleY: 0, transformOrigin: "top center" });
    if (allowScrub) progress.setAttribute("data-bs-scrubbing", "");
  }
  if (bgWords.length) gsap.set(bgWords, { opacity: 0 });

  const easeLux = "power2.out";

  /* Philosophy */
  const philosophy = q('[data-bs-act="philosophy"]');
  if (philosophy) {
    const phItems = philosophy.querySelectorAll("[data-bs-reveal]");
    gsap.to(phItems, {
      opacity: 1,
      y: 0,
      duration: 1.45 * durScale,
      stagger: 0.12 * durScale,
      ease: easeLux,
      scrollTrigger: {
        trigger: philosophy,
        start: "top 80%",
        once: true,
      },
    });
  }

  /* Background words — fade only, gentle drift */
  if (bgWords.length) {
    gsap.to(bgWords, {
      opacity: 1,
      duration: (liteMotion ? 1.4 : 2.4) * durScale,
      stagger: liteMotion ? 0.15 : 0.3,
      ease: "power1.out",
      scrollTrigger: {
        trigger: root,
        start: "top 75%",
        once: true,
      },
    });

    if (allowScrub) {
      bgWords.forEach((word, i) => {
        gsap.to(word, {
          yPercent: i % 2 === 0 ? -5 : 6,
          ease: "none",
          scrollTrigger: {
            trigger: root,
            start: "top bottom",
            end: "bottom top",
            scrub: 1.6,
          },
        });
      });
    }
  }

  /* Portrait reveal */
  const composition = q('[data-bs-act="composition"]');
  if (composition && portrait) {
    if (allowScrub) {
      gsap
        .timeline({
          scrollTrigger: {
            trigger: composition,
            start: "top 78%",
            end: "top 32%",
            scrub: 1.25,
          },
        })
        .to(portrait, { opacity: 1, ease: "none" }, 0)
        .to(mask, { clipPath: "inset(0% 0% 0% 0%)", ease: "none" }, 0)
        .to(portraitMedia, { scale: 1, yPercent: 0, ease: "none" }, 0);

      if (portraitMedia) {
        gsap.fromTo(
          portraitMedia,
          { yPercent: 0 },
          {
            yPercent: -4,
            ease: "none",
            scrollTrigger: {
              trigger: composition,
              start: "top 32%",
              end: "bottom top",
              scrub: 1.6,
            },
          }
        );
      }
    } else {
      gsap.to(portrait, {
        opacity: 1,
        duration: 0.9,
        ease: easeLux,
        scrollTrigger: {
          trigger: composition,
          start: "top 78%",
          once: true,
        },
      });
    }

    const caption = portrait.querySelector(".bs-portrait-caption");
    if (caption) {
      gsap.to(caption, {
        opacity: 1,
        y: 0,
        duration: 1.2 * durScale,
        ease: easeLux,
        scrollTrigger: {
          trigger: portrait,
          start: "top 58%",
          once: true,
        },
      });
    }
  }

  /* Timeline */
  const timeline = q("[data-bs-timeline]");
  if (timeline && steps.length) {
    const label = timeline.querySelector(".bs-timeline-label");
    if (label) {
      gsap.to(label, {
        opacity: 1,
        y: 0,
        duration: 1.15 * durScale,
        ease: easeLux,
        scrollTrigger: {
          trigger: timeline,
          start: "top 82%",
          once: true,
        },
      });
    }

    gsap.to(steps, {
      opacity: 1,
      y: 0,
      duration: 1.15 * durScale,
      stagger: 0.1 * durScale,
      ease: easeLux,
      scrollTrigger: {
        trigger: timeline,
        start: "top 74%",
        once: true,
      },
    });

    if (progress) {
      if (allowScrub) {
        gsap.fromTo(
          progress,
          { scaleY: 0 },
          {
            scaleY: 1,
            ease: "none",
            scrollTrigger: {
              trigger: timeline,
              start: "top 58%",
              end: "bottom 38%",
              scrub: 0.7,
            },
          }
        );
      } else {
        gsap.to(progress, {
          scaleY: 1,
          duration: 0.8,
          ease: easeLux,
          scrollTrigger: {
            trigger: timeline,
            start: "top 58%",
            once: true,
          },
        });
      }
    }

    steps.forEach((step, index) => {
      ScrollTrigger.create({
        trigger: step,
        start: "top 60%",
        end: "bottom 40%",
        onEnter: () => activateStep(index),
        onEnterBack: () => activateStep(index),
      });
    });

    activateStep(0);
  }

  /* Values — no blur (feels gimmicky / costly) */
  const valuesAct = q('[data-bs-act="values"]');
  if (valuesAct) {
    const valueItems = valuesAct.querySelectorAll("[data-bs-reveal], [data-bs-value]");
    gsap.to(valueItems, {
      opacity: 1,
      y: 0,
      duration: 1.2 * durScale,
      stagger: 0.08 * durScale,
      ease: easeLux,
      scrollTrigger: {
        trigger: valuesAct,
        start: "top 80%",
        once: true,
      },
    });
  }

  /* Finale */
  const finale = q('[data-bs-act="finale"]');
  if (finale) {
    const finaleItems = finale.querySelectorAll("[data-bs-reveal]");
    gsap.to(finaleItems, {
      opacity: 1,
      y: 0,
      duration: 1.35 * durScale,
      stagger: 0.16 * durScale,
      ease: easeLux,
      scrollTrigger: {
        trigger: finale,
        start: "top 82%",
        once: true,
      },
    });
  }
})();
