document.addEventListener("DOMContentLoaded", () => {
const menuBtn = document.getElementById("menuBtn");
const mobileMenu = document.getElementById("mobileMenu");



if (!menuBtn || !mobileMenu) return;

menuBtn.addEventListener("click", (e) => {
e.preventDefault();
mobileMenu.classList.toggle("hidden");
});

mobileMenu.querySelectorAll("a").forEach((link) => {
link.addEventListener("click", () => {
mobileMenu.classList.add("hidden");
});
});
});