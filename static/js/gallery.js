/**
 * Luxury editorial gallery — Swiper stage, filters, fullscreen lightbox,
 * before/after compare, video, keyboard & touch.
 */
(function () {
  "use strict";

  const root = document.querySelector("[data-gallery-root]");
  if (!root || typeof Swiper === "undefined") return;

  const perf = window.__sitePerf || {
    reduce: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    lite: true,
    full: false,
  };
  const reduceMotion = !!perf.reduce;
  const liteMotion = !!perf.lite;
  const fullMotion = !!perf.full;

  const payloadEl = document.getElementById("gallery-payload");
  let items = [];
  try {
    items = payloadEl ? JSON.parse(payloadEl.textContent || "[]") : [];
  } catch (_err) {
    items = [];
  }

  const swiperEl = root.querySelector("[data-gallery-swiper]");
  const paginationEl = root.querySelector("[data-gallery-pagination]");
  const prevEl = root.querySelector("[data-gallery-prev]");
  const nextEl = root.querySelector("[data-gallery-next]");
  const filterBtns = Array.from(root.querySelectorAll("[data-gallery-filter]"));
  const openBtns = Array.from(root.querySelectorAll("[data-gallery-open]"));

  const lightbox = root.querySelector("[data-gallery-lightbox]");
  if (!swiperEl || !lightbox) return;

  /* ── Progressive image load ── */
  const markLoaded = (media) => media.classList.add("is-loaded");

  root.querySelectorAll("[data-gallery-media]").forEach((media) => {
    const img = media.querySelector("[data-gallery-img]");
    if (!img) {
      markLoaded(media);
      return;
    }
    if (img.complete && img.naturalWidth) {
      markLoaded(media);
    } else {
      img.addEventListener("load", () => markLoaded(media), { once: true });
      img.addEventListener("error", () => markLoaded(media), { once: true });
    }
  });

  /* ── Swiper ── */
  const gallerySwiper = new Swiper(swiperEl, {
    slidesPerView: "auto",
    centeredSlides: true,
    spaceBetween: 18,
    loop: items.length > 3,
    speed: reduceMotion ? 0 : fullMotion ? 900 : 420,
    grabCursor: true,
    watchSlidesProgress: true,
    observer: true,
    observeParents: true,
    resistanceRatio: 0.72,
    freeMode: false,
    keyboard: {
      enabled: true,
      onlyInViewport: true,
    },
    autoplay: fullMotion && !reduceMotion
      ? {
          delay: 4800,
          disableOnInteraction: false,
          pauseOnMouseEnter: true,
        }
      : false,
    pagination: paginationEl
      ? {
          el: paginationEl,
          clickable: true,
        }
      : undefined,
    navigation:
      prevEl && nextEl
        ? {
            nextEl,
            prevEl,
          }
        : undefined,
    breakpoints: {
      640: { spaceBetween: 22 },
      1024: { spaceBetween: 28 },
      1280: { spaceBetween: 32 },
    },
    on: {
      init(sw) {
        sw.slides.forEach((slide) => {
          slide.setAttribute("role", "group");
          slide.setAttribute("aria-roledescription", "slide");
        });
      },
    },
  });

  if (typeof ScrollTrigger !== "undefined" && window.__sitePerf && window.__sitePerf.allowGsapScroll) {
    ScrollTrigger.create({
      trigger: swiperEl,
      start: "top 92%",
      once: true,
      onEnter: () => gallerySwiper.update(),
    });
  } else {
    window.addEventListener("load", () => gallerySwiper.update(), { once: true });
  }

  /* ── Category filters ── */
  let activeFilter = "all";

  const applyFilter = (slug) => {
    activeFilter = slug;
    filterBtns.forEach((btn) => {
      const isActive = btn.getAttribute("data-gallery-filter") === slug;
      btn.classList.toggle("is-active", isActive);
      btn.setAttribute("aria-selected", isActive ? "true" : "false");
    });

    const slides = Array.from(swiperEl.querySelectorAll(".swiper-slide[data-gallery-slide]"));
    let firstVisible = -1;
    let visibleCount = 0;

    slides.forEach((slide, index) => {
      const cat = slide.getAttribute("data-category") || "all";
      const visible = slug === "all" || cat === slug;
      slide.classList.toggle("is-filtered-out", !visible);
      slide.style.display = visible ? "" : "none";
      if (visible) {
        visibleCount += 1;
        if (firstVisible < 0) firstVisible = index;
      }
    });

    if (gallerySwiper.params.loop) {
      gallerySwiper.loopDestroy();
    }
    gallerySwiper.params.loop = slug === "all" && visibleCount > 3;
    gallerySwiper.update();
    if (gallerySwiper.params.loop) {
      gallerySwiper.loopCreate();
      gallerySwiper.update();
    }
    gallerySwiper.slideTo(Math.max(firstVisible, 0), reduceMotion ? 0 : 700);
  };

  filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const slug = btn.getAttribute("data-gallery-filter") || "all";
      if (slug === activeFilter) return;
      applyFilter(slug);
    });
  });

  /* ── Lightbox state ── */
  const lb = {
    el: lightbox,
    category: lightbox.querySelector("[data-lb-category]"),
    title: lightbox.querySelector("[data-lb-title]"),
    description: lightbox.querySelector("[data-lb-description]"),
    facts: lightbox.querySelector("[data-lb-facts]"),
    review: lightbox.querySelector("[data-lb-review]"),
    ctaTitle: lightbox.querySelector("[data-lb-cta-title]"),
    consult: lightbox.querySelector("[data-lb-consult]"),
    book: lightbox.querySelector("[data-lb-book]"),
    thumbs: lightbox.querySelector("[data-lb-thumbs]"),
    img: lightbox.querySelector("[data-lb-img]"),
    video: lightbox.querySelector("[data-lb-video]"),
    before: lightbox.querySelector("[data-lb-before]"),
    after: lightbox.querySelector("[data-lb-after]"),
    beforePane: lightbox.querySelector("[data-lb-before-pane]"),
    compareHandle: lightbox.querySelector("[data-lb-compare-handle]"),
    compare: lightbox.querySelector("[data-lb-compare]"),
    modes: {
      image: lightbox.querySelector('[data-lb-mode="image"]'),
      video: lightbox.querySelector('[data-lb-mode="video"]'),
      ba: lightbox.querySelector('[data-lb-mode="ba"]'),
    },
    prev: lightbox.querySelector("[data-lb-prev]"),
    next: lightbox.querySelector("[data-lb-next]"),
  };

  let currentItemIndex = 0;
  let currentMediaIndex = 0;
  let mediaList = [];
  let lastFocus = null;
  let pinchStartDist = 0;
  let isZoomed = false;

  const setMode = (mode) => {
    Object.entries(lb.modes).forEach(([key, node]) => {
      if (!node) return;
      const active = key === mode;
      node.hidden = !active;
      node.classList.toggle("is-active", active);
    });
  };

  const stopVideo = () => {
    if (!lb.video) return;
    lb.video.pause();
    lb.video.removeAttribute("src");
    lb.video.load();
  };

  const buildFacts = (item) => {
    if (!lb.facts) return;
    const story = item.story || {};
    const rows = [
      ["مشکل", story.problem],
      ["راه‌حل", story.solution],
      ["خدمات", story.services],
      ["مدت", story.duration],
      ["نتیجه", story.result],
      ["مکان", item.location],
      ["تاریخ", item.completed_at],
    ].filter(([, v]) => Boolean(v));

    lb.facts.innerHTML = rows
      .map(
        ([k, v]) =>
          `<div><dt>${k}</dt><dd>${String(v)
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")}</dd></div>`
      )
      .join("");
  };

  const buildThumbs = () => {
    if (!lb.thumbs) return;
    lb.thumbs.innerHTML = "";
    mediaList.forEach((media, index) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "gallery-lb-thumb" + (index === currentMediaIndex ? " is-active" : "");
      btn.setAttribute("role", "tab");
      btn.setAttribute("aria-label", media.label || `رسانه ${index + 1}`);
      btn.setAttribute("aria-selected", index === currentMediaIndex ? "true" : "false");

      if (media.kind === "video") {
        btn.innerHTML =
          '<span style="display:grid;place-items:center;width:100%;height:100%;font-size:0.7rem;color:rgba(247,244,239,0.7)">▶</span>';
      } else if (media.kind === "ba") {
        btn.innerHTML =
          '<span style="display:grid;place-items:center;width:100%;height:100%;font-size:0.55rem;letter-spacing:0.08em;color:rgba(247,244,239,0.65)">B/A</span>';
      } else {
        const img = document.createElement("img");
        img.src = media.thumb || media.src;
        img.alt = "";
        img.loading = "lazy";
        img.decoding = "async";
        btn.appendChild(img);
      }

      btn.addEventListener("click", () => showMedia(index));
      lb.thumbs.appendChild(btn);
    });
  };

  const buildMediaList = (item) => {
    const list = [];
    (item.images || []).forEach((img) => {
      if (!img.src) return;
      list.push({
        kind: "image",
        src: img.src,
        thumb: img.lqip || img.src,
        alt: img.alt || item.title,
        label: img.caption || item.title,
      });
    });
    if (item.has_video && item.video_src) {
      list.push({
        kind: "video",
        src: item.video_src,
        poster: item.video_poster || (item.cover && item.cover.src) || "",
        label: "ویدئو",
      });
    }
    if (item.has_before_after && item.before && item.after) {
      list.push({
        kind: "ba",
        before: item.before,
        after: item.after,
        label: "قبل و بعد",
      });
    }
    if (!list.length && item.cover && item.cover.src) {
      list.push({
        kind: "image",
        src: item.cover.src,
        thumb: item.cover.lqip || item.cover.src,
        alt: item.cover.alt || item.title,
        label: item.title,
      });
    }
    return list;
  };

  const setCompare = (percent) => {
    const p = Math.max(4, Math.min(96, percent));
    if (lb.beforePane) lb.beforePane.style.width = `${p}%`;
    if (lb.compareHandle) {
      lb.compareHandle.style.insetInlineStart = `${p}%`;
      lb.compareHandle.setAttribute("aria-valuenow", String(Math.round(p)));
    }
  };

  const syncBaWidth = () => {
    const vp = lightbox.querySelector("[data-lb-viewport]");
    if (vp && lb.compare) {
      lb.compare.style.setProperty("--ba-width", `${vp.clientWidth}px`);
    }
  };

  const showMedia = (index) => {
    if (!mediaList.length) return;
    currentMediaIndex = (index + mediaList.length) % mediaList.length;
    const media = mediaList[currentMediaIndex];
    stopVideo();
    isZoomed = false;
    if (lb.img) lb.img.classList.remove("is-zoomed");

    if (media.kind === "video") {
      setMode("video");
      if (lb.video) {
        lb.video.src = media.src;
        if (media.poster) lb.video.poster = media.poster;
        lb.video.play().catch(() => {});
      }
    } else if (media.kind === "ba") {
      setMode("ba");
      if (lb.before) {
        lb.before.src = media.before.src;
        lb.before.alt = media.before.alt || "";
      }
      if (lb.after) {
        lb.after.src = media.after.src;
        lb.after.alt = media.after.alt || "";
      }
      setCompare(50);
      syncBaWidth();
    } else {
      setMode("image");
      if (lb.img) {
        lb.img.src = media.src;
        lb.img.alt = media.alt || "";
      }
    }

    if (lb.thumbs) {
      Array.from(lb.thumbs.children).forEach((node, i) => {
        const on = i === currentMediaIndex;
        node.classList.toggle("is-active", on);
        node.setAttribute("aria-selected", on ? "true" : "false");
      });
    }
  };

  const populateItem = (item) => {
    if (lb.category) lb.category.textContent = item.category_title || "";
    if (lb.title) lb.title.textContent = item.title || "";
    if (lb.description) lb.description.textContent = item.description || item.subtitle || "";
    buildFacts(item);

    if (lb.review) {
      if (item.story && item.story.review) {
        lb.review.hidden = false;
        lb.review.textContent = `«${item.story.review}»`;
      } else {
        lb.review.hidden = true;
        lb.review.textContent = "";
      }
    }

    const cta = item.cta || {};
    if (lb.ctaTitle) lb.ctaTitle.textContent = cta.title || "از این نتیجه خوشتان آمد؟";
    if (lb.consult) {
      lb.consult.href = cta.consultation_url || "#";
      lb.consult.textContent = cta.consultation_label || "دریافت مشاوره";
    }
    if (lb.book) {
      lb.book.href = cta.booking_url || "#";
      lb.book.textContent = cta.booking_label || "رزرو این خدمت";
    }

    mediaList = buildMediaList(item);
    currentMediaIndex = 0;
    buildThumbs();
    showMedia(0);
  };

  const openLightbox = (itemIndex) => {
    if (!items.length) return;
    currentItemIndex = Math.max(0, Math.min(itemIndex, items.length - 1));
    const item = items[currentItemIndex];
    if (!item) return;

    lastFocus = document.activeElement;
    populateItem(item);

    if (lightbox.parentElement !== document.body) {
      document.body.appendChild(lightbox);
    }

    lightbox.hidden = false;
    requestAnimationFrame(() => {
      lightbox.classList.add("is-open");
    });
    document.body.classList.add("gallery-lb-open");
    if (gallerySwiper.autoplay && gallerySwiper.autoplay.running) {
      gallerySwiper.autoplay.stop();
    }

    const closeBtn = lightbox.querySelector("[data-gallery-lb-close]");
    if (closeBtn) closeBtn.focus({ preventScroll: true });
  };

  const closeLightbox = () => {
    lightbox.classList.remove("is-open");
    document.body.classList.remove("gallery-lb-open");
    stopVideo();
    isZoomed = false;
    if (lb.img) lb.img.classList.remove("is-zoomed");

    window.setTimeout(() => {
      if (!lightbox.classList.contains("is-open")) {
        lightbox.hidden = true;
      }
    }, reduceMotion ? 0 : 420);

    if (gallerySwiper.autoplay && !reduceMotion) {
      gallerySwiper.autoplay.start();
    }
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus({ preventScroll: true });
    }
  };

  const stepItem = (delta) => {
    if (!items.length) return;
    let next = currentItemIndex + delta;
    // respect active filter
    for (let i = 0; i < items.length; i += 1) {
      next = (next + items.length) % items.length;
      const candidate = items[next];
      if (activeFilter === "all" || candidate.category === activeFilter) {
        currentItemIndex = next;
        populateItem(candidate);
        return;
      }
      next += delta;
    }
  };

  openBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.getAttribute("data-gallery-open") || "0", 10);
      openLightbox(idx);
    });
  });

  lightbox.querySelectorAll("[data-gallery-lb-close]").forEach((node) => {
    node.addEventListener("click", closeLightbox);
  });

  if (lb.prev) {
    lb.prev.addEventListener("click", () => {
      if (mediaList.length > 1) showMedia(currentMediaIndex - 1);
      else stepItem(-1);
    });
  }
  if (lb.next) {
    lb.next.addEventListener("click", () => {
      if (mediaList.length > 1) showMedia(currentMediaIndex + 1);
      else stepItem(1);
    });
  }

  if (lb.img) {
    lb.img.addEventListener("click", () => {
      isZoomed = !isZoomed;
      lb.img.classList.toggle("is-zoomed", isZoomed);
    });
  }

  /* ── Before/After drag ── */
  const bindCompare = () => {
    if (!lb.compare || !lb.compareHandle) return;
    let dragging = false;

    const updateFromClientX = (clientX) => {
      const rect = lb.compare.getBoundingClientRect();
      if (!rect.width) return;
      // RTL: measure from right edge for visual consistency with inset-inline
      const isRtl = document.documentElement.dir === "rtl";
      const ratio = isRtl
        ? (rect.right - clientX) / rect.width
        : (clientX - rect.left) / rect.width;
      setCompare(ratio * 100);
      syncBaWidth();
    };

    const onPointerDown = (e) => {
      dragging = true;
      lb.compareHandle.setPointerCapture?.(e.pointerId);
      updateFromClientX(e.clientX);
    };
    const onPointerMove = (e) => {
      if (!dragging) return;
      updateFromClientX(e.clientX);
    };
    const onPointerUp = (e) => {
      dragging = false;
      try {
        lb.compareHandle.releasePointerCapture?.(e.pointerId);
      } catch (_e) {}
    };

    lb.compare.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);

    lb.compareHandle.addEventListener("keydown", (e) => {
      const now = parseFloat(lb.compareHandle.getAttribute("aria-valuenow") || "50");
      if (e.key === "ArrowLeft" || e.key === "ArrowDown") {
        e.preventDefault();
        setCompare(now - 4);
      } else if (e.key === "ArrowRight" || e.key === "ArrowUp") {
        e.preventDefault();
        setCompare(now + 4);
      } else if (e.key === "Home") {
        e.preventDefault();
        setCompare(4);
      } else if (e.key === "End") {
        e.preventDefault();
        setCompare(96);
      }
    });
  };
  bindCompare();

  /* ── Touch swipe in lightbox viewport ── */
  const viewport = lightbox.querySelector("[data-lb-viewport]");
  if (viewport) {
    let startX = 0;
    let startY = 0;
    let tracking = false;

    viewport.addEventListener(
      "touchstart",
      (e) => {
        if (e.touches.length === 1) {
          tracking = true;
          startX = e.touches[0].clientX;
          startY = e.touches[0].clientY;
        } else if (e.touches.length === 2) {
          tracking = false;
          const [a, b] = e.touches;
          pinchStartDist = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
        }
      },
      { passive: true }
    );

    viewport.addEventListener(
      "touchmove",
      (e) => {
        if (e.touches.length === 2 && lb.img && !lb.modes.image.hidden) {
          const [a, b] = e.touches;
          const dist = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
          if (pinchStartDist && dist / pinchStartDist > 1.15) {
            isZoomed = true;
            lb.img.classList.add("is-zoomed");
          } else if (pinchStartDist && dist / pinchStartDist < 0.85) {
            isZoomed = false;
            lb.img.classList.remove("is-zoomed");
          }
        }
      },
      { passive: true }
    );

    viewport.addEventListener(
      "touchend",
      (e) => {
        if (!tracking) return;
        tracking = false;
        const touch = e.changedTouches[0];
        if (!touch) return;
        const dx = touch.clientX - startX;
        const dy = touch.clientY - startY;
        if (Math.abs(dx) < 48 || Math.abs(dx) < Math.abs(dy)) return;
        // RTL: swipe toward start (right) → previous visually feels like next in LTR terms
        const isRtl = document.documentElement.dir === "rtl";
        if (dx > 0) {
          if (isRtl) showMedia(currentMediaIndex + 1);
          else showMedia(currentMediaIndex - 1);
        } else if (isRtl) showMedia(currentMediaIndex - 1);
        else showMedia(currentMediaIndex + 1);
      },
      { passive: true }
    );
  }

  /* ── Keyboard ── */
  document.addEventListener("keydown", (e) => {
    if (!lightbox.classList.contains("is-open")) return;
    if (e.key === "Escape") {
      e.preventDefault();
      closeLightbox();
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      showMedia(currentMediaIndex - 1);
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      showMedia(currentMediaIndex + 1);
    } else if (e.key === "Home") {
      e.preventDefault();
      showMedia(0);
    } else if (e.key === "End") {
      e.preventDefault();
      showMedia(mediaList.length - 1);
    }
  });

  /* ── Lazy animate cards into view ── */
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-inview");
          io.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.15 }
    );
    root.querySelectorAll("[data-gallery-card]").forEach((card) => io.observe(card));
  }
})();
