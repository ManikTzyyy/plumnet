document.addEventListener("DOMContentLoaded", function () {
  const checkboxes = document.querySelectorAll(".client-checkbox");
  const selectedList = document.getElementById("selected-list");
  const activateBtn = document.getElementById("activate-all");
  const selectAll = document.getElementById("select-all-checkbox");
  const btnGO = document.getElementById("go-action");
  const action = document.getElementById("action-dropdown");

  // Update selected list & tombol aktivasi
  function updateSelected() {
    selectedList.innerHTML = ""; // kosongin list

    const selected = Array.from(checkboxes)
      .filter((cb) => cb.checked)
      .map((cb) => ({
        id: cb.dataset.id,
        name: cb.dataset.name,
        paket: cb.dataset.paket,
      }));

    selected.forEach((client) => {
      const item = document.createElement("div");
      item.classList.add("item-selected");
      item.textContent = `${client.name} (${client.paket})`;
      selectedList.appendChild(item);
    });

    if (selected.length === 0) {
      activateBtn.disabled = true;
      activateBtn.classList.add("disable-button");
      activateBtn.classList.remove("success-button");
    } else {
      activateBtn.disabled = false;
      activateBtn.classList.remove("disable-button");
      activateBtn.classList.add("success-button");
    }
  }

  // Toggle row highlight
  function toggleRowHighlight(cb) {
    const row = cb.closest("tr");
    if (cb.checked) {
      row.classList.add("selected-row");
    } else {
      row.classList.remove("selected-row");
    }
  }

  // Event listener untuk setiap checkbox
  checkboxes.forEach((cb) => {
    cb.addEventListener("change", () => {
      toggleRowHighlight(cb);
      updateSelected();
    });
  });

  // Event listener untuk selectAll
  if (selectAll) {
    selectAll.addEventListener("change", function () {
      const checked = this.checked;
      checkboxes.forEach((cb) => {
        cb.checked = checked;
        toggleRowHighlight(cb);
      });
      updateSelected();
    });
  }

  // Event tombol aktivasi
  if (activateBtn) {
    activateBtn.addEventListener("click", () => {
      const selectedIds = Array.from(checkboxes)
        .filter((cb) => cb.checked)
        .map((cb) => ({
          name: cb.dataset.name,
          host: cb.dataset.host,
          username: cb.dataset.username,
          password: cb.dataset.password,
          pppoe: cb.dataset.pppoe,
          profile: cb.dataset.paket,
          local_address: cb.dataset.iplocal,
        }));
      toggleActivasiMultiClient(selectedIds);
    });
  }

  // Event tombol GO action
  if (btnGO && action) {
    btnGO.addEventListener("click", () => {
      const actionValue = action.value;
      const selectedIds = Array.from(checkboxes)
        .filter((cb) => cb.checked)
        .map((cb) => ({
          id: cb.dataset.id,
          name: cb.dataset.name,
          host: cb.dataset.host,
          username: cb.dataset.username,
          password: cb.dataset.password,
          pppoe: cb.dataset.pppoe,
        }));

      if (selectedIds.length === 0) {
        Swal.fire({
          title: "Pilih Data terlebih dahulu!",
          icon: "warning",
        });
        return;
      }

      if (actionValue === "delete") {
        deleteMultiple(selectedIds, "client", "client");
      } else if (actionValue === "payment") {
        // functionChangeStatusPaymentMultiple();
      } else {
        Swal.fire({
          title: "Pilih Action terlebih dahulu!",
          icon: "warning",
        });
      }
    });
  }
});
