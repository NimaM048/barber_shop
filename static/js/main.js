/**
 * Saleh Ayoubi — luxury front-end presence
 * Lenis + GSAP ScrollTrigger + Swiper
 */
(() => {
  "use strict";

  const perf = window.__sitePerf || {
    reduce: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    lite: true,
    full: false,
    allowSmoothScroll: false,
    allowParallax: false,
    allowFilterFx: false,
    allowScrub: false,
    allowMagnetic: false,
    allowGsapScroll: false,
    allowHeroDraw: false,
  };
  const reduceMotion = !!perf.reduce;
  const liteMotion = !!perf.lite;
  const fullMotion = !!perf.full;
  const tier = perf.tier || (fullMotion ? "full" : "lite");
  const useGsapHero = tier === "full" || tier === "balanced";

  const toPersianDigits = (str) =>
    String(str).replace(/\d/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[d]);

  /* ── Lenis smooth scroll (skipped on lite / reduced) ── */
  let lenis = null;
  if (perf.allowSmoothScroll && !reduceMotion && typeof Lenis !== "undefined") {
    lenis = new Lenis({
      duration: 1.15,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    });
    window.__lenis = lenis;

    if (typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined") {
      gsap.registerPlugin(ScrollTrigger);
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add((time) => {
        lenis.raf(time * 1000);
      });
      gsap.ticker.lagSmoothing(0);
    } else {
      function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
      }
      requestAnimationFrame(raf);
    }
  } else if (typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined") {
    gsap.registerPlugin(ScrollTrigger);
  }

  /* ── Site navigation progress + page transitions ── */
  const siteProgress = (() => {
    const root = document.querySelector("[data-site-progress]");
    const bar = document.querySelector("[data-site-progress-bar]");
    const shell = document.querySelector("[data-site-shell]");
    if (!root || !bar) return null;

    const STORAGE_KEY = "site-nav-progress";
    const TRANSITION_KEY = "site-page-transition";
    const LEAVE_MS = reduceMotion ? 0 : fullMotion ? 280 : 120;
    let value = 0;
    let trickleTimer = 0;
    let hiding = false;
    let navigating = false;

    const setProgress = (next, instant) => {
      value = Math.max(0, Math.min(1, next));
      if (instant) {
        const prev = bar.style.transition;
        bar.style.transition = "none";
        bar.style.transform = `scaleX(${value})`;
        void bar.offsetWidth;
        bar.style.transition = prev;
        return;
      }
      bar.style.transform = `scaleX(${value})`;
    };

    const stopTrickle = () => {
      if (trickleTimer) {
        window.clearTimeout(trickleTimer);
        trickleTimer = 0;
      }
    };

    const trickle = () => {
      stopTrickle();
      if (value >= 0.86 || hiding) return;
      const remaining = 0.86 - value;
      const step = Math.max(0.01, remaining * (0.07 + Math.random() * 0.1));
      setProgress(value + step);
      trickleTimer = window.setTimeout(trickle, 320 + Math.random() * 480);
    };

    const start = () => {
      hiding = false;
      root.classList.remove("is-done");
      root.classList.add("is-active");
      setProgress(0.06, true);
      requestAnimationFrame(() => setProgress(0.2));
      trickle();
    };

    const done = () => {
      if (!root.classList.contains("is-active") && value <= 0) return;
      stopTrickle();
      hiding = true;
      setProgress(1);
      window.setTimeout(() => {
        root.classList.add("is-done");
        root.classList.remove("is-active");
        window.setTimeout(() => {
          setProgress(0, true);
          root.classList.remove("is-done");
          hiding = false;
        }, 520);
      }, reduceMotion ? 40 : 260);
    };

    const markTransition = () => {
      try {
        sessionStorage.setItem(STORAGE_KEY, "1");
        sessionStorage.setItem(TRANSITION_KEY, "1");
      } catch {
        /* ignore */
      }
    };

    const beginLeave = () => {
      document.documentElement.classList.add("is-page-leaving");
      document.documentElement.classList.remove("is-page-ready", "is-page-entering");
    };

    const revealPage = () => {
      const html = document.documentElement;
      const wasEntering = html.classList.contains("is-page-entering");

      try {
        sessionStorage.removeItem(TRANSITION_KEY);
      } catch {
        /* ignore */
      }

      if (!wasEntering || reduceMotion) {
        html.classList.remove("is-page-entering", "is-page-leaving");
        html.classList.add("is-page-ready");
        return;
      }

      requestAnimationFrame(() => {
        html.classList.add("is-page-ready");
        html.classList.remove("is-page-entering");
      });
    };

    const isInternalNav = (anchor) => {
      if (!anchor || anchor.target === "_blank" || anchor.hasAttribute("download")) {
        return false;
      }
      const href = anchor.getAttribute("href");
      if (!href || href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) {
        return false;
      }
      let url;
      try {
        url = new URL(anchor.href, window.location.href);
      } catch {
        return false;
      }
      if (url.origin !== window.location.origin) return false;
      if (
        url.pathname === window.location.pathname &&
        url.search === window.location.search &&
        url.hash
      ) {
        return false;
      }
      if (
        url.pathname === window.location.pathname &&
        url.search === window.location.search &&
        !url.hash
      ) {
        return false;
      }
      return true;
    };

    document.addEventListener("click", (event) => {
      if (event.defaultPrevented) return;
      if (event.button !== 0) return;
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (navigating) {
        event.preventDefault();
        return;
      }

      const anchor = event.target.closest("a[href]");
      if (!isInternalNav(anchor)) return;

      event.preventDefault();
      navigating = true;
      markTransition();
      start();
      beginLeave();

      const href = anchor.href;
      window.setTimeout(() => {
        window.location.assign(href);
      }, LEAVE_MS);
    });

    window.addEventListener("pageshow", (event) => {
      let pending = false;
      try {
        pending = sessionStorage.getItem(STORAGE_KEY) === "1";
        if (pending) sessionStorage.removeItem(STORAGE_KEY);
      } catch {
        /* ignore */
      }

      navigating = false;
      document.documentElement.classList.remove("is-page-leaving");

      if (event.persisted) {
        stopTrickle();
        root.classList.remove("is-active", "is-done");
        setProgress(0, true);
        document.documentElement.classList.remove("is-page-entering");
        document.documentElement.classList.add("is-page-ready");
        return;
      }

      revealPage();

      if (pending) {
        root.classList.add("is-active");
        setProgress(0.68, true);
        requestAnimationFrame(() => done());
      }
    });

    /* First paint without a pending transition */
    if (!document.documentElement.classList.contains("is-page-entering")) {
      document.documentElement.classList.add("is-page-ready");
    }

    return { start, done, shell };
  })();

  if (siteProgress) {
    window.__siteProgress = siteProgress;
  }

  /* ── Scroll to top ── */
  const scrollTopBtn = document.querySelector("[data-scroll-top]");
  if (scrollTopBtn) {
    scrollTopBtn.hidden = false;
    const SHOW_AFTER = Math.max(420, Math.round(window.innerHeight * 0.65));
    let visible = false;
    let ticking = false;

    const setVisible = (next) => {
      if (next === visible) return;
      visible = next;
      scrollTopBtn.classList.toggle("is-visible", visible);
      scrollTopBtn.setAttribute("aria-hidden", visible ? "false" : "true");
      scrollTopBtn.tabIndex = visible ? 0 : -1;
    };

    const update = () => {
      ticking = false;
      const y = lenis ? lenis.scroll : window.scrollY || document.documentElement.scrollTop;
      setVisible(y > SHOW_AFTER);
    };

    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    };

    if (lenis) {
      lenis.on("scroll", onScroll);
    } else {
      window.addEventListener("scroll", onScroll, { passive: true });
    }
    update();

    scrollTopBtn.addEventListener("click", () => {
      if (lenis) {
        lenis.scrollTo(0, {
          duration: reduceMotion ? 0.01 : 1.35,
          easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        });
      } else {
        window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      }
    });
  }

  /* ── Mobile nav ── */
  const toggle = document.querySelector("[data-nav-toggle]");
  const mobileNav = document.querySelector("[data-mobile-nav]");

  if (toggle && mobileNav) {
    const setNavOpen = (open) => {
      mobileNav.classList.toggle("hidden", !open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "بستن منو" : "باز کردن منو");
      if (open) {
        const firstLink = mobileNav.querySelector("a");
        if (firstLink) firstLink.focus();
      } else {
        toggle.focus();
      }
    };

    toggle.addEventListener("click", () => {
      const isOpen = !mobileNav.classList.contains("hidden");
      setNavOpen(!isOpen);
    });

    mobileNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        setNavOpen(false);
      });
    });

    document.addEventListener("keydown", (e) => {
      if (e.key !== "Escape") return;
      if (mobileNav.classList.contains("hidden")) return;
      setNavOpen(false);
    });
  }

  /* ── Reveal (GSAP or IntersectionObserver fallback) ── */
  const revealEls = document.querySelectorAll("[data-reveal]");

  if (revealEls.length) {
    /* ScrollTrigger reveals only on full cinematic — IO is far cheaper while scrolling */
    if (
      perf.allowGsapScroll &&
      !reduceMotion &&
      typeof gsap !== "undefined" &&
      typeof ScrollTrigger !== "undefined"
    ) {
      revealEls.forEach((el) => {
        const delay = parseFloat(el.getAttribute("data-delay") || "0") * 0.1;
        gsap.fromTo(
          el,
          { autoAlpha: 0, y: 28 },
          {
            autoAlpha: 1,
            y: 0,
            duration: 0.9,
            delay,
            ease: "power3.out",
            scrollTrigger: {
              trigger: el,
              start: "top 88%",
              once: true,
            },
          }
        );
      });
    } else if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            const el = entry.target;
            const delay = el.getAttribute("data-delay");
            if (delay) el.classList.add(`delay-${delay}`);
            el.classList.add("is-inview");
            el.classList.remove("reveal-prep");
            io.unobserve(el);
          });
        },
        { threshold: 0.08, rootMargin: "0px 0px -4% 0px" }
      );
      revealEls.forEach((el) => {
        el.classList.add("reveal-prep");
        io.observe(el);
      });
    } else {
      revealEls.forEach((el) => el.classList.add("is-inview"));
    }
  }

  /* ── Smooth anchors ── */
  document.querySelectorAll('a[href*="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const href = anchor.getAttribute("href");
      if (!href) return;
      const hashIndex = href.indexOf("#");
      if (hashIndex === -1) return;
      const id = href.slice(hashIndex);
      if (!id || id === "#") return;

      const path = href.slice(0, hashIndex);
      const samePage =
        !path ||
        path === window.location.pathname ||
        path === window.location.pathname + window.location.search;

      if (!samePage) return;

      const target = document.querySelector(id);
      if (!target) return;

      e.preventDefault();
      if (lenis) {
        lenis.scrollTo(target, { offset: -20 });
      } else {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  /* ── Hero Stage: cinematic intro + depth + scroll ── */
  const heroStage = document.querySelector("[data-hero-stage]");
  if (heroStage) {
    const q = (sel) => heroStage.querySelector(sel);
    const qa = (sel) => heroStage.querySelectorAll(sel);

    const mesh = q("[data-hero-mesh]");
    const grid = q("[data-hero-grid]");
    const guides = qa(".hero-guide");
    const spotlight = q("[data-hero-spotlight]");
    const logoSvg = q("[data-hero-logo-svg]");
    const logoImg = q("[data-hero-logo-img]");
    const drawPaths = qa("[data-draw]");
    const tagline = q("[data-hero-tagline]");
    const divider = q("[data-hero-divider]");
    const cta = q("[data-hero-cta]");
    const ctaBtns = qa("[data-hero-btn]");
    const scrollHint = q("[data-hero-scroll]");
    const lockup = q("[data-hero-lockup]");
    const atmosphere = q("[data-hero-atmosphere]");
    const meta = qa("[data-hero-meta]");
    const logoLayer = q('[data-parallax-target="logo"]');

    const showStaticHero = () => {
      if (mesh) mesh.style.opacity = "1";
      if (grid) grid.style.opacity = "0.07";
      guides.forEach((g) => {
        g.style.opacity = "1";
      });
      if (spotlight) spotlight.style.opacity = "1";
      heroStage.style.setProperty("--hero-glow-opacity", "0.55");
      if (logoSvg) logoSvg.style.display = "none";
      if (logoImg) {
        logoImg.style.opacity = "1";
        logoImg.style.filter = "drop-shadow(0 10px 22px rgba(0, 0, 0, 0.28))";
      }
      if (tagline) {
        tagline.style.opacity = "1";
        tagline.style.filter = "none";
        tagline.style.clipPath = "none";
        tagline.style.webkitClipPath = "none";
        tagline.style.visibility = "visible";
      }
      if (divider) {
        divider.style.opacity = "1";
        divider.style.transform = "scaleX(1)";
      }
      if (cta) cta.style.opacity = "1";
      ctaBtns.forEach((btn) => {
        btn.style.opacity = "1";
        btn.style.transform = "none";
      });
      if (scrollHint) scrollHint.style.opacity = "1";
      meta.forEach((el) => {
        el.style.opacity = "1";
      });
    };

    if (reduceMotion || !useGsapHero || typeof gsap === "undefined") {
      showStaticHero();
      heroStage.classList.add("is-hero-ready");
    } else if (!fullMotion) {
      /* Balanced / lite: short opacity fade — no blur, clip-path, or stroke-draw */
      if (logoSvg) gsap.set(logoSvg, { display: "none" });
      gsap.set([mesh, grid, spotlight, guides, logoImg, tagline, divider, ctaBtns, scrollHint, meta], {
        opacity: 0,
      });
      if (cta) gsap.set(cta, { opacity: 1 });
      if (tagline) {
        gsap.set(tagline, {
          clipPath: "none",
          webkitClipPath: "none",
          visibility: "visible",
          filter: "none",
        });
      }
      if (logoImg) gsap.set(logoImg, { filter: "drop-shadow(0 10px 22px rgba(0, 0, 0, 0.28))" });
      if (ctaBtns.length) gsap.set(ctaBtns, { y: 10 });
      if (divider) gsap.set(divider, { scaleX: 0.4 });

      const intro = gsap.timeline({ defaults: { ease: "power2.out" } });
      intro.to(mesh, { opacity: 1, duration: 0.55 }, 0);
      intro.to(grid, { opacity: 0.07, duration: 0.5 }, 0.05);
      intro.to(spotlight, { opacity: 1, duration: 0.45 }, 0.08);
      intro.to(guides, { opacity: 1, duration: 0.4 }, 0.1);
      intro.to(heroStage, { "--hero-glow-opacity": 0.5, duration: 0.6 }, 0.1);
      intro.to(logoImg, { opacity: 1, duration: 0.55 }, 0.12);
      intro.to(tagline, { opacity: 1, duration: 0.45 }, 0.28);
      intro.to(divider, { opacity: 1, scaleX: 1, duration: 0.4 }, 0.38);
      intro.to(
        ctaBtns,
        { opacity: 1, y: 0, duration: 0.4, stagger: 0.04, clearProps: "transform" },
        0.45
      );
      intro.to(scrollHint, { opacity: 1, duration: 0.35 }, 0.55);
      intro.to(meta, { opacity: 1, duration: 0.35 }, 0.55);
    } else {
      const drawDots = qa("[data-draw-dot]");
      const useFilterFx = !!perf.allowFilterFx;

      if (tagline) {
        const tagFrom = {
          autoAlpha: 0,
          clipPath: "inset(0 0 0 100%)",
          webkitClipPath: "inset(0 0 0 100%)",
        };
        if (useFilterFx) tagFrom.filter = "blur(8px)";
        gsap.set(tagline, tagFrom);
      }

      if (drawPaths.length) gsap.set(drawPaths, { strokeDashoffset: 1 });
      if (drawDots.length) gsap.set(drawDots, { opacity: 0 });
      if (logoSvg) {
        const svgFrom = { opacity: 0 };
        if (useFilterFx) svgFrom.filter = "blur(14px)";
        gsap.set(logoSvg, svgFrom);
      }
      gsap.set(logoImg, {
        opacity: 0,
        filter: useFilterFx
          ? "blur(20px) drop-shadow(0 10px 22px rgba(0, 0, 0, 0.28))"
          : "drop-shadow(0 10px 22px rgba(0, 0, 0, 0.28))",
      });
      gsap.set(divider, { scaleX: 0, opacity: 0 });
      gsap.set(ctaBtns, { opacity: 0, y: 18 });
      gsap.set(cta, { opacity: 1 });
      gsap.set(scrollHint, { opacity: 0 });
      gsap.set(meta, { opacity: 0 });
      gsap.set(guides, { opacity: 0 });
      gsap.set(mesh, { opacity: 0 });
      gsap.set(grid, { opacity: 0 });
      gsap.set(spotlight, { opacity: 0 });

      const intro = gsap.timeline({
        defaults: { ease: "power2.out" },
        delay: 0,
      });

      intro.to(mesh, { opacity: 1, duration: 1.15, ease: "power1.out" }, 0);
      intro.to(grid, { opacity: 0.085, duration: 1.05, ease: "power1.inOut" }, 0.1);
      intro.to(guides, { opacity: 1, duration: 0.75, stagger: 0.06, ease: "power1.out" }, 0.2);
      intro.to(spotlight, { opacity: 1, duration: 0.9 }, 0.3);
      intro.to(
        heroStage,
        { "--hero-glow-opacity": 0.72, duration: 1.45, ease: "sine.inOut" },
        0.35
      );

      if (logoSvg && drawPaths.length && perf.allowHeroDraw) {
        intro.to(logoSvg, { opacity: 1, duration: 0.28 }, 0.4);
        intro.to(
          drawPaths,
          {
            strokeDashoffset: 0,
            duration: 1.55,
            stagger: { each: 0.03, from: "start" },
            ease: "power1.inOut",
          },
          0.45
        );
        intro.to(
          drawDots,
          { opacity: 1, duration: 0.35, stagger: 0.09, ease: "power1.out" },
          1.55
        );
        if (useFilterFx) {
          intro.to(logoSvg, { filter: "blur(0px)", duration: 0.85, ease: "power2.out" }, 1.5);
        }
        intro.to(
          logoImg,
          {
            opacity: 1,
            filter: "drop-shadow(0 10px 22px rgba(0, 0, 0, 0.28))",
            duration: 1.05,
            ease: "power2.out",
          },
          1.6
        );
        intro.to(logoSvg, { opacity: 0, duration: 0.5, ease: "power1.out" }, 2.0);
      } else if (logoImg) {
        if (logoSvg) gsap.set(logoSvg, { display: "none" });
        intro.to(
          logoImg,
          {
            opacity: 1,
            filter: "drop-shadow(0 10px 22px rgba(0, 0, 0, 0.28))",
            duration: 1.0,
            ease: "power2.out",
          },
          0.45
        );
      }

      if (tagline) {
        const tagTo = {
          autoAlpha: 1,
          clipPath: "inset(0 0 0 0%)",
          webkitClipPath: "inset(0 0 0 0%)",
          duration: 1.05,
          ease: "power2.out",
        };
        if (useFilterFx) tagTo.filter = "blur(0px)";
        intro.to(tagline, tagTo, perf.allowHeroDraw ? 1.4 : 1.0);
      }

      intro.to(
        divider,
        { scaleX: 1, opacity: 1, duration: 0.75, ease: "power3.inOut" },
        perf.allowHeroDraw ? 2.25 : 1.6
      );
      intro.to(
        ctaBtns,
        {
          opacity: 1,
          y: 0,
          duration: 0.9,
          stagger: 0.09,
          ease: "power3.out",
          clearProps: "transform",
        },
        perf.allowHeroDraw ? 2.45 : 1.8
      );
      intro.to(scrollHint, { opacity: 1, duration: 0.8, ease: "power1.out" }, perf.allowHeroDraw ? 2.9 : 2.2);
      intro.to(meta, { opacity: 1, duration: 0.95, stagger: 0.1 }, perf.allowHeroDraw ? 3.0 : 2.3);
    }

    /* Mouse parallax — full tier only */
    if (perf.allowParallax && !reduceMotion) {
      const mouse = { x: 0, y: 0, tx: 0, ty: 0, sx: 50, sy: 42, tsx: 50, tsy: 42 };
      const finePointer = window.matchMedia("(pointer: fine)").matches;
      let parallaxFrame = 0;
      let parallaxActive = false;

      if (finePointer) {
        const tickParallax = () => {
          mouse.x += (mouse.tx - mouse.x) * 0.045;
          mouse.y += (mouse.ty - mouse.y) * 0.045;
          mouse.sx += (mouse.tsx - mouse.sx) * 0.06;
          mouse.sy += (mouse.tsy - mouse.sy) * 0.06;

          heroStage.style.setProperty("--hero-spot-x", `${mouse.sx.toFixed(2)}%`);
          heroStage.style.setProperty("--hero-spot-y", `${mouse.sy.toFixed(2)}%`);

          if (grid) {
            grid.style.transform = `translate3d(${mouse.x * 6}px, ${mouse.y * 6}px, 0)`;
          }
          if (logoLayer) {
            logoLayer.style.transform = `translate3d(${mouse.x * 2.5}px, ${mouse.y * 2.5}px, 0)`;
          }

          const settling =
            Math.abs(mouse.tx - mouse.x) > 0.002 ||
            Math.abs(mouse.ty - mouse.y) > 0.002 ||
            Math.abs(mouse.tsx - mouse.sx) > 0.05 ||
            Math.abs(mouse.tsy - mouse.sy) > 0.05;

          if (parallaxActive || settling) {
            parallaxFrame = requestAnimationFrame(tickParallax);
          } else {
            parallaxFrame = 0;
          }
        };

        const ensureTick = () => {
          if (!parallaxFrame) parallaxFrame = requestAnimationFrame(tickParallax);
        };

        heroStage.addEventListener(
          "pointermove",
          (e) => {
            const rect = heroStage.getBoundingClientRect();
            mouse.tx = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
            mouse.ty = ((e.clientY - rect.top) / rect.height - 0.5) * 2;
            mouse.tsx = ((e.clientX - rect.left) / rect.width) * 100;
            mouse.tsy = ((e.clientY - rect.top) / rect.height) * 100;
            parallaxActive = true;
            ensureTick();
          },
          { passive: true }
        );

        heroStage.addEventListener(
          "pointerleave",
          () => {
            mouse.tx = 0;
            mouse.ty = 0;
            mouse.tsx = 50;
            mouse.tsy = 42;
            parallaxActive = false;
            ensureTick();
          },
          { passive: true }
        );
      }
    }

    /* Scroll cinema — full tier only */
    if (
      perf.allowScrub &&
      !reduceMotion &&
      typeof gsap !== "undefined" &&
      typeof ScrollTrigger !== "undefined"
    ) {
      const scrollTl = gsap.timeline({
        scrollTrigger: {
          trigger: heroStage,
          start: "top top",
          end: "bottom top",
          scrub: 1.2,
        },
      });

      if (atmosphere) {
        scrollTl.to(atmosphere, { scale: 1.08, ease: "none" }, 0);
      }
      if (grid) {
        scrollTl.to(grid, { opacity: 0, ease: "none" }, 0);
      }
      if (lockup) {
        scrollTl.to(
          lockup,
          { scale: 0.9, y: -36, autoAlpha: 0.35, ease: "none" },
          0
        );
      }
      if (logoImg) {
        scrollTl.to(logoImg, { scale: 0.94, ease: "none" }, 0);
      }
      if (scrollHint) {
        scrollTl.to(scrollHint, { autoAlpha: 0, ease: "none" }, 0);
      }
      scrollTl.to(
        heroStage,
        { "--hero-glow-opacity": 0, ease: "none" },
        0
      );
    }
  }

  /* Gallery: see static/js/gallery.js (homepage only) */

  /* ── Counters ── */
  const counters = document.querySelectorAll("[data-counter]");
  if (counters.length && "IntersectionObserver" in window) {
    const animateCounter = (el) => {
      const target = parseFloat(el.getAttribute("data-target") || "0");
      const decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      const suffix = el.getAttribute("data-suffix") || "";
      const duration = liteMotion ? 900 : 1800;
      const start = performance.now();

      if (reduceMotion) {
        el.textContent = toPersianDigits(target.toFixed(decimals) + suffix);
        return;
      }

      const tick = (now) => {
        const t = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        el.textContent = toPersianDigits((target * eased).toFixed(decimals) + suffix);
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };

    const cio = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          animateCounter(entry.target);
          cio.unobserve(entry.target);
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach((el) => cio.observe(el));
  }

  /* ── Magnetic buttons — soft premium pull ── */
  if (perf.allowMagnetic && !reduceMotion && window.matchMedia("(pointer: fine)").matches) {
    document.querySelectorAll("[data-magnetic]").forEach((btn) => {
      const strength = 22;
      let frame = 0;
      let currentX = 0;
      let currentY = 0;
      let targetX = 0;
      let targetY = 0;
      let tracking = false;

      const tick = () => {
        currentX += (targetX - currentX) * 0.14;
        currentY += (targetY - currentY) * 0.14;
        btn.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
        if (
          tracking ||
          Math.abs(targetX - currentX) > 0.05 ||
          Math.abs(targetY - currentY) > 0.05
        ) {
          frame = requestAnimationFrame(tick);
        } else {
          frame = 0;
        }
      };

      btn.addEventListener("mousemove", (e) => {
        const rect = btn.getBoundingClientRect();
        targetX = (e.clientX - rect.left - rect.width / 2) / strength;
        targetY = (e.clientY - rect.top - rect.height / 2) / strength;
        tracking = true;
        if (!frame) frame = requestAnimationFrame(tick);
      });

      btn.addEventListener("mouseleave", () => {
        targetX = 0;
        targetY = 0;
        tracking = false;
        if (!frame) frame = requestAnimationFrame(tick);
      });
    });
  }

  /* ── Blur-up lazy images ── */
  document.querySelectorAll("img[loading='lazy']").forEach((img) => {
    if (img.complete) return;
    img.dataset.blurUp = "true";
    img.addEventListener(
      "load",
      () => {
        img.classList.add("is-loaded");
        delete img.dataset.blurUp;
      },
      { once: true }
    );
  });
})();
