(function () {
  "use strict";

  function initHomeReviews() {
    var root = document.querySelector("[data-home-reviews-swiper]");
    if (!root || typeof window.Swiper === "undefined") return;

    new window.Swiper(root, {
      slidesPerView: 1,
      spaceBetween: 16,
      speed: 650,
      grabCursor: true,
      watchOverflow: true,
      keyboard: { enabled: true },
      navigation: {
        prevEl: "[data-home-reviews-prev]",
        nextEl: "[data-home-reviews-next]",
      },
      pagination: {
        el: "[data-home-reviews-pagination]",
        clickable: true,
      },
      breakpoints: {
        720: { slidesPerView: 2, spaceBetween: 16 },
        1100: { slidesPerView: 3, spaceBetween: 16 },
      },
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initHomeReviews);
  } else {
    initHomeReviews();
  }
})();
