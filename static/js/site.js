document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menuBtn");
  const mobileMenu = document.getElementById("mobileMenu");
  let revealInitialized = false;
  const whatsappNumber = "447522069867";

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
      if (!answer) return;

      const arrow = toggle.querySelector("svg, i");
      const isExpanded = toggle.getAttribute("aria-expanded") === "true";

      faqToggles.forEach((otherToggle) => {
        if (otherToggle !== toggle) {
          otherToggle.setAttribute("aria-expanded", "false");

          const otherAnswer = otherToggle.nextElementSibling;
          if (otherAnswer) otherAnswer.classList.add("hidden");

          const otherArrow = otherToggle.querySelector("svg, i");
          if (otherArrow) otherArrow.style.transform = "rotate(0deg)";
        }
      });

      toggle.setAttribute("aria-expanded", String(!isExpanded));
      answer.classList.toggle("hidden");

      if (arrow) {
        arrow.style.transform = isExpanded ? "rotate(0deg)" : "rotate(180deg)";
      }
    });
  });

  const selectFirstAvailableVariant = () => {
    const forms = document.querySelectorAll(".js-variant-form");
    forms.forEach((form) => {
      const checked = form.querySelector(".js-variant-radio:checked:not(:disabled)");
      if (checked) return;

      const firstAvailable = form.querySelector(".js-variant-radio:not(:disabled)");
      if (firstAvailable) {
        firstAvailable.checked = true;
      }
    });
  };

  const addWhatsAppFloat = () => {
    if (document.querySelector(".whatsapp-float")) return;

    const link = document.createElement("a");
    link.href = `https://wa.me/${whatsappNumber}`;
    link.className = "whatsapp-float";
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", "Need help? Contact us on WhatsApp");
    link.innerHTML = `
      <span class="whatsapp-float__icon" aria-hidden="true">
        <i data-lucide="message-circle" class="w-4 h-4"></i>
      </span>
      <span class="whatsapp-float__text">Need help? Contact us on WhatsApp</span>
    `;

    document.body.appendChild(link);
  };

  selectFirstAvailableVariant();
  addWhatsAppFloat();

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
        <h2 id="age-gate-title" class="age-gate__title">Enter LightLab</h2>
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