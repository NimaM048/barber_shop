/**
 * Consultation hub + detail — fully data-driven from API.
 */
(() => {
  "use strict";

  const BOOKMARK_KEY = "sa_consult_bookmarks";

  function qs(sel, root = document) {
    return root.querySelector(sel);
  }

  function qsa(sel, root = document) {
    return [...root.querySelectorAll(sel)];
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function staticUrl(base, path) {
    if (!path) return "";
    if (/^https?:\/\//i.test(path) || path.startsWith("/media/")) return path;
    return (base || "/static/").replace(/\/?$/, "/") + String(path).replace(/^\//, "");
  }

  function toast(host, message, type = "info") {
    if (!host) return;
    const el = document.createElement("div");
    el.className = `consult-toast${type === "error" ? " is-error" : ""}${type === "success" ? " is-success" : ""}`;
    el.textContent = message;
    host.appendChild(el);
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transition = "opacity 0.35s ease";
      setTimeout(() => el.remove(), 400);
    }, 3000);
  }

  async function apiGet(url) {
    const res = await fetch(url, {
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      throw new Error(data.error || "خطا در دریافت اطلاعات");
    }
    return data;
  }

  function getBookmarks() {
    try {
      return JSON.parse(localStorage.getItem(BOOKMARK_KEY) || "[]");
    } catch {
      return [];
    }
  }

  function setBookmarks(ids) {
    localStorage.setItem(BOOKMARK_KEY, JSON.stringify(ids));
  }

  function toggleBookmark(id) {
    const ids = getBookmarks();
    const i = ids.indexOf(id);
    if (i >= 0) ids.splice(i, 1);
    else ids.push(id);
    setBookmarks(ids);
    return ids.includes(id);
  }

  /* ─── Hub ─── */
  function initHub() {
    const root = qs("[data-consult-hub]");
    if (!root) return;

    const toastHost = qs("[data-toast-host]", root);
    const grid = qs("[data-hub-grid]", root);
    const loading = qs("[data-hub-loading]", root);
    const empty = qs("[data-hub-empty]", root);
    const err = qs("[data-hub-error]", root);
    const staticBase = root.dataset.static || "/static/";

    function applyHubChrome(hub) {
      if (!hub) return;
      const setText = (sel, value) => {
        const el = qs(sel, root);
        if (el && value) el.textContent = value;
      };
      setText("[data-hub-section-label]", hub.section_label);
      setText("[data-hub-title]", hub.title);
      setText("[data-hub-subtitle]", hub.subtitle);
      setText("[data-hub-empty-text]", hub.empty_message);
      if (hub.document_title) {
        document.title = `${hub.document_title} | ${document.title.split("|").pop()?.trim() || ""}`.trim();
      }
      if (hub.meta_description) {
        const meta = document.querySelector('meta[name="description"]');
        if (meta) meta.setAttribute("content", hub.meta_description);
      }
    }

    function formatCardStats(hub, cat) {
      const tips = cat.tip_count_display || cat.tip_count || "۰";
      const minutes = cat.estimated_read_display || cat.estimated_read_minutes || "۰";
      const tpl = hub?.card_stats_template || "{tips} نکته · حدود {minutes} دقیقه";
      return tpl.replace("{tips}", tips).replace("{minutes}", minutes);
    }

    async function load() {
      if (loading) loading.hidden = false;
      if (grid) grid.hidden = true;
      if (empty) empty.hidden = true;
      if (err) err.hidden = true;

      try {
        const data = await apiGet(root.dataset.apiBase);
        const hub = data.hub || {};
        const cats = data.categories || [];
        applyHubChrome(hub);
        if (!cats.length) {
          if (empty) empty.hidden = false;
          return;
        }
        renderHub(cats, hub);
        if (grid) grid.hidden = false;
      } catch (e) {
        const text = qs("[data-hub-error-text]", root);
        if (text) text.textContent = e.message;
        if (err) err.hidden = false;
        toast(toastHost, e.message, "error");
      } finally {
        if (loading) loading.hidden = true;
      }
    }

    function renderHub(cats, hub) {
      if (!grid) return;
      const cta = hub?.card_cta_label || "مشاهده راهنما";
      const [featured, ...rest] = cats;
      let html = "";
      if (featured) {
        const jpg = featured.image_jpg || featured.image_webp;
        const webp = featured.image_webp;
        const stats = formatCardStats(hub, featured);
        html += `
          <a href="/consultations/${escapeHtml(featured.key)}/" class="consult-feature">
            <div class="consult-feature-media">
              <picture>
                ${webp ? `<source srcset="${escapeHtml(staticUrl(staticBase, webp))}" type="image/webp">` : ""}
                <img src="${escapeHtml(staticUrl(staticBase, jpg))}" alt="${escapeHtml(featured.title || "")}" width="960" height="600" loading="eager" decoding="async">
              </picture>
              <span class="consult-feature-veil" aria-hidden="true"></span>
            </div>
            <div class="consult-feature-copy">
              <p class="consult-hub-meta">${escapeHtml(featured.card_label || featured.icon || "")}</p>
              <h2 class="consult-feature-title">${escapeHtml(featured.title)}</h2>
              <p class="consult-hub-desc">${escapeHtml(featured.short_description || "")}</p>
              <div class="consult-feature-meta-row">
                ${stats ? `<span class="consult-feature-chip">${escapeHtml(stats)}</span>` : ""}
                <span class="consult-hub-cta">${escapeHtml(cta)} <span aria-hidden="true">←</span></span>
              </div>
            </div>
          </a>`;
      }
      if (rest.length) {
        html += `
          <div class="consult-index-wrap">
            <p class="consult-index-label">سایر راهنماها</p>
            <ul class="editorial-index consult-index">` + rest.map((c) => {
          const jpg = c.image_jpg || c.image_webp;
          const webp = c.image_webp;
          return `
            <li>
              <a href="/consultations/${escapeHtml(c.key)}/" class="editorial-index-row consult-index-row">
                <div class="editorial-index-thumb">
                  <picture>
                    ${webp ? `<source srcset="${escapeHtml(staticUrl(staticBase, webp))}" type="image/webp">` : ""}
                    <img src="${escapeHtml(staticUrl(staticBase, jpg))}" alt="${escapeHtml(c.title || "")}" width="200" height="267" loading="lazy" decoding="async">
                  </picture>
                </div>
                <div class="editorial-index-copy">
                  <p class="editorial-index-meta">${escapeHtml(c.card_label || c.icon || "")}</p>
                  <h3 class="editorial-index-title">${escapeHtml(c.title)}</h3>
                  <p class="editorial-index-desc">${escapeHtml(c.short_description || "")}</p>
                </div>
                <span class="editorial-index-action" aria-hidden="true">←</span>
              </a>
            </li>`;
        }).join("") + `</ul>
          </div>`;
      }
      grid.innerHTML = html;
      grid.className = "consult-hub-editorial";
    }

    qs("[data-hub-retry]", root)?.addEventListener("click", load);
    load();
  }

  /* ─── Detail ─── */
  function initDetail() {
    const root = qs("[data-consult-detail]");
    if (!root) return;

    const toastHost = qs("[data-toast-host]", root);
    const loading = qs("[data-detail-loading]", root);
    const detailRoot = qs("[data-detail-root]", root);
    const errBox = qs("[data-detail-error]", root);
    const staticBase = root.dataset.static || "/static/";
    const apiDetail = root.dataset.apiDetail;

    let state = {
      category: null,
      groups: [],
      alerts: [],
      faqs: [],
      q: "",
      group: "",
      highlights: false,
    };

    // Restore scroll after back navigation
    const scrollKey = `sa_consult_scroll_${root.dataset.categoryKey}`;

    async function load() {
      if (loading) loading.hidden = false;
      if (detailRoot) detailRoot.hidden = true;
      if (errBox) errBox.hidden = true;

      try {
        const params = new URLSearchParams();
        if (state.q) params.set("q", state.q);
        if (state.highlights) params.set("highlights", "1");
        // Group chips scroll in-page; do not filter/reload by group
        const url = apiDetail + (params.toString() ? `?${params}` : "");
        const data = await apiGet(url);
        state.category = data.category;
        state.groups = data.groups || [];
        state.alerts = data.alerts || [];
        state.faqs = data.faqs || [];
        renderAll(data);
        if (detailRoot) detailRoot.hidden = false;
        setActiveChip(state.group);

        const saved = sessionStorage.getItem(scrollKey);
        if (saved) {
          requestAnimationFrame(() => {
            window.scrollTo(0, Number(saved) || 0);
            sessionStorage.removeItem(scrollKey);
          });
        }
      } catch (e) {
        const text = qs("[data-detail-error-text]", root);
        if (text) text.textContent = e.message;
        if (errBox) errBox.hidden = false;
        toast(toastHost, e.message, "error");
      } finally {
        if (loading) loading.hidden = true;
      }
    }

    function renderAll(data) {
      renderHero(data.category);
      renderFilters(data.groups || []);
      renderAlerts(data.alerts || []);
      renderGroups(data.groups || [], data.ungrouped_tips || []);
      renderFaq(data.faqs || []);

      const empty = qs("[data-tips-empty]", root);
      if (empty) empty.hidden = (data.result_count || 0) > 0;
    }

    function renderHero(cat) {
      const hero = qs("[data-detail-hero]", root);
      if (!hero || !cat) return;
      document.title = `${cat.title} | مشاوره`;
      const lede = cat.description || cat.short_description || "";
      hero.innerHTML = `
        <p class="section-label">${escapeHtml(cat.card_label || cat.icon || "راهنما")}</p>
        <h1 class="consult-detail-title type-chapter">${escapeHtml(cat.title)}</h1>
        ${lede ? `<p class="consult-detail-lede">${escapeHtml(lede)}</p>` : ""}
        <div class="consult-detail-meta">
          <span class="consult-detail-chip">${escapeHtml(cat.tip_count_display || "۰")} نکته</span>
          <span class="consult-detail-chip">حدود ${escapeHtml(cat.estimated_read_display || "۰")} دقیقه</span>
        </div>
      `;
    }

    function renderFilters(groups) {
      const box = qs("[data-group-filters]", root);
      if (!box) return;
      const allActive = !state.group ? " is-active" : "";
      box.innerHTML =
        `<button type="button" class="consult-chip${allActive}" data-scroll-group="">همه</button>` +
        groups
          .map((g) => {
            const active = state.group === g.key ? " is-active" : "";
            return `<button type="button" class="consult-chip${active}" data-scroll-group="${escapeHtml(g.key)}">${escapeHtml(g.title)}</button>`;
          })
          .join("");
    }

    function setActiveChip(groupKey) {
      state.group = groupKey || "";
      qsa("[data-scroll-group]", root).forEach((chip) => {
        const key = chip.getAttribute("data-scroll-group") || "";
        chip.classList.toggle("is-active", key === state.group);
      });
    }

    function smoothScrollTo(el) {
      if (!el) return;
      const headerOffset = 110;
      const lenis = window.__lenis;
      if (lenis && typeof lenis.scrollTo === "function") {
        lenis.scrollTo(el, {
          offset: -headerOffset,
          duration: 1.35,
          easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        });
        return;
      }
      const top = el.getBoundingClientRect().top + window.scrollY - headerOffset;
      window.scrollTo({ top, behavior: "smooth" });
    }

    function focusGroup(groupKey) {
      setActiveChip(groupKey);

      if (!groupKey) {
        const start = qs("[data-groups]", root) || qs("[data-detail-toolbar]", root);
        smoothScrollTo(start);
        return;
      }

      const section = qs(`[data-group-key="${groupKey}"]`, root);
      if (!section) return;

      qsa(".consult-group.is-focused", root).forEach((s) =>
        s.classList.remove("is-focused")
      );
      section.classList.add("is-focused");
      smoothScrollTo(section);

      window.clearTimeout(focusGroup._timer);
      focusGroup._timer = window.setTimeout(() => {
        section.classList.remove("is-focused");
      }, 1600);
    }

    function renderAlerts(alerts) {
      const box = qs("[data-alerts]", root);
      if (!box) return;
      if (!alerts.length) {
        box.innerHTML = "";
        return;
      }
      box.innerHTML = alerts
        .map(
          (a) => `
        <div class="consult-alert is-${escapeHtml(a.severity)}">
          <span class="consult-alert-icon" aria-hidden="true">${escapeHtml(a.icon)}</span>
          <div>
            <p class="consult-alert-title">${escapeHtml(a.title)}</p>
            <p class="consult-alert-msg">${escapeHtml(a.message)}</p>
          </div>
        </div>`
        )
        .join("");
    }

    function tipCard(tip, index) {
      const bookmarks = getBookmarks();
      const bookmarked = bookmarks.includes(tip.id);
      const media = [];
      if (tip.video_url) {
        media.push(
          `<a class="consult-media-link" href="${escapeHtml(tip.video_url)}" target="_blank" rel="noopener">ویدئو</a>`
        );
      }
      if (tip.pdf_url) {
        media.push(
          `<a class="consult-media-link" href="${escapeHtml(tip.pdf_url)}" target="_blank" rel="noopener">PDF</a>`
        );
      }
      if (tip.audio_url) {
        media.push(
          `<a class="consult-media-link" href="${escapeHtml(tip.audio_url)}" target="_blank" rel="noopener">صوت</a>`
        );
      }
      if (tip.external_link) {
        media.push(
          `<a class="consult-media-link" href="${escapeHtml(tip.external_link)}" target="_blank" rel="noopener">بیشتر</a>`
        );
      }

      const img = tip.image
        ? `<div class="consult-tip-media media-frame media-frame--landscape"><img src="${escapeHtml(staticUrl(staticBase, tip.image))}" alt="${escapeHtml(tip.title || "")}" width="960" height="600" loading="lazy" decoding="async"></div>`
        : "";

      return `
        <article class="consult-tip${tip.is_highlight ? " is-highlight" : ""}" data-tip-id="${tip.id}" style="animation-delay:${Math.min(index, 8) * 0.05}s">
          <div class="consult-tip-top">
            <span class="consult-tip-index" aria-hidden="true">${String(index + 1).padStart(2, "0")}</span>
            <div class="consult-tip-actions">
              ${tip.is_highlight ? `<span class="consult-tip-badge">مهم</span>` : ""}
              <button type="button" class="consult-icon-btn${bookmarked ? " is-on" : ""}" data-bookmark="${tip.id}" aria-label="نشان‌گذاری" aria-pressed="${bookmarked ? "true" : "false"}">★</button>
              <button type="button" class="consult-icon-btn" data-share-tip="${tip.id}" aria-label="اشتراک">↗</button>
            </div>
          </div>
          <h3 class="consult-tip-title">${escapeHtml(tip.title)}</h3>
          <p class="consult-tip-body">${escapeHtml(tip.description)}</p>
          ${img}
          ${media.length ? `<div class="consult-tip-links">${media.join("")}</div>` : ""}
        </article>`;
    }

    function renderGroups(groups, ungrouped) {
      const box = qs("[data-groups]", root);
      if (!box) return;
      let html = "";
      let idx = 0;
      groups.forEach((g) => {
        if (!g.tips || !g.tips.length) return;
        html += `
          <section class="consult-group" id="consult-group-${escapeHtml(g.key)}" data-group-key="${escapeHtml(g.key)}" data-phase="${escapeHtml(g.phase)}">
            <div class="consult-group-head">
              <p class="section-label">${escapeHtml(g.phase_label || "")}</p>
              <h2 class="consult-group-title">${escapeHtml(g.title)}</h2>
              ${g.description ? `<p class="consult-group-desc">${escapeHtml(g.description)}</p>` : ""}
            </div>
            <div class="consult-tip-grid">
              ${g.tips.map((t) => tipCard(t, idx++)).join("")}
            </div>
          </section>`;
      });
      if (ungrouped.length) {
        html += `
          <section class="consult-group">
            <div class="consult-group-head">
              <p class="section-label">مکمل</p>
              <h2 class="consult-group-title">سایر نکات</h2>
            </div>
            <div class="consult-tip-grid">
              ${ungrouped.map((t) => tipCard(t, idx++)).join("")}
            </div>
          </section>`;
      }
      box.innerHTML = html;
    }

    function renderFaq(faqs) {
      const section = qs("[data-faq-section]", root);
      const list = qs("[data-faq-list]", root);
      if (!section || !list) return;
      if (!faqs.length) {
        section.hidden = true;
        return;
      }
      section.hidden = false;
      list.innerHTML = faqs
        .map(
          (f, i) => `
        <div class="consult-acc-item${i === 0 ? "" : ""}">
          <button type="button" class="consult-acc-btn" aria-expanded="false">
            <span>${escapeHtml(f.question)}</span>
            <span class="consult-acc-plus" aria-hidden="true">+</span>
          </button>
          <div class="consult-acc-panel" hidden>
            <p>${escapeHtml(f.answer)}</p>
          </div>
        </div>`
        )
        .join("");
    }

    // Events
    let searchTimer;
    qs("[data-search-input]", root)?.addEventListener("input", (e) => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        state.q = e.target.value.trim();
        load();
      }, 280);
    });

    qs("[data-highlights-only]", root)?.addEventListener("change", (e) => {
      state.highlights = e.target.checked;
      load();
    });

    root.addEventListener("click", (e) => {
      const chip = e.target.closest("[data-scroll-group]");
      if (chip) {
        e.preventDefault();
        focusGroup(chip.getAttribute("data-scroll-group") || "");
        return;
      }

      const clear = e.target.closest("[data-clear-filters]");
      if (clear) {
        state.q = "";
        state.group = "";
        state.highlights = false;
        const input = qs("[data-search-input]", root);
        if (input) input.value = "";
        const hl = qs("[data-highlights-only]", root);
        if (hl) hl.checked = false;
        setActiveChip("");
        load();
        return;
      }

      const bm = e.target.closest("[data-bookmark]");
      if (bm) {
        const id = Number(bm.getAttribute("data-bookmark"));
        const on = toggleBookmark(id);
        bm.classList.toggle("is-on", on);
        toast(toastHost, on ? "نشان شد" : "از نشان‌ها حذف شد", "success");
        return;
      }

      const shareTip = e.target.closest("[data-share-tip]");
      if (shareTip) {
        const card = shareTip.closest("[data-tip-id]");
        const title = card?.querySelector(".consult-tip-title")?.textContent || "";
        const desc = card?.querySelector(".consult-tip-body")?.textContent || "";
        const text = `${title}\n${desc}\n${location.href}`;
        if (navigator.share) {
          navigator.share({ title, text }).catch(() => {});
        } else if (navigator.clipboard?.writeText) {
          navigator.clipboard.writeText(text).then(() =>
            toast(toastHost, "کپی شد", "success")
          );
        }
        return;
      }

      const accBtn = e.target.closest(".consult-acc-btn");
      if (accBtn) {
        const item = accBtn.closest(".consult-acc-item");
        const panel = item?.querySelector(".consult-acc-panel");
        const open = accBtn.getAttribute("aria-expanded") === "true";
        qsa(".consult-acc-btn", root).forEach((b) => {
          b.setAttribute("aria-expanded", "false");
          const p = b.parentElement?.querySelector(".consult-acc-panel");
          if (p) p.hidden = true;
          b.querySelector(".consult-acc-plus") &&
            (b.querySelector(".consult-acc-plus").textContent = "+");
        });
        if (!open && panel) {
          accBtn.setAttribute("aria-expanded", "true");
          panel.hidden = false;
          const plus = accBtn.querySelector(".consult-acc-plus");
          if (plus) plus.textContent = "−";
        }
        return;
      }

      if (e.target.closest("[data-share-guide]")) {
        const text = `${state.category?.title || "راهنما"}\n${location.href}`;
        if (navigator.share) {
          navigator.share({ title: state.category?.title, text, url: location.href }).catch(() => {});
        } else if (navigator.clipboard?.writeText) {
          navigator.clipboard.writeText(text).then(() =>
            toast(toastHost, "لینک کپی شد", "success")
          );
        }
        return;
      }

      if (e.target.closest("[data-print-guide]")) {
        window.print();
        return;
      }

      if (e.target.closest("[data-open-ticket]")) {
        const sec = qs("[data-ticket-section]", root);
        if (sec) {
          sec.hidden = false;
          sec.scrollIntoView({ behavior: "smooth", block: "start" });
        }
        return;
      }

      if (e.target.closest("[data-close-ticket]")) {
        const sec = qs("[data-ticket-section]", root);
        if (sec) sec.hidden = true;
      }
    });

    function csrfToken() {
      const match = document.cookie.match(/csrftoken=([^;]+)/);
      return match ? decodeURIComponent(match[1]) : "";
    }

    qs("[data-ticket-form]", root)?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = e.target;
      const btnLabel = qs("[data-ticket-submit-label]", root);
      const fd = new FormData(form);
      if (!fd.get("category_key")) {
        fd.set("category_key", root.dataset.categoryKey || "");
      }
      if (root.dataset.fromBooking === "1") {
        fd.set("source", "booking");
      }
      if (root.dataset.bookingService) {
        fd.set("booking_service_key", root.dataset.bookingService);
      }

      if (btnLabel) btnLabel.textContent = "در حال ارسال…";
      try {
        const res = await fetch(root.dataset.ticketUrl || "/consultations/api/tickets/", {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "X-CSRFToken": csrfToken(),
            Accept: "application/json",
          },
          body: fd,
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || data.ok === false) {
          throw new Error(data.error || "ارسال تیکت ناموفق بود");
        }
        toast(toastHost, data.ticket?.message || "تیکت ثبت شد", "success");
        form.reset();
        const sec = qs("[data-ticket-section]", root);
        if (sec) sec.hidden = true;
      } catch (err) {
        toast(toastHost, err.message, "error");
      } finally {
        if (btnLabel) btnLabel.textContent = "ارسال تیکت";
      }
    });

    // Save scroll when leaving to hub links inside tips
    window.addEventListener("pagehide", () => {
      sessionStorage.setItem(scrollKey, String(window.scrollY));
    });

    // Reading progress
    const bar = qs("[data-read-progress-bar]", root);
    window.addEventListener(
      "scroll",
      () => {
        if (!bar) return;
        const doc = document.documentElement;
        const max = doc.scrollHeight - doc.clientHeight;
        const pct = max > 0 ? (window.scrollY / max) * 100 : 0;
        bar.style.width = `${Math.min(100, Math.max(0, pct))}%`;
      },
      { passive: true }
    );

    load();
  }

  function init() {
    initHub();
    initDetail();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
