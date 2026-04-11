document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menuBtn");
  const mobileMenu = document.getElementById("mobileMenu");

  // Mobile menu toggle
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener("click", (e) => {
      e.preventDefault();
      mobileMenu.classList.toggle("hidden");
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenu.classList.add("hidden");
      });
    });
  }

  // FAQ accordion toggle (single item open at a time)
  const faqToggles = document.querySelectorAll(".faq-toggle");

  faqToggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const answer = toggle.nextElementSibling;
      const arrow = toggle.querySelector("i");
      const isExpanded = toggle.getAttribute("aria-expanded") === "true";

      faqToggles.forEach((otherToggle) => {
        if (otherToggle !== toggle) {
          otherToggle.setAttribute("aria-expanded", "false");
          otherToggle.nextElementSibling.classList.add("hidden");
          otherToggle.querySelector("i").style.transform = "rotate(0deg)";
        }
      });

      toggle.setAttribute("aria-expanded", String(!isExpanded));
      answer.classList.toggle("hidden");
      arrow.style.transform = isExpanded ? "rotate(0deg)" : "rotate(180deg)";
    });
  });
});