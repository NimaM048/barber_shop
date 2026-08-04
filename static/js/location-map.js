/**
 * Location map — local Leaflet + dark court skin + copy UX
 * Prefers self-hosted Leaflet so CDN blocks never force a white Google embed.
 */
(() => {
  "use strict";

  const root = document.querySelector("[data-location-root]");
  if (!root) return;

  const mapEl = root.querySelector("[data-location-map]");
  const frame = root.querySelector("[data-location-frame]");
  const copyBtn = root.querySelector("[data-location-copy]");
  const copyLabel = root.querySelector("[data-location-copy-label]");
  const live = root.querySelector("[data-location-live]");

  const lat = Number(root.dataset.lat);
  const lng = Number(root.dataset.lng);
  const zoom = Number(root.dataset.zoom || 16);
  const markerLabel = root.dataset.markerLabel || "";
  const address = root.dataset.address || "";
  const mapsUrl = root.dataset.mapsUrl || "";
  const directionsUrl = root.dataset.directionsUrl || "";
  const embedUrl = root.dataset.embedUrl || "";
  const leafletCss =
    root.dataset.leafletCss || "/static/vendor/leaflet/leaflet.css";
  const leafletJs =
    root.dataset.leafletJs || "/static/vendor/leaflet/leaflet.js";

  let mapInstance = null;
  let assetsPromise = null;

  const announce = (message) => {
    if (!live) return;
    live.textContent = message;
    live.classList.add("is-visible");
    window.setTimeout(() => {
      live.classList.remove("is-visible");
      live.textContent = "";
    }, 2200);
  };

  const copyAddress = async () => {
    if (!address) return;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(address);
      } else {
        const ta = document.createElement("textarea");
        ta.value = address;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
      if (copyBtn) copyBtn.classList.add("is-copied");
      if (copyLabel) copyLabel.textContent = "کپی شد";
      announce("آدرس کپی شد");
      window.setTimeout(() => {
        if (copyBtn) copyBtn.classList.remove("is-copied");
        if (copyLabel) copyLabel.textContent = "کپی آدرس";
      }, 1800);
    } catch (_err) {
      announce("کپی انجام نشد");
    }
  };

  if (copyBtn) {
    copyBtn.addEventListener("click", copyAddress);
  }

  const loadCss = (href) =>
    new Promise((resolve, reject) => {
      if (document.querySelector(`link[data-ff-leaflet-css="1"]`)) {
        resolve();
        return;
      }
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      link.dataset.ffLeafletCss = "1";
      link.onload = () => resolve();
      link.onerror = () => reject(new Error("leaflet css"));
      document.head.appendChild(link);
    });

  const loadScript = (src) =>
    new Promise((resolve, reject) => {
      if (window.L) {
        resolve();
        return;
      }
      const existing = document.querySelector(`script[data-ff-leaflet-js="1"]`);
      if (existing) {
        existing.addEventListener("load", () => resolve());
        existing.addEventListener("error", () => reject(new Error("leaflet js")));
        return;
      }
      const script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.dataset.ffLeafletJs = "1";
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("leaflet js"));
      document.body.appendChild(script);
    });

  const ensureLeaflet = () => {
    if (assetsPromise) return assetsPromise;
    assetsPromise = Promise.all([loadCss(leafletCss), loadScript(leafletJs)]);
    return assetsPromise;
  };

  const markerIcon = () => {
    const L = window.L;
    return L.divIcon({
      className: "ff-map-marker-wrap",
      html:
        '<span class="ff-map-marker" aria-hidden="true">' +
        '<span class="ff-map-marker-core"></span>' +
        "</span>",
      iconSize: [44, 54],
      iconAnchor: [22, 52],
      popupAnchor: [0, -44],
    });
  };

  const markReady = () => {
    if (frame) frame.classList.add("is-ready");
  };

  const mountFallbackEmbed = () => {
    if (!frame) {
      markReady();
      return;
    }
    if (frame.querySelector(".ff-locate-embed")) {
      markReady();
      return;
    }

    /* Keep the vessel dark even if we must use Google embed */
    frame.classList.add("is-embed-dark");

    if (embedUrl) {
      const iframe = document.createElement("iframe");
      iframe.className = "ff-locate-embed";
      iframe.title = `نقشه موقعیت ${markerLabel}`.trim();
      iframe.loading = "lazy";
      iframe.referrerPolicy = "no-referrer-when-downgrade";
      iframe.allowFullscreen = true;
      iframe.src = embedUrl;
      iframe.addEventListener("load", markReady);
      frame.appendChild(iframe);
    } else {
      markReady();
    }

    if (mapEl) mapEl.setAttribute("hidden", "");
  };

  const addDarkTiles = (L, map) => {
    /* OSM + court filter = previous brand look; Carto as native-dark backup */
    const layers = [
      {
        url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        options: {
          maxZoom: 19,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" rel="noopener noreferrer" target="_blank">OSM</a>',
        },
        skin: "filter-dark",
      },
      {
        url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        options: {
          maxZoom: 20,
          subdomains: "abcd",
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" rel="noopener noreferrer" target="_blank">OSM</a> &copy; <a href="https://carto.com/" rel="noopener noreferrer" target="_blank">CARTO</a>',
        },
        skin: "native-dark",
      },
    ];

    const primary = layers[0];
    const layer = L.tileLayer(primary.url, primary.options);
    layer.addTo(map);
    if (mapEl) mapEl.dataset.mapSkin = primary.skin;

    let swapped = false;
    layer.on("tileerror", () => {
      if (swapped) return;
      swapped = true;
      map.removeLayer(layer);
      const fallback = layers[1];
      L.tileLayer(fallback.url, fallback.options).addTo(map);
      if (mapEl) mapEl.dataset.mapSkin = fallback.skin;
    });
  };

  const initMap = () => {
    if (!mapEl || mapInstance || !Number.isFinite(lat) || !Number.isFinite(lng)) {
      mountFallbackEmbed();
      return;
    }

    ensureLeaflet()
      .then(() => {
        const L = window.L;
        if (!L) throw new Error("leaflet missing");

        mapInstance = L.map(mapEl, {
          center: [lat, lng],
          zoom,
          scrollWheelZoom: false,
          zoomControl: true,
          attributionControl: true,
          keyboard: true,
        });

        addDarkTiles(L, mapInstance);

        const marker = L.marker([lat, lng], {
          icon: markerIcon(),
          title: markerLabel,
          alt: markerLabel || "موقعیت سالن",
          keyboard: true,
          riseOnHover: true,
        }).addTo(mapInstance);

        const popupBits = [
          markerLabel ? `<strong dir="auto">${markerLabel}</strong>` : "",
          address ? `<span dir="auto">${address}</span>` : "",
          directionsUrl
            ? `<a href="${directionsUrl}" target="_blank" rel="noopener noreferrer">مسیریابی</a>`
            : "",
          mapsUrl
            ? `<a href="${mapsUrl}" target="_blank" rel="noopener noreferrer">نقشه</a>`
            : "",
        ]
          .filter(Boolean)
          .join("<br>");

        if (popupBits) {
          marker.bindPopup(
            `<div class="ff-map-popup" dir="rtl">${popupBits}</div>`,
            { closeButton: true, className: "ff-map-popup-shell" }
          );
        }

        mapInstance.whenReady(() => {
          window.setTimeout(() => {
            mapInstance.invalidateSize();
            markReady();
          }, 60);
        });

        const enableWheel = () => mapInstance.scrollWheelZoom.enable();
        const disableWheel = () => mapInstance.scrollWheelZoom.disable();
        mapEl.addEventListener("focus", enableWheel);
        mapEl.addEventListener("blur", disableWheel);
        mapEl.addEventListener("mouseenter", enableWheel);
        mapEl.addEventListener("mouseleave", disableWheel);
      })
      .catch(() => {
        mountFallbackEmbed();
      });
  };

  const boot = () => {
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            io.disconnect();
            initMap();
          });
        },
        { rootMargin: "240px 0px", threshold: 0.01 }
      );
      io.observe(root);
    } else {
      initMap();
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot, { once: true });
  } else {
    boot();
  }
})();
