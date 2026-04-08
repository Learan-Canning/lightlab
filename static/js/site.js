// Handles the mobile menu open/close behavior.
document.addEventListener("DOMContentLoaded", () => {
	const menuBtn = document.getElementById("menuBtn");
	const mobileMenu = document.getElementById("mobileMenu");

	// Exit safely if either element is missing.
	if (!menuBtn || !mobileMenu) return;

	// Toggle menu visibility when the hamburger is clicked.
	menuBtn.addEventListener("click", (e) => {
		e.preventDefault();
		mobileMenu.classList.toggle("hidden");
	});

	// Close the mobile menu after selecting a link.
	mobileMenu.querySelectorAll("a").forEach((link) => {
		link.addEventListener("click", () => {
			mobileMenu.classList.add("hidden");
		});
	});
});