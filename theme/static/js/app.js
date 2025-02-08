const toggleButton = document.querySelector(".menuButton");
const menu = document.getElementById("mobileMenu");
// Add event listener to toggle menu visibility
toggleButton.addEventListener("click", () => {
  menu.classList.toggle("hidden");
});
// Fixed
window.addEventListener("scroll", function () {
  const mobileMenu = document.getElementById("navbar");
  const navbar_color = document.getElementById("navbarColor");
  if (window.scrollY > 0) {
    // Check if the page is scrolled
    mobileMenu.classList.add("fixed"); // Add shadow when scrolled
    navbar_color.classList.add("shadow-lg", "bg-white");
  } else {
    mobileMenu.classList.remove("shadow-lg", "fixed"); // Remove shadow when at the top
    navbar_color.classList.remove("shadow-lg", "bg-white");
  }
});
function moveCarousel(carouselId, direction) {
  const carousel = document.getElementById(carouselId);
  const cardWidth = carousel.firstElementChild.offsetWidth + 16; // Include spacing
  carousel.scrollLeft += direction * cardWidth;
}
