const showLoader = () => {
  document.querySelector(".loader-wrapper").style.display = "flex"; // atau block
};

const hideLoader = () => {
  document.querySelector(".loader-wrapper").style.display = "none";
};



// Intercept semua form submit
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      showLoader();
    });
  });

  // Intercept semua link yang perlu waktu (opsional)
  document.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", function (e) {
      const href = link.getAttribute("href");

      // Hindari link ke # atau javascript:void(0)
      if (href && !href.startsWith("#") && !href.startsWith("javascript")) {
        showLoader();
      }
    });
  });
});
