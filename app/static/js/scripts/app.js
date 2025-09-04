document.addEventListener("DOMContentLoaded", function() {
  // Mendapatkan URL saat ini
  const currentUrl = window.location.pathname;

  // Mendapatkan semua elemen menu
  const menuLinks = document.querySelectorAll('.menu-link');

  // Menambahkan kelas 'active' pada elemen yang sesuai
  menuLinks.forEach(link => {
      const linkUrl = link.getAttribute('href');
      if (linkUrl === currentUrl) {
          link.classList.add('active');
      }
  });
});


document.addEventListener("DOMContentLoaded", function () {
  // Memeriksa status kolaps dari localStorage
  const isCollapsed = localStorage.getItem("sidebarCollapsed") === 'true';

  const sidebar = document.querySelector(".sidebar");
  if (isCollapsed) {
      sidebar.classList.add("collapsed");
      const menuText = document.querySelectorAll(".menu-text");
      menuText.forEach(function (menuText) {
          menuText.classList.add("hidden");
      });
      const collapse = document.querySelectorAll(".menu-collapse");
      collapse.forEach(function (collapse) {
          collapse.classList.add("collapse");
      });
  }

  // Menambahkan event listener untuk toggle menu
  document.getElementById("toggle-menu").addEventListener("click", function () {
      const menuText = document.querySelectorAll(".menu-text");
      menuText.forEach(function (menuText) {
          menuText.classList.toggle("hidden");
      });

      const collapse = document.querySelectorAll(".menu-collapse");
      collapse.forEach(function (collapse) {
          collapse.classList.toggle("collapse");
      });

      sidebar.classList.toggle("collapsed");

      const isCollapsed = sidebar.classList.contains("collapsed");
      localStorage.setItem("sidebarCollapsed", isCollapsed);
  });
});





// Icon for leaftjs
var serverIcon = L.divIcon({
    className: 'map-icon',
    html: '<i class="fas fa-server"></i>',
    iconSize: [30, 30],
    iconAnchor: [15, 10]
});


var odpIcon = L.divIcon({
    className: 'map-icon',
    html: '<i class="fas fa-network-wired"></i>',
    iconSize: [30, 30],
    iconAnchor: [15, 10]
});

var clientIcon = L.divIcon({
    className: 'map-icon',
    html: '<i class="fas fa-user"></i>',
    iconSize: [30, 30],
    iconAnchor: [15, 10]
});