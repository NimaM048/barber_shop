/**
 * Booking wizard — component-based state machine.
 * All schedule data comes from the API; nothing is hardcoded.
 */
(() => {
  "use strict";

  const STEPS = [1, 2, 3, 4, 5, "success"];

  const DRAFT_KEY = "sa_booking_draft_v1";
  const FIRST_VISIT_KEY = "sa_booking_seen_services";
  const DEFAULT_UI = {
    error_fetch: "خطا در دریافت اطلاعات",
    error_book: "خطا در ثبت رزرو",
    success_book: "رزرو با موفقیت ثبت شد",
    error_guide_ack: "برای ثبت نهایی باید راهنما را تأیید کنید",
    success_copy: "اطلاعات رزرو کپی شد",
    error_copy: "امکان کپی وجود ندارد",
    error_form: "لطفاً اطلاعات را اصلاح کنید",
    success_resume: "ادامه رزرو از جایی که رها کردید",
    capacity_changed:
      "ظرفیت این نوبت تغییر کرده است؛ لطفاً ساعت دیگری انتخاب کنید.",
    service_label_fallback: "خدمت تخصصی",
    service_select_cta: "انتخاب",
  };

  const state = {
    step: 1,
    services: [],
    service: null,
    calendar: null,
    calYear: null,
    calMonth: null,
    selectedDate: null,
    selectedDateMeta: null,
    slots: [],
    slotsMeta: null,
    selectedSlot: null,
    form: { first_name: "", last_name: "", phone: "", notes: "" },
    booking: null,
    submitting: false,
    guideSummary: null,
    guideAck: false,
    consultGate: null,
    consultGateSkipped: false,
    ui: { ...DEFAULT_UI },
  };

  const els = {};

  function qs(sel, root = document) {
    return root.querySelector(sel);
  }

  function qsa(sel, root = document) {
    return [...root.querySelectorAll(sel)];
  }

  function toPersianDigits(value) {
    return String(value).replace(/\d/g, (digit) => "۰۱۲۳۴۵۶۷۸۹"[digit]);
  }

  function csrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    if (match) return decodeURIComponent(match[1]);
    const input = qs("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function staticUrl(path) {
    if (!path) return "";
    const base = els.app?.dataset.static || "/static/";
    return base.replace(/\/?$/, "/") + path.replace(/^\//, "");
  }

  function apiServicesUrl() {
    return els.app.dataset.apiBase;
  }

  function apiBookUrl() {
    return els.app.dataset.bookUrl;
  }

  function serviceBase(key) {
    // /appointments/api/services/ → /appointments/api/services/<key>/
    const base = apiServicesUrl().replace(/\/?$/, "/");
    return `${base}${encodeURIComponent(key)}/`;
  }

  function ui(key, fallback = "") {
    return state.ui[key] || DEFAULT_UI[key] || fallback;
  }

  function loadUiConfig() {
    const raw = els.app?.dataset.uiConfig;
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw);
      state.ui = { ...DEFAULT_UI, ...parsed };
    } catch {
      state.ui = { ...DEFAULT_UI };
    }
  }

  async function apiGet(url) {
    const res = await fetch(url, {
      headers: { Accept: "application/json" },
      credentials: "same-origin",
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      throw new Error(data.error || ui("error_fetch"));
    }
    return data;
  }

  async function apiPost(url, body) {
    const res = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken(),
      },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) {
      const error = new Error(data.error || ui("error_book"));
      error.status = res.status;
      throw error;
    }
    return data;
  }

  function toast(message, type = "info") {
    const host = els.toastHost;
    if (!host) return;
    const el = document.createElement("div");
    el.className = `booking-toast${type === "error" ? " is-error" : ""}${type === "success" ? " is-success" : ""}`;
    el.textContent = message;
    host.appendChild(el);
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transition = "opacity 0.35s ease";
      setTimeout(() => el.remove(), 400);
    }, 3200);
  }

  function setLoading(on) {
    if (!els.loading) return;
    els.loading.hidden = !on;
  }

  function updateStepper() {
    const stepNum =
      state.step === "success"
        ? 6
        : state.step === "consult"
          ? 1
          : state.step;
    qsa("[data-step-indicator]").forEach((item) => {
      const n = Number(item.dataset.stepIndicator);
      const active = n === stepNum && state.step !== "consult";
      item.classList.toggle("is-active", active);
      item.classList.toggle("is-done", n < stepNum || (state.step === "consult" && n === 1));
      if (active) item.setAttribute("aria-current", "step");
      else item.removeAttribute("aria-current");
    });
    qsa(".booking-step-line").forEach((line, idx) => {
      line.classList.toggle("is-done", idx + 1 < stepNum);
    });

    const stepper = qs("[data-booking-stepper]");
    if (stepper) {
      stepper.classList.toggle("is-gate", state.step === "consult");
      stepper.hidden = state.step === "success";
      stepper.setAttribute("aria-hidden", state.step === "success" ? "true" : "false");
    }

    const intro = qs(".booking-intro");
    if (intro) {
      intro.hidden = state.step === "success";
    }
  }

  function saveDraft() {
    try {
      const payload = {
        serviceKey: state.service?.key || "",
        consultGateSkipped: state.consultGateSkipped,
        selectedDate: state.selectedDate,
        selectedDateMeta: state.selectedDateMeta,
        selectedSlot: state.selectedSlot,
        form: state.form,
        step: state.step === "consult" ? 2 : state.step,
        savedAt: Date.now(),
      };
      sessionStorage.setItem(DRAFT_KEY, JSON.stringify(payload));
    } catch {
      /* ignore */
    }
  }

  function loadDraft() {
    try {
      const raw = sessionStorage.getItem(DRAFT_KEY);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  function clearDraft() {
    try {
      sessionStorage.removeItem(DRAFT_KEY);
    } catch {
      /* ignore */
    }
  }

  function seenServices() {
    try {
      return JSON.parse(localStorage.getItem(FIRST_VISIT_KEY) || "[]");
    } catch {
      return [];
    }
  }

  function markServiceSeen(key) {
    const list = seenServices();
    if (!list.includes(key)) {
      list.push(key);
      try {
        localStorage.setItem(FIRST_VISIT_KEY, JSON.stringify(list));
      } catch {
        /* storage can be unavailable in private/restricted contexts */
      }
    }
  }

  function isFirstVisit(key) {
    return !seenServices().includes(key);
  }

  async function fetchConsultGate(serviceKey) {
    const base =
      els.app?.dataset.guideSummaryBase || "/consultations/api/booking-summary/";
    const data = await apiGet(
      `${base.replace(/\/?$/, "/")}${encodeURIComponent(serviceKey)}/`
    );
    return data.summary || null;
  }

  function renderConsultGate(summary) {
    const gate = summary?.gate || {};
    const setText = (sel, value) => {
      const el = qs(sel);
      if (el && value) el.textContent = value;
    };
    setText("[data-gate-eyebrow]", gate.eyebrow);
    setText("[data-gate-title]", gate.title);
    setText("[data-gate-body]", gate.body);
    setText("[data-gate-primary-kicker]", gate.primary_kicker);
    setText("[data-gate-primary-label]", gate.primary_cta);
    setText("[data-gate-primary-desc]", gate.primary_desc);
    setText("[data-gate-primary-cta]", gate.primary_cta_suffix);
    setText("[data-gate-secondary-label]", gate.secondary_cta);
    setText("[data-gate-secondary-desc]", gate.secondary_desc);

    const first = qs("[data-gate-first]");
    if (first) {
      const show = isFirstVisit(state.service.key);
      first.hidden = !show;
      if (show) {
        setText("[data-gate-first-title]", gate.first_visit_title);
        setText("[data-gate-first-body]", gate.first_visit_body);
      }
    }
  }

  async function proceedToCalendar() {
    state.consultGateSkipped = true;
    markServiceSeen(state.service.key);
    const sub = qs("[data-step2-sub]");
    if (sub && state.service) {
      sub.textContent = `${state.service.name} · ${state.service.duration_display || state.service.duration_minutes} دقیقه · ${state.service.start_time_display} تا ${state.service.end_time_display}`;
    }
    const title = qs("[data-step2-title]");
    if (title && state.service) title.textContent = `تاریخ — ${state.service.name}`;
    showStep(2);
    await loadCalendar();
  }

  function goToConsultation() {
    if (!state.service || !state.consultGate) return;
    markServiceSeen(state.service.key);
    state.consultGateSkipped = false;
    saveDraft();
    const catKey = state.consultGate.category?.key;
    if (!catKey) return;
    const url = `/consultations/${encodeURIComponent(catKey)}/?from=booking&service=${encodeURIComponent(state.service.key)}`;
    window.location.href = url;
  }

  function prefersReducedMotion() {
    return window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  }

  function focusActiveStep(panel) {
    if (!panel) return;
    const target = panel.querySelector("h1, h2, [data-step-focus]");
    if (!target) return;
    target.setAttribute("tabindex", "-1");
    requestAnimationFrame(() => target.focus({ preventScroll: true }));
  }

  function showStep(step, { focus = true } = {}) {
    state.step = step;
    let activePanel = null;
    qsa("[data-booking-step]").forEach((panel) => {
      const id = panel.dataset.bookingStep;
      const match = String(id) === String(step);
      panel.hidden = !match;
      if (match) activePanel = panel;
    });
    updateStepper();
    window.scrollTo({ top: 0, behavior: prefersReducedMotion() ? "auto" : "smooth" });
    if (focus) focusActiveStep(activePanel);
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /* ─── Step 1: Services ─── */
  function renderServices() {
    const grid = els.serviceGrid;
    const empty = qs("[data-services-empty]");
    const err = qs("[data-services-error]");
    if (!grid) return;

    grid.innerHTML = "";
    if (empty) empty.hidden = true;
    if (err) err.hidden = true;

    if (!state.services.length) {
      if (empty) empty.hidden = false;
      return;
    }

    state.services.forEach((svc, i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "booking-service-row";
      btn.dataset.serviceKey = svc.key || svc.slug || "";
      btn.setAttribute("aria-pressed", "false");
      btn.style.animationDelay = `${i * 0.05}s`;
      btn.setAttribute(
        "aria-label",
        `انتخاب ${svc.name}، حدود ${svc.duration_display || svc.duration_minutes} دقیقه`
      );
      const img = svc.image_webp || svc.image_jpg;
      const jpg = svc.image_jpg || svc.image_webp;
      const serviceLabel =
        svc.card_label || svc.label || ui("service_label_fallback");
      btn.innerHTML = `
        <div class="booking-service-thumb">
          <picture>
            ${svc.image_webp ? `<source srcset="${escapeHtml(staticUrl(svc.image_webp))}" type="image/webp">` : ""}
            <img src="${escapeHtml(staticUrl(jpg || img))}" alt="${escapeHtml(svc.name || "")}" width="120" height="160" loading="${i ? "lazy" : "eager"}" decoding="async">
          </picture>
        </div>
        <div class="booking-service-copy">
          <p class="svc-meta"><span class="svc-index">${toPersianDigits(String(i + 1).padStart(2, "0"))}</span> · ${escapeHtml(serviceLabel)}</p>
          <h3>${escapeHtml(svc.name)}</h3>
          <p class="svc-desc">${escapeHtml(svc.description || "")}</p>
          <p class="svc-duration">حدود ${escapeHtml(svc.duration_display || svc.duration_minutes)} دقیقه</p>
        </div>
        <span class="svc-cta">${escapeHtml(ui("service_select_cta"))} <span aria-hidden="true">←</span></span>
      `;
      btn.addEventListener("click", () => selectService(svc));
      grid.appendChild(btn);
    });
  }

  async function loadServices() {
    setLoading(true);
    qs("[data-services-error]")?.setAttribute("hidden", "");
    try {
      const data = await apiGet(apiServicesUrl());
      state.services = data.services || [];
      renderServices();

      const params = new URLSearchParams(window.location.search);
      if (params.get("resume") === "1") {
        return;
      }

      const pre = (els.app.dataset.preselect || "").trim();
      if (pre) {
        const match = state.services.find(
          (s) => s.key === pre || s.slug === pre
        );
        if (match) {
          await selectService(match);
        }
      }
    } catch (e) {
      const err = qs("[data-services-error]");
      const text = qs("[data-services-error-text]");
      if (text) text.textContent = e.message;
      if (err) err.hidden = false;
      toast(e.message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function selectService(svc, { skipGate = false } = {}) {
    state.service = svc;
    state.selectedDate = null;
    state.selectedSlot = null;
    state.calendar = null;
    state.consultGate = null;
    state.consultGateSkipped = !!skipGate;
    updateAsideSummary();
    qsa(".booking-service-row").forEach((row) => {
      const selected = row.dataset.serviceKey === (svc.key || svc.slug || "");
      row.classList.toggle("is-selected", selected);
      row.setAttribute("aria-pressed", selected ? "true" : "false");
    });
    setLoading(true);

    try {
      if (!skipGate) {
        try {
          const summary = await fetchConsultGate(svc.key);
          if (summary?.gate_required || summary?.gate) {
            state.consultGate = summary;
            renderConsultGate(summary);
            showStep("consult");
            return;
          }
        } catch {
          /* if gate API fails, continue booking */
        }
      }

      await proceedToCalendar();
    } finally {
      setLoading(false);
    }
  }

  /* ─── Step 2: Calendar ─── */
  async function loadCalendar(year, month) {
    if (!state.service) return;
    const cal = els.calendar;
    const loading = qs("[data-cal-loading]");
    if (cal) cal.hidden = true;
    if (loading) loading.hidden = false;

    try {
      let url = `${serviceBase(state.service.key)}calendar/`;
      const params = new URLSearchParams();
      if (year) params.set("year", year);
      if (month) params.set("month", month);
      const qsParams = params.toString();
      if (qsParams) url += `?${qsParams}`;

      const data = await apiGet(url);
      state.calendar = data;
      state.calYear = data.year;
      state.calMonth = data.month;
      renderCalendar();
    } catch (e) {
      toast(e.message, "error");
    } finally {
      if (loading) loading.hidden = true;
      if (cal) cal.hidden = false;
    }
  }

  function renderCalendar() {
    const data = state.calendar;
    if (!data) return;

    const title = qs("[data-cal-title]");
    if (title) title.textContent = data.title;

    const prev = qs("[data-cal-prev]");
    const next = qs("[data-cal-next]");
    if (prev) prev.disabled = !data.prev;
    if (next) next.disabled = !data.next;

    const weekdays = qs("[data-cal-weekdays]");
    if (weekdays) {
      weekdays.innerHTML = (data.weekdays || [])
        .map((w) => `<span>${escapeHtml(w)}</span>`)
        .join("");
    }

    const grid = qs("[data-cal-grid]");
    if (!grid) return;
    grid.setAttribute("aria-label", `روزهای ${data.title || "تقویم"}`);
    grid.innerHTML = "";

    for (let i = 0; i < (data.offset || 0); i++) {
      const filler = document.createElement("span");
      filler.className = "booking-day is-empty";
      filler.setAttribute("aria-hidden", "true");
      grid.appendChild(filler);
    }

    (data.days || []).forEach((day) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `booking-day is-${day.state}`;
      if (day.is_today) btn.classList.add("is-today");
      if (state.selectedDate === day.date) btn.classList.add("is-selected");
      btn.textContent = day.jalali_day_display;
      btn.disabled = !day.selectable;
      const availability = day.selectable
        ? `${day.available_slots || 0} نوبت آزاد`
        : day.state === "full"
          ? "تکمیل"
          : day.state === "closed"
            ? "تعطیل"
            : "غیرقابل انتخاب";
      btn.setAttribute(
        "aria-label",
        `${day.weekday_label} ${day.jalali_day_display} ${data.month_label || ""} ${data.year_display || ""}، ${availability}`.trim()
      );
      btn.setAttribute("aria-pressed", state.selectedDate === day.date ? "true" : "false");
      if (day.selectable) {
        btn.addEventListener("click", () => selectDate(day));
      }
      grid.appendChild(btn);
    });
  }

  async function selectDate(day) {
    state.selectedDate = day.date;
    state.selectedDateMeta = day;
    state.selectedSlot = null;
    updateAsideSummary();
    renderCalendar();

    const sub = qs("[data-step3-sub]");
    if (sub) {
      sub.textContent = `${day.weekday_label}، ${day.jalali_day_display} — ${state.service.name}`;
    }
    showStep(3);
    await loadSlots(day.date);
  }

  /* ─── Step 3: Slots ─── */
  async function loadSlots(dateIso) {
    if (!state.service) return;
    const grid = qs("[data-slots-grid]");
    const loading = qs("[data-slots-loading]");
    const empty = qs("[data-slots-empty]");
    if (grid) grid.innerHTML = "";
    if (empty) empty.hidden = true;
    if (loading) loading.hidden = false;

    try {
      const url = `${serviceBase(state.service.key)}slots/?date=${encodeURIComponent(dateIso)}`;
      const data = await apiGet(url);
      state.slots = data.slots || [];
      state.slotsMeta = data;
      renderSlots();
    } catch (e) {
      toast(e.message, "error");
    } finally {
      if (loading) loading.hidden = true;
    }
  }

  function renderSlots() {
    const grid = qs("[data-slots-grid]");
    const empty = qs("[data-slots-empty]");
    const meta = qs("[data-slots-meta]");
    if (!grid) return;

    grid.innerHTML = "";
    const available = state.slots.filter((s) => s.status === "available");

    if (meta && state.slotsMeta) {
      meta.textContent = state.slotsMeta.date_display
        ? `${state.slotsMeta.weekday_label} ${state.slotsMeta.date_display} · ${available.length} نوبت آزاد`
        : "";
    }

    if (!available.length && !state.slots.some((s) => s.status !== "disabled")) {
      if (empty) empty.hidden = false;
      return;
    }

    if (!state.slots.length) {
      if (empty) empty.hidden = false;
      return;
    }

    state.slots.forEach((slot) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `booking-slot is-${slot.status}`;
      if (
        state.selectedSlot &&
        state.selectedSlot.starts_at === slot.starts_at
      ) {
        btn.classList.add("is-selected");
      }

      const remain =
        slot.status === "available" && slot.capacity > 1
          ? `<span class="slot-remain">${slot.remaining} ظرفیت باقی</span>`
          : slot.status === "available"
            ? `<span class="slot-remain">آزاد</span>`
            : slot.status === "reserved"
              ? `<span class="slot-remain">رزرو شده</span>`
              : `<span class="slot-remain">غیرفعال</span>`;

      btn.innerHTML = `<span>${escapeHtml(slot.start_display)}</span>${remain}`;
      btn.disabled = slot.status !== "available";
      const slotStatus =
        slot.status === "available"
          ? slot.capacity > 1
            ? `${slot.remaining} ظرفیت باقی‌مانده`
            : "آزاد"
          : slot.status === "reserved"
            ? "رزرو شده"
            : "غیرفعال";
      btn.setAttribute("aria-label", `${slot.start_display}، ${slotStatus}`);
      btn.setAttribute(
        "aria-pressed",
        state.selectedSlot?.starts_at === slot.starts_at ? "true" : "false"
      );

      if (slot.status === "available") {
        btn.addEventListener("click", () => selectSlot(slot));
      }
      grid.appendChild(btn);
    });

    if (!available.length && empty) {
      empty.hidden = false;
    }
  }

  function selectSlot(slot) {
    state.selectedSlot = slot;
    updateAsideSummary();
    renderSlots();
    // Soft delay for selection animation, then advance
    setTimeout(() => showStep(4), 220);
  }

  /* ─── Step 4: Form ─── */
  function validateForm() {
    const errors = {};
    const f = state.form;
    const first = (f.first_name || "").trim();
    const last = (f.last_name || "").trim();
    let phone = (f.phone || "").trim();

    const fa = "۰۱۲۳۴۵۶۷۸۹";
    const en = "0123456789";
    phone = phone
      .split("")
      .map((c) => {
        const i = fa.indexOf(c);
        return i >= 0 ? en[i] : c;
      })
      .join("")
      .replace(/[\s\-()]/g, "");
    if (phone.startsWith("+98")) phone = "0" + phone.slice(3);
    if (phone.startsWith("98") && phone.length === 12) phone = "0" + phone.slice(2);

    if (first.length < 2) errors.first_name = "نام باید حداقل ۲ حرف باشد.";
    if (last.length < 2) errors.last_name = "نام خانوادگی باید حداقل ۲ حرف باشد.";
    if (!/^09\d{9}$/.test(phone)) {
      errors.phone = "شماره موبایل معتبر نیست (مثال: ۰۹۱۳xxxxxxx).";
    }

    let firstInvalid = null;
    qsa("[data-error-for]").forEach((el) => {
      const key = el.dataset.errorFor;
      const input = els.form?.elements?.[key];
      if (errors[key]) {
        el.textContent = errors[key];
        el.hidden = false;
        input?.setAttribute("aria-invalid", "true");
        if (!firstInvalid) firstInvalid = input;
      } else {
        el.hidden = true;
        el.textContent = "";
        input?.removeAttribute("aria-invalid");
      }
    });

    if (!Object.keys(errors).length) {
      state.form.phone = phone;
      state.form.first_name = first;
      state.form.last_name = last;
    }

    if (firstInvalid) firstInvalid.focus();
    return Object.keys(errors).length === 0;
  }

  function readForm() {
    const form = els.form;
    if (!form) return;
    state.form.first_name = form.first_name.value;
    state.form.last_name = form.last_name.value;
    state.form.phone = form.phone.value;
    state.form.notes = form.notes.value;
  }

  function restoreForm() {
    const form = els.form;
    if (!form) return;
    form.first_name.value = state.form.first_name || "";
    form.last_name.value = state.form.last_name || "";
    form.phone.value = state.form.phone || "";
    form.notes.value = state.form.notes || "";
  }

  function renderSummary() {
    const box = qs("[data-summary]");
    updateAsideSummary();
    if (!box || !state.service || !state.selectedSlot) return;

    const dateLabel =
      state.slotsMeta?.date_display ||
      state.selectedDateMeta?.jalali_day_display ||
      state.selectedDate;

    const rows = [
      ["سرویس", state.service.name],
      ["تاریخ", `${state.slotsMeta?.weekday_label || ""} ${dateLabel}`.trim()],
      [
        "ساعت",
        `${state.selectedSlot.start_display} تا ${state.selectedSlot.end_display}`,
      ],
      ["نام", `${state.form.first_name} ${state.form.last_name}`.trim()],
      ["تماس", state.form.phone],
    ];
    if (state.form.notes?.trim()) {
      rows.push(["توضیحات", state.form.notes.trim()]);
    }

    box.innerHTML = `<div class="booking-confirm-card-head">
      <span class="booking-confirm-card-kicker">مرور رزرو</span>
      <span class="booking-confirm-card-note">لطفاً اطلاعات را یک‌بار دیگر بررسی کنید</span>
    </div><dl>${rows
      .map(
        ([k, v]) =>
          `<div class="booking-summary-row"><dt>${escapeHtml(k)}</dt><dd>${escapeHtml(v)}</dd></div>`
      )
      .join("")}</dl>`;

    loadGuideSummary();
  }

  function updateAsideSummary() {
    const box = qs("[data-booking-summary]");
    if (!box) return;
    if (!state.service) {
      box.innerHTML = `<p class="booking-summary-empty">هنوز سرویسی انتخاب نشده است.</p>`;
      return;
    }
    const rows = [["سرویس", state.service.name]];
    if (state.service.duration_display || state.service.duration_minutes) {
      rows.push([
        "مدت",
        state.service.duration_display || `${state.service.duration_minutes} دقیقه`,
      ]);
    }
    if (state.selectedDate) {
      const dateLabel =
        state.slotsMeta?.date_display ||
        state.selectedDateMeta?.jalali_day_display ||
        state.selectedDate;
      rows.push([
        "تاریخ",
        `${state.slotsMeta?.weekday_label || state.selectedDateMeta?.weekday_label || ""} ${dateLabel}`.trim(),
      ]);
    }
    if (state.selectedSlot) {
      rows.push([
        "ساعت",
        `${state.selectedSlot.start_display} تا ${state.selectedSlot.end_display}`,
      ]);
    }
    box.innerHTML = `<dl>${rows
      .map(
        ([k, v]) =>
          `<div class="booking-summary-row"><dt>${escapeHtml(k)}</dt><dd>${escapeHtml(v)}</dd></div>`
      )
      .join("")}</dl>`;
  }

  async function loadGuideSummary() {
    const wrap = qs("[data-booking-guide]");
    const btn = qs("[data-confirm-book]");
    if (!wrap || !state.service) return;

    state.guideSummary = null;
    state.guideAck = false;
    wrap.hidden = true;
    const ack = qs("[data-guide-ack]");
    if (ack) ack.checked = false;
    const ackErr = qs("[data-guide-ack-error]");
    if (ackErr) ackErr.hidden = true;

    const base = els.app?.dataset.guideSummaryBase || "/consultations/api/booking-summary/";
    try {
      const data = await apiGet(
        `${base.replace(/\/?$/, "/")}${encodeURIComponent(state.service.key)}/`
      );
      if (!data.summary) {
        if (btn) btn.disabled = false;
        return;
      }
      state.guideSummary = data.summary;
      renderGuideSummary(data.summary);
      wrap.hidden = false;
      if (btn) btn.disabled = true;
    } catch {
      // Guide is optional if API fails — allow booking
      if (btn) btn.disabled = false;
    }
  }

  function renderGuideSummary(summary) {
    const list = qs("[data-guide-highlights]");
    const alerts = qs("[data-guide-alerts]");
    const link = qs("[data-guide-link]");
    const label = qs("[data-guide-ack-label]");
    const heading = qs("[data-guide-heading]");
    const ackErr = qs("[data-guide-ack-error]");

    if (heading && summary.confirm_guide_heading) {
      heading.textContent = summary.confirm_guide_heading;
    }
    if (link && summary.guide_url) {
      link.href = summary.guide_url;
    }
    if (link && summary.confirm_guide_link_label) {
      link.textContent = summary.confirm_guide_link_label;
    }
    if (label && summary.acknowledgment_label) {
      label.textContent = summary.acknowledgment_label;
    }
    if (ackErr && summary.acknowledgment_error) {
      ackErr.textContent = summary.acknowledgment_error;
    }

    if (list) {
      list.innerHTML = (summary.highlights || [])
        .slice(0, 5)
        .map(
          (t) =>
            `<li><span class="booking-guide-dot" aria-hidden="true"></span><span><strong>${escapeHtml(t.title)}</strong> — ${escapeHtml(t.description)}</span></li>`
        )
        .join("");
    }

    if (alerts) {
      alerts.innerHTML = (summary.alerts || [])
        .map(
          (a) =>
            `<div class="booking-guide-alert is-${escapeHtml(a.severity)}"><span aria-hidden="true">${escapeHtml(a.icon)}</span> ${escapeHtml(a.message)}</div>`
        )
        .join("");
    }
  }

  function syncConfirmEnabled() {
    const btn = qs("[data-confirm-book]");
    if (!btn) return;
    if (state.guideSummary?.acknowledgment_required) {
      btn.disabled = !state.guideAck || state.submitting;
    } else {
      btn.disabled = state.submitting;
    }
  }

  /* ─── Step 5 / Success ─── */
  async function confirmBooking() {
    if (state.submitting) return;
    if (!state.service || !state.selectedSlot) return;

    if (state.guideSummary?.acknowledgment_required && !state.guideAck) {
      const ackErr = qs("[data-guide-ack-error]");
      if (ackErr) ackErr.hidden = false;
      toast(ui("error_guide_ack"), "error");
      return;
    }

    state.submitting = true;
    const btn = qs("[data-confirm-book]");
    const label = qs("[data-confirm-label]");
    if (btn) btn.disabled = true;
    if (label) label.textContent = "در حال ثبت…";

    try {
      const data = await apiPost(apiBookUrl(), {
        service_key: state.service.key,
        starts_at: state.selectedSlot.starts_at,
        first_name: state.form.first_name,
        last_name: state.form.last_name,
        phone: state.form.phone,
        notes: state.form.notes || "",
        guide_acknowledged: !!state.guideAck || !state.guideSummary,
      });
      state.booking = data.booking;
      renderSuccess();
      showStep("success");
      clearDraft();
      toast(ui("success_book"), "success");
    } catch (e) {
      if (e.status === 409 && state.selectedDate) {
        state.selectedSlot = null;
        await loadSlots(state.selectedDate);
        showStep(3);
        toast(ui("capacity_changed"), "error");
      } else {
        toast(e.message, "error");
        if (state.selectedDate) {
          await loadSlots(state.selectedDate);
        }
      }
    } finally {
      state.submitting = false;
      if (label) label.textContent = "ثبت نهایی";
      syncConfirmEnabled();
    }
  }

  function renderSuccess() {
    const card = qs("[data-success-card]");
    const b = state.booking;
    if (!card || !b) return;

    const rows = [
      ["کد رزرو", b.booking_code],
      ["سرویس", b.service_name],
      ["تاریخ", b.date_display],
      ["ساعت", `${b.start_time_display} تا ${b.end_time_display}`],
      ["نام", b.full_name],
      ["تماس", b.phone_display || b.phone],
    ];

    card.innerHTML = `<dl>${rows
      .map(
        ([k, v]) =>
          `<div class="booking-summary-row"><dt>${escapeHtml(k)}</dt><dd dir="auto">${escapeHtml(v)}</dd></div>`
      )
      .join("")}</dl>`;
  }

  function shareBooking() {
    const b = state.booking;
    if (!b) return;
    const text = [
      `رزرو ${b.service_name}`,
      `کد: ${b.booking_code}`,
      `تاریخ: ${b.date_display}`,
      `ساعت: ${b.start_time_display}`,
      `نام: ${b.full_name}`,
    ].join("\n");

    if (navigator.share) {
      navigator.share({ title: "رزرو نوبت", text }).catch(() => {});
      return;
    }
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(text).then(
        () => toast(ui("success_copy"), "success"),
        () => toast(ui("error_copy"), "error")
      );
    }
  }

  function resetBooking() {
    state.step = 1;
    state.service = null;
    state.calendar = null;
    state.selectedDate = null;
    state.selectedDateMeta = null;
    state.slots = [];
    state.slotsMeta = null;
    state.selectedSlot = null;
    state.form = { first_name: "", last_name: "", phone: "", notes: "" };
    state.booking = null;
    state.guideSummary = null;
    state.guideAck = false;
    restoreForm();
    updateAsideSummary();
    showStep(1, { focus: false });
    renderServices();
  }

  function goBack() {
    if (state.step === "consult") {
      showStep(1);
      return;
    }
    if (state.step === 2) {
      if (state.consultGate) {
        showStep("consult");
      } else {
        showStep(1);
      }
      return;
    }
    if (state.step === 3) {
      showStep(2);
      return;
    }
    if (state.step === 4) {
      restoreForm();
      showStep(3);
      return;
    }
    if (state.step === 5) {
      restoreForm();
      showStep(4);
    }
  }

  function bindEvents() {
    els.app.addEventListener("click", (e) => {
      const t = e.target.closest("[data-back]");
      if (t) {
        e.preventDefault();
        goBack();
      }
    });

    qs("[data-retry-services]")?.addEventListener("click", loadServices);

    qs("[data-cal-prev]")?.addEventListener("click", () => {
      if (!state.calendar?.prev) return;
      loadCalendar(state.calendar.prev.year, state.calendar.prev.month);
    });
    qs("[data-cal-next]")?.addEventListener("click", () => {
      if (!state.calendar?.next) return;
      loadCalendar(state.calendar.next.year, state.calendar.next.month);
    });

    els.form?.addEventListener("submit", (e) => {
      e.preventDefault();
      readForm();
      if (!validateForm()) {
        toast(ui("error_form"), "error");
        return;
      }
      renderSummary();
      showStep(5);
    });

    // Persist form fields as user types and clear stale field errors as they are corrected.
    els.form?.addEventListener("input", (event) => {
      if (event.target?.name === "phone") {
        event.target.value = event.target.value.slice(0, 11);
      }
      readForm();
      const field = event.target;
      if (!field?.name) return;
      field.removeAttribute("aria-invalid");
      const error = qs(`[data-error-for="${field.name}"]`, els.form);
      if (error) {
        error.hidden = true;
        error.textContent = "";
      }
    });

    qs("[data-confirm-book]")?.addEventListener("click", confirmBooking);
    qs("[data-share-booking]")?.addEventListener("click", shareBooking);
    qs("[data-booking-reset]")?.addEventListener("click", resetBooking);

    qs("[data-guide-ack]")?.addEventListener("change", (e) => {
      state.guideAck = !!e.target.checked;
      const ackErr = qs("[data-guide-ack-error]");
      if (ackErr) ackErr.hidden = true;
      syncConfirmEnabled();
    });

    qs("[data-gate-continue]")?.addEventListener("click", () => {
      proceedToCalendar();
    });

    qs("[data-gate-consult]")?.addEventListener("click", () => {
      goToConsultation();
    });
  }

  async function resumeFromDraft() {
    const params = new URLSearchParams(window.location.search);
    const resume = params.get("resume") === "1";
    const pre = (els.app.dataset.preselect || params.get("service") || "").trim();
    const draft = loadDraft();

    if (!resume || !draft?.serviceKey) {
      return false;
    }

    const match = state.services.find(
      (s) => s.key === draft.serviceKey || s.slug === draft.serviceKey
    );
    if (!match && !pre) return false;

    const svc =
      match ||
      state.services.find((s) => s.key === pre || s.slug === pre);
    if (!svc) return false;

    state.form = { ...state.form, ...(draft.form || {}) };
    state.consultGateSkipped = true;
    restoreForm();

    await selectService(svc, { skipGate: true });

    // Soft-clean URL
    try {
      const url = new URL(window.location.href);
      url.searchParams.delete("resume");
      window.history.replaceState({}, "", url.pathname + (url.search || ""));
    } catch {
      /* ignore */
    }

    toast(ui("success_resume"), "success");
    return true;
  }

  function cacheElements() {
    els.app = qs("[data-booking-app]");
    if (!els.app) return false;
    els.toastHost = qs("[data-toast-host]");
    els.loading = qs("[data-booking-loading]");
    els.serviceGrid = qs("[data-service-grid]");
    els.calendar = qs("[data-calendar]");
    els.form = qs("[data-booking-form]");
    if (els.form?.elements?.phone) {
      els.form.elements.phone.maxLength = 11;
    }
    return true;
  }

  async function refreshSettings() {
    const url = els.app?.dataset.settingsUrl;
    if (!url) return;
    try {
      const data = await apiGet(url);
      if (data.ui) state.ui = { ...DEFAULT_UI, ...data.ui };
    } catch {
      /* keep SSR ui config */
    }
  }

  function init() {
    if (!cacheElements()) return;
    loadUiConfig();
    bindEvents();
    showStep(1);
    refreshSettings().finally(() => {
      loadServices().then(async () => {
        const resumed = await resumeFromDraft();
        if (resumed) return;
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
