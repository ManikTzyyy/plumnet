const showLoader = () => {
  document.querySelector(".loader-wrapper").style.display = "flex"; // atau block
};

const hideLoader = () => {
  document.querySelector(".loader-wrapper").style.display = "none";
};

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (e.submitter && e.submitter.classList.contains("no-loader")) return;
      showLoader();
    });
  });

   document.querySelectorAll("button.delete-button").forEach((btn) => {
    btn.addEventListener("click", () => {
      showLoader();
    });
  });

  document.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", function (e) {
      if (link.classList.contains("no-loader")) return;
      const href = link.getAttribute("href");
      if (href && !href.startsWith("#") && !href.startsWith("javascript")) {
        showLoader();
      }
    });
  });
});
