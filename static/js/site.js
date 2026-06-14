document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menuBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  let revealInitialized = false;

  const initializeRevealObserver = () => {
    if (revealInitialized) return;

    const revealItems = document.querySelectorAll(".reveal");
    if (!revealItems.length) return;

    revealInitialized = true;

    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      {
        threshold: 0.16,
        rootMargin: "0px 0px -8% 0px",
      }
    );

    revealItems.forEach((item) => revealObserver.observe(item));
  };

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

  // Age gate logic

  const isHomePage = window.location.pathname === "/";
  const navEntry = performance.getEntriesByType("navigation")[0];
  const navType = navEntry ? navEntry.type : "navigate";

  let isInternalReferrer = false;
  if (document.referrer) {
    try {
      isInternalReferrer =
        new URL(document.referrer).origin === window.location.origin;
    } catch (err) {
      isInternalReferrer = false;
    }
  }

  // Show on:
  // - first/return visits from outside (navigate + external/empty referrer)
  // - refreshes (reload)
  // Skip on internal navigation (navigate + internal referrer)
  const shouldShowAgeGate =
    isHomePage &&
    (navType === "reload" || (navType === "navigate" && !isInternalReferrer));

  if (shouldShowAgeGate) {
    const ageGate = document.createElement("div");
    ageGate.className = "age-gate";
    ageGate.innerHTML = `
      <div class="age-gate__panel" role="dialog" aria-modal="true" aria-labelledby="age-gate-title">
        <div class="age-gate__logo-wrap">
          <img src="/static/img/lightlablogo.jpg" alt="LightLab logo" class="age-gate__logo">
        </div>
        <p class="age-gate__eyebrow">18+ Only</p>
        <h2 id="age-gate-title" class="age-gate__title">Enter LightLabs</h2>
        <p class="age-gate__text">
          This website contains age-restricted Products.
          Research Purposes only. You must be 18 or over to enter.
        </p>
        <div class="age-gate__actions">
          <button type="button" class="age-gate__enter">Enter Site</button>
          <a href="https://www.google.com" class="age-gate__leave">Leave</a>
        </div>
      </div>
    `;

    document.body.appendChild(ageGate);
    document.body.style.overflow = "hidden";

    const enterButton = ageGate.querySelector(".age-gate__enter");
    enterButton.addEventListener("click", () => {
      ageGate.remove();
      document.body.style.overflow = "";
      window.requestAnimationFrame(() => {
        initializeRevealObserver();
      });
    });
  } else {
    initializeRevealObserver();
  }
});