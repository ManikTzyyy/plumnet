document.addEventListener("DOMContentLoaded", function () {
  const checkboxes = document.querySelectorAll(".client-checkbox");
  const activateBtn = document.getElementById("activate-all");
  const selectAll = document.getElementById("select-all-checkbox");
  const btnGO = document.getElementById("go-action");
  const action = document.getElementById("action-dropdown");

  function updateActivateBtn() {
    if (!activateBtn) return;
    const selectedCount = Array.from(checkboxes).filter(
      (cb) => cb.checked
    ).length;

    if (selectedCount === 0) {
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
      updateActivateBtn();
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
      updateActivateBtn();
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
          profile: cb.dataset.paket,
          local_address: cb.dataset.iplocal,
          idpaket: cb.dataset.idpaket,
          idpool: cb.dataset.idpool,
          poolname: cb.dataset.poolname,
        }));

      if (selectedIds.length === 0) {
        Swal.fire({
          title: "Pilih Data terlebih dahulu!",
          icon: "warning",
        });

        return;
      }

      if (actionValue === "delete") {
        handleMultiple(selectedIds, "client", "client", "delete");
      } else if (actionValue === "payment") {
        handleMultiple(selectedIds, "client", "client", "payment");
      } else if (actionValue === "delete-gw") {
        handleMultiple(selectedIds, "gateway", "server-list", "delete");
      } else if (actionValue === "delete-paket") {
        handleMultiple(selectedIds, "paket", "paket-list", "delete");
      } else if (actionValue === "delete-ts") {
        handleMultiple(selectedIds, "trans", "client", "delete");
      } else if (actionValue === "verifikasi") {
        handleMultiple(selectedIds, "client", "client", "verif");
      } else if (actionValue === "network-status") {
        handleMultiple(selectedIds, "client", "client", "network");
      } else if (actionValue === "migrasi") {
        let datatoSend = selectedIds;

        datatoSend = selectedIds.map((item) => ({
          id_client: item.id,
          id_paket: item.idpaket,
          paket_name: item.profile,
          id_pool: item.idpool,
          pool_name: item.poolname,
        }));

        const invalidData = datatoSend.filter(
          (d) => !d.id_paket || !d.paket_name || !d.id_pool || !d.pool_name
        );

        // if (invalidData.length > 0) {
        //   const invalidList = invalidData
        //     .map((d) => `Client ID: ${d.id_client || "(tidak diketahui)"}`)
        //     .join("\n");
        //   Swal.fire({
        //     title: "Data tidak lengkap!",
        //     html: `Client tidak memiliki paket, mohon set paket dulu:<br><pre>${invalidList}</pre>`,
        //     icon: "warning",
        //   });
        //   return;
        // }

        console.log(datatoSend)

        migrateDatas(datatoSend);
      } else {
        Swal.fire({
          title: "Pilih Action terlebih dahulu!",
          icon: "warning",
        });
      }
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const checkboxesIP = document.querySelectorAll(".ip-checkbox");
  const selectAllIP = document.getElementById("select-all-checkbox-IP");
  const btnGOIP = document.getElementById("go-action-ip");
  const actionIP = document.getElementById("action-dropdown-ip");

  // Toggle row highlight
  function toggleRowHighlightIP(cb) {
    const row = cb.closest("tr");
    if (cb.checked) {
      row.classList.add("selected-row");
    } else {
      row.classList.remove("selected-row");
    }
  }

  // Event listener untuk setiap checkbox
  checkboxesIP.forEach((cb) => {
    cb.addEventListener("change", () => {
      toggleRowHighlightIP(cb);
    });
  });

  // Event listener untuk selectAll
  if (selectAllIP) {
    selectAllIP.addEventListener("change", function () {
      const checked = this.checked;
      checkboxesIP.forEach((cb) => {
        cb.checked = checked;
        toggleRowHighlightIP(cb);
      });
    });
  }

  if (btnGOIP && actionIP) {
    btnGOIP.addEventListener("click", () => {
      const actionValueIP = actionIP.value;
      const selectedIdsIP = Array.from(checkboxesIP)
        .filter((cb) => cb.checked)
        .map((cb) => ({
          id: cb.dataset.id,
          name: cb.dataset.name,
        }));

      if (selectedIdsIP.length === 0) {
        Swal.fire({
          title: "Pilih Data terlebih dahulu!",
          icon: "warning",
        });
        return;
      }

      if (actionValueIP === "delete-ip") {
        handleMultiple(selectedIdsIP, "ip", "paket-list", "delete");
        // alert("delete ip" + selectedIdsIP);
      } else {
        Swal.fire({
          title: "Pilih Action terlebih dahulu!",
          icon: "warning",
        });
      }
    });
  }
});
