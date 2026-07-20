/**
 * Magazine hub + article interactions.
 * Hub first paint is SSR; JS hydrates filters/search and progressive images.
 */
(function () {
  "use strict";

  const FA = "۰۱۲۳۴۵۶۷۸۹";
  const toFa = (n) => String(n).replace(/\d/g, (d) => FA[d]);
  const REDUCE = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function csrfToken() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  async function api(url, options = {}) {
    const opts = {
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        "X-CSRFToken": csrfToken(),
        ...(options.headers || {}),
      },
      ...options,
    };
    const res = await fetch(url, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      throw new Error(data.error || "خطا در ارتباط با سرور");
    }
    return data;
  }

  function staticUrl(root, path) {
    if (!path) return "";
    if (/^https?:\/\//i.test(path) || path.startsWith("/media/") || path.startsWith("/static/")) {
      return path;
    }
    return root + path.replace(/^\//, "");
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  function metaLine(a) {
    const mins = a.reading_minutes_fa || toFa(a.reading_minutes || 0);
    const parts = [a.category?.title, `${mins} دقیقه`, a.published_at_fa].filter(Boolean);
    return parts.map(escapeHtml).join(" · ");
  }

  /* ── LQIP progressive reveal ── */
  function bindLqip(scope) {
    const root = scope || document;
    root.querySelectorAll("[data-lqip-frame]").forEach((frame) => {
      if (frame.dataset.lqipBound === "1") return;
      frame.dataset.lqipBound = "1";
      const full = frame.querySelector("[data-lqip-full]");
      if (!full) {
        frame.classList.add("is-loaded");
        return;
      }
      const mark = () => frame.classList.add("is-loaded");
      if (full.complete && full.naturalWidth > 0) {
        mark();
      } else {
        full.addEventListener("load", mark, { once: true });
        full.addEventListener("error", mark, { once: true });
      }
    });
  }

  function mediaHTML(a, staticRoot, { eager = false, ratioClass = "" } = {}) {
    const cover = staticUrl(staticRoot, a.cover);
    const lqip = staticUrl(staticRoot, a.cover_lqip);
    if (!cover) {
      return `<div class="mag-media mag-media-empty ${ratioClass}" aria-hidden="true"></div>`;
    }
    return `
      <div class="mag-media ${ratioClass}" data-lqip-frame>
        ${
          lqip
            ? `<img src="${lqip}" alt="" class="mag-media-lqip" width="16" height="20" aria-hidden="true" decoding="async">`
            : ""
        }
        <img
          src="${cover}"
          alt="${escapeAttr(a.cover_alt || a.title)}"
          class="mag-media-img"
          width="1200"
          height="1500"
          ${eager ? 'fetchpriority="high"' : 'loading="lazy"'}
          decoding="async"
          data-lqip-full
        >
      </div>`;
  }

  function entryHTML(a, staticRoot, variant) {
    const isLead = variant === "lead";
    const isRow = variant === "row";
    const classes = [
      "mag-entry",
      isLead ? "mag-entry-lead" : "",
      isRow ? "mag-entry-row" : "",
      variant === "stack" ? "mag-entry-stack" : "",
      variant === "archive" ? "mag-entry-archive" : "",
    ]
      .filter(Boolean)
      .join(" ");

    const ratio =
      isLead ? "mag-media-portrait" : isRow ? "mag-media-square" : "mag-media-landscape";

    return `
      <a href="${a.url}" class="${classes}" data-reveal>
        ${mediaHTML(a, staticRoot, { eager: isLead, ratioClass: ratio })}
        <div class="mag-entry-body">
          <p class="mag-entry-cat">${escapeHtml(a.category?.title || "")}</p>
          <h3 class="mag-entry-title">${escapeHtml(a.title)}</h3>
          ${
            a.excerpt && (isLead || variant === "archive")
              ? `<p class="mag-entry-excerpt">${escapeHtml(a.excerpt)}</p>`
              : ""
          }
          <p class="mag-entry-meta">${metaLine(a)}</p>
          ${isLead ? `<span class="mag-entry-cta">مطالعه <span aria-hidden="true">←</span></span>` : ""}
        </div>
      </a>`;
  }

  /* ═══════════════ HUB ═══════════════ */
  function initHub(root) {
    const apiBase = root.dataset.apiBase || "/magazine/api";
    const staticRoot = root.dataset.static || "/static/";
    const ssr = root.dataset.ssr === "1";

    let state = {
      category: root.dataset.filterCategory || new URLSearchParams(location.search).get("category") || "",
      tag: root.dataset.filterTag || new URLSearchParams(location.search).get("tag") || "",
      sort: root.dataset.filterSort || new URLSearchParams(location.search).get("sort") || "newest",
      page: parseInt(root.dataset.filterPage || new URLSearchParams(location.search).get("page") || "1", 10) || 1,
      q: root.dataset.filterQ || new URLSearchParams(location.search).get("q") || "",
    };

    const els = {
      coverMount: root.querySelector("[data-cover-mount]"),
      catTrack: root.querySelector("[data-cat-track]"),
      featured: root.querySelector("[data-featured-grid]"),
      latest: root.querySelector("[data-latest-grid]"),
      popular: root.querySelector("[data-popular-list]"),
      tags: root.querySelector("[data-tag-cloud]"),
      pagination: root.querySelector("[data-pagination]"),
      empty: root.querySelector("[data-latest-empty]"),
      error: root.querySelector("[data-hub-error]"),
      errorText: root.querySelector("[data-hub-error-text]"),
      retry: root.querySelector("[data-hub-retry]"),
      searchInput: root.querySelector("[data-search-input]"),
      searchDrop: root.querySelector("[data-search-dropdown]"),
      filterStatus: root.querySelector("[data-filter-status]"),
      clearFilters: root.querySelector("[data-clear-filters]"),
      progress: root.querySelector("[data-hub-progress]"),
      journeyTitle: root.querySelector("[data-journey-title]"),
      journeyCopy: root.querySelector("[data-journey-copy]"),
      journeyConsult: root.querySelector("[data-journey-consult]"),
      journeyBook: root.querySelector("[data-journey-book]"),
      sortBtns: root.querySelectorAll("[data-filter-sort]"),
    };

    function showError(msg) {
      if (!els.error) return;
      els.error.hidden = false;
      if (els.errorText) els.errorText.textContent = msg;
    }

    function hideError() {
      if (els.error) els.error.hidden = true;
    }

    function updateFilterStatus() {
      if (!els.filterStatus) return;
      const bits = [];
      if (state.category) bits.push(`موضوع: ${state.category}`);
      if (state.tag) bits.push(`برچسب: ${state.tag}`);
      if (state.q) bits.push(`جستجو: «${state.q}»`);
      if (!bits.length) {
        els.filterStatus.hidden = true;
        els.filterStatus.innerHTML = "";
        return;
      }
      els.filterStatus.hidden = false;
      els.filterStatus.innerHTML = `
        <span>${escapeHtml(bits.join(" · "))}</span>
        <button type="button" class="mag-text-btn" data-clear-inline>پاک کردن</button>`;
      els.filterStatus.querySelector("[data-clear-inline]")?.addEventListener("click", clearFilters);
    }

    function clearFilters() {
      state.category = "";
      state.tag = "";
      state.q = "";
      state.page = 1;
      if (els.searchInput) els.searchInput.value = "";
      els.catTrack?.querySelectorAll(".mag-topic").forEach((b) => {
        const active = !(b.getAttribute("data-cat") || "");
        b.classList.toggle("is-active", active);
        b.setAttribute("aria-pressed", active ? "true" : "false");
      });
      els.tags?.querySelectorAll(".mag-tag-btn").forEach((b) => {
        b.classList.remove("is-active");
        b.setAttribute("aria-pressed", "false");
      });
      updateFilterStatus();
      loadArticles();
      syncUrl();
    }

    function bindCategoryClicks() {
      els.catTrack?.querySelectorAll("[data-cat]").forEach((btn) => {
        btn.addEventListener("click", () => {
          state.category = btn.getAttribute("data-cat") || "";
          state.page = 1;
          els.catTrack.querySelectorAll(".mag-topic").forEach((b) => {
            const on = b === btn;
            b.classList.toggle("is-active", on);
            b.setAttribute("aria-pressed", on ? "true" : "false");
          });
          updateFilterStatus();
          loadArticles();
          syncUrl();
        });
      });
    }

    function bindTagClicks() {
      els.tags?.querySelectorAll("[data-tag]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const slug = btn.getAttribute("data-tag") || "";
          state.tag = state.tag === slug ? "" : slug;
          state.page = 1;
          els.tags.querySelectorAll(".mag-tag-btn").forEach((b) => {
            const on = b.getAttribute("data-tag") === state.tag;
            b.classList.toggle("is-active", on);
            b.setAttribute("aria-pressed", on ? "true" : "false");
          });
          updateFilterStatus();
          loadArticles();
          syncUrl();
        });
      });
    }

    function renderLatest(data) {
      if (!els.latest) return;
      const list = data.articles || [];
      els.empty?.toggleAttribute("hidden", list.length > 0);
      els.latest.innerHTML = list.map((a) => entryHTML(a, staticRoot, "archive")).join("");
      bindLqip(els.latest);

      const p = data.pagination || {};
      if (els.pagination) {
        if (p.pages > 1) {
          els.pagination.hidden = false;
          els.pagination.innerHTML = `
            <button type="button" class="mag-page-btn" data-prev ${p.has_prev ? "" : "disabled"} aria-label="صفحه قبل">قبلی</button>
            <span class="mag-page-info" aria-live="polite">${toFa(p.page)} / ${toFa(p.pages)}</span>
            <button type="button" class="mag-page-btn" data-next ${p.has_next ? "" : "disabled"} aria-label="صفحه بعد">بعدی</button>`;
          els.pagination.querySelector("[data-prev]")?.addEventListener("click", () => {
            if (p.has_prev) {
              state.page -= 1;
              loadArticles({ scroll: true });
            }
          });
          els.pagination.querySelector("[data-next]")?.addEventListener("click", () => {
            if (p.has_next) {
              state.page += 1;
              loadArticles({ scroll: true });
            }
          });
        } else {
          els.pagination.hidden = true;
        }
      }
    }

    function syncUrl() {
      const u = new URL(location.href);
      ["category", "tag", "sort", "q"].forEach((k) => {
        if (state[k]) u.searchParams.set(k, state[k]);
        else u.searchParams.delete(k);
      });
      if (state.page > 1) u.searchParams.set("page", String(state.page));
      else u.searchParams.delete("page");
      history.replaceState(null, "", u);
    }

    async function loadArticles({ scroll = false } = {}) {
      const params = new URLSearchParams({
        page: String(state.page),
        page_size: "9",
        sort: state.sort,
      });
      if (state.category) params.set("category", state.category);
      if (state.tag) params.set("tag", state.tag);
      if (state.q) params.set("q", state.q);
      els.latest?.setAttribute("aria-busy", "true");
      try {
        const data = await api(`${apiBase}/articles/?${params}`);
        renderLatest(data);
        syncUrl();
        if (scroll) {
          root.querySelector("[data-section-latest]")?.scrollIntoView({
            behavior: REDUCE ? "auto" : "smooth",
            block: "start",
          });
        }
      } catch (err) {
        showError(err.message || "خطا");
      } finally {
        els.latest?.removeAttribute("aria-busy");
      }
    }

    /* Search autocomplete + keyboard */
    let searchTimer = null;
    let searchItems = [];
    let searchIndex = -1;

    function setSearchExpanded(open) {
      els.searchInput?.setAttribute("aria-expanded", open ? "true" : "false");
      if (els.searchDrop) els.searchDrop.hidden = !open;
    }

    function highlightSearch(i) {
      searchItems.forEach((el, idx) => el.classList.toggle("is-focus", idx === i));
    }

    els.searchInput?.addEventListener("input", () => {
      clearTimeout(searchTimer);
      const q = els.searchInput.value.trim();
      searchTimer = setTimeout(async () => {
        if (q.length < 2) {
          setSearchExpanded(false);
          els.searchDrop.innerHTML = "";
          searchItems = [];
          searchIndex = -1;
          return;
        }
        try {
          const data = await api(`${apiBase}/search/?q=${encodeURIComponent(q)}`);
          const parts = [];
          (data.articles || []).forEach((a) => {
            parts.push(
              `<a href="${a.url}" class="mag-search-item" role="option"><strong>${escapeHtml(a.title)}</strong><span>${escapeHtml(a.category?.title || "")}</span></a>`
            );
          });
          (data.categories || []).forEach((c) => {
            parts.push(
              `<button type="button" class="mag-search-item" role="option" data-pick-cat="${escapeAttr(c.slug)}">موضوع: ${escapeHtml(c.title)}</button>`
            );
          });
          (data.tags || []).forEach((t) => {
            parts.push(
              `<button type="button" class="mag-search-item" role="option" data-pick-tag="${escapeAttr(t.slug)}">برچسب: ${escapeHtml(t.title)}</button>`
            );
          });
          if (!parts.length) {
            parts.push(`<p class="mag-search-empty">نتیجه‌ای یافت نشد</p>`);
          }
          els.searchDrop.innerHTML = parts.join("");
          setSearchExpanded(true);
          searchItems = [...els.searchDrop.querySelectorAll(".mag-search-item")];
          searchIndex = -1;

          els.searchDrop.querySelectorAll("[data-pick-cat]").forEach((b) => {
            b.addEventListener("click", () => {
              state.category = b.getAttribute("data-pick-cat") || "";
              state.page = 1;
              setSearchExpanded(false);
              els.catTrack?.querySelectorAll(".mag-topic").forEach((btn) => {
                const on = (btn.getAttribute("data-cat") || "") === state.category;
                btn.classList.toggle("is-active", on);
                btn.setAttribute("aria-pressed", on ? "true" : "false");
              });
              updateFilterStatus();
              loadArticles();
              syncUrl();
            });
          });
          els.searchDrop.querySelectorAll("[data-pick-tag]").forEach((b) => {
            b.addEventListener("click", () => {
              state.tag = b.getAttribute("data-pick-tag") || "";
              state.page = 1;
              setSearchExpanded(false);
              updateFilterStatus();
              loadArticles();
              syncUrl();
            });
          });
        } catch {
          /* ignore */
        }
      }, 220);
    });

    els.searchInput?.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        setSearchExpanded(false);
        return;
      }
      if (e.key === "ArrowDown" && searchItems.length) {
        e.preventDefault();
        searchIndex = Math.min(searchIndex + 1, searchItems.length - 1);
        highlightSearch(searchIndex);
        return;
      }
      if (e.key === "ArrowUp" && searchItems.length) {
        e.preventDefault();
        searchIndex = Math.max(searchIndex - 1, 0);
        highlightSearch(searchIndex);
        return;
      }
      if (e.key === "Enter") {
        if (searchIndex >= 0 && searchItems[searchIndex]) {
          e.preventDefault();
          searchItems[searchIndex].click();
          return;
        }
        e.preventDefault();
        state.q = els.searchInput.value.trim();
        state.page = 1;
        setSearchExpanded(false);
        updateFilterStatus();
        loadArticles({ scroll: true });
        syncUrl();
      }
    });

    document.addEventListener("click", (e) => {
      if (!root.querySelector("[data-search-wrap]")?.contains(e.target)) {
        setSearchExpanded(false);
      }
    });

    els.sortBtns?.forEach((btn) => {
      btn.addEventListener("click", () => {
        state.sort = btn.getAttribute("data-filter-sort") || "newest";
        state.page = 1;
        els.sortBtns.forEach((b) => {
          const on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        loadArticles();
        syncUrl();
      });
    });

    els.clearFilters?.addEventListener("click", clearFilters);
    els.retry?.addEventListener("click", () => {
      hideError();
      loadArticles();
    });
    root.querySelector("[data-clear-inline]")?.addEventListener("click", clearFilters);

    // Bind SSR pagination if present
    els.pagination?.querySelector("[data-prev]")?.addEventListener("click", () => {
      if (state.page > 1) {
        state.page -= 1;
        loadArticles({ scroll: true });
      }
    });
    els.pagination?.querySelector("[data-next]")?.addEventListener("click", () => {
      state.page += 1;
      loadArticles({ scroll: true });
    });

    window.addEventListener(
      "scroll",
      () => {
        if (!els.progress) return;
        const h = document.documentElement;
        const max = h.scrollHeight - h.clientHeight;
        const p = max > 0 ? (h.scrollTop / max) * 100 : 0;
        els.progress.style.width = `${p}%`;
      },
      { passive: true }
    );

    bindCategoryClicks();
    bindTagClicks();
    bindLqip(root);
    updateFilterStatus();

    // SSR already painted — only refetch when filters diverge from defaults via interaction.
    // Soft-revalidate archive if URL has non-default filters that match SSR (no flash).
    if (!ssr) {
      loadArticles().catch((err) => showError(err.message || "خطا"));
    }
  }

  /* ═══════════════ ARTICLE ═══════════════ */
  function initArticle(root) {
    const apiBase = root.dataset.apiBase || "/magazine/api";
    const slug = root.dataset.slug;
    const progress = root.querySelector("[data-read-progress]");
    const body = root.querySelector("[data-article-body]");
    const toast = root.querySelector("[data-toast]");
    let completed = false;

    function showToast(msg) {
      if (!toast) return;
      toast.textContent = msg;
      toast.hidden = false;
      clearTimeout(showToast._t);
      showToast._t = setTimeout(() => {
        toast.hidden = true;
      }, 2400);
    }

    bindLqip(root);
    api(`${apiBase}/articles/${slug}/view/`, { method: "POST", body: "{}" }).catch(() => {});

    window.addEventListener(
      "scroll",
      () => {
        if (!progress || !body) return;
        const rect = body.getBoundingClientRect();
        const total = body.offsetHeight - window.innerHeight * 0.35;
        const scrolled = Math.min(Math.max(-rect.top, 0), Math.max(total, 1));
        const pct = (scrolled / Math.max(total, 1)) * 100;
        progress.style.width = `${pct}%`;
        if (!completed && pct >= 88) {
          completed = true;
          api(`${apiBase}/articles/${slug}/complete-read/`, { method: "POST", body: "{}" }).catch(
            () => {}
          );
        }
      },
      { passive: true }
    );

    const likeBtn = root.querySelector("[data-like-btn]");
    const bookmarkBtn = root.querySelector("[data-bookmark-btn]");

    likeBtn?.addEventListener("click", async () => {
      try {
        const data = await api(`${apiBase}/articles/${slug}/like/`, {
          method: "POST",
          body: "{}",
        });
        likeBtn.setAttribute("aria-pressed", data.liked ? "true" : "false");
        const label = likeBtn.querySelector("[data-like-label]");
        if (label) label.textContent = data.liked ? "پسندیده‌اید" : "پسندیدن";
        likeBtn.classList.toggle("is-active", !!data.liked);
      } catch (err) {
        showToast(err.message);
      }
    });

    bookmarkBtn?.addEventListener("click", async () => {
      try {
        const data = await api(`${apiBase}/articles/${slug}/bookmark/`, {
          method: "POST",
          body: "{}",
        });
        bookmarkBtn.setAttribute("aria-pressed", data.bookmarked ? "true" : "false");
        const label = bookmarkBtn.querySelector("[data-bookmark-label]");
        if (label) label.textContent = data.bookmarked ? "ذخیره شد" : "ذخیره";
        bookmarkBtn.classList.toggle("is-active", !!data.bookmarked);
        showToast(data.bookmarked ? "مقاله ذخیره شد" : "از ذخیره‌ها حذف شد");
      } catch (err) {
        showToast(err.message);
      }
    });

    root.querySelector("[data-print-btn]")?.addEventListener("click", () => window.print());

    root.querySelectorAll("[data-share-ch]").forEach((el) => {
      el.addEventListener("click", () => {
        const ch = el.getAttribute("data-share-ch") || "";
        api(`${apiBase}/articles/${slug}/share/`, {
          method: "POST",
          body: JSON.stringify({ channel: ch }),
        }).catch(() => {});
      });
    });

    root.querySelector("[data-copy-link]")?.addEventListener("click", async (e) => {
      const url = e.currentTarget.getAttribute("data-url") || location.href;
      try {
        await navigator.clipboard.writeText(url);
        showToast("لینک کپی شد");
        api(`${apiBase}/articles/${slug}/share/`, {
          method: "POST",
          body: JSON.stringify({ channel: "copy" }),
        }).catch(() => {});
      } catch {
        showToast("کپی لینک ممکن نشد");
      }
    });

    /* Editorial feedback (replaces stars) */
    const feedbackRoot = root.querySelector("[data-feedback]");
    const thanks = root.querySelector("[data-feedback-thanks]");
    root.querySelectorAll("[data-feedback]").forEach((btn) => {
      if (!btn.hasAttribute("data-feedback") || btn.tagName !== "BUTTON") return;
    });
    feedbackRoot?.querySelectorAll("button[data-feedback]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const feedback = btn.getAttribute("data-feedback") || "";
        try {
          await api(`${apiBase}/articles/${slug}/rate/`, {
            method: "POST",
            body: JSON.stringify({ feedback }),
          });
          feedbackRoot.querySelectorAll("button[data-feedback]").forEach((b) => {
            const on = b === btn;
            b.classList.toggle("is-active", on);
            b.setAttribute("aria-pressed", on ? "true" : "false");
          });
          if (thanks) thanks.hidden = false;
        } catch (err) {
          showToast(err.message);
        }
      });
    });

    if (root.dataset.liked === "1") likeBtn?.classList.add("is-active");
    if (root.dataset.bookmarked === "1") bookmarkBtn?.classList.add("is-active");
    if (root.dataset.userRating === "5" || root.dataset.userRating === "1") {
      if (thanks) thanks.hidden = false;
    }

    const tocLinks = root.querySelectorAll("[data-toc-list] a");
    if (tocLinks.length && "IntersectionObserver" in window) {
      const map = new Map();
      tocLinks.forEach((a) => {
        const id = a.getAttribute("href")?.slice(1);
        const el = id && document.getElementById(id);
        if (el) map.set(el, a);
      });
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((en) => {
            if (en.isIntersecting) {
              tocLinks.forEach((l) => l.classList.remove("is-active"));
              map.get(en.target)?.classList.add("is-active");
            }
          });
        },
        { rootMargin: "-20% 0px -65% 0px", threshold: 0 }
      );
      map.forEach((_, el) => io.observe(el));
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    const hub = document.querySelector("[data-magazine-hub]");
    if (hub) initHub(hub);
    const article = document.querySelector("[data-magazine-article]");
    if (article) initArticle(article);
  });
})();
