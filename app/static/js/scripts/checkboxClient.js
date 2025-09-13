document.addEventListener("DOMContentLoaded", function () {
  const checkboxes = document.querySelectorAll(".client-checkbox");
  const btnGO = document.getElementById("go-action");
  const action = document.getElementById("action-dropdown");
  const selectAll = document.getElementById("select-all-checkbox");

  // highlight baris kalau dipilih
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", function () {
      const row = this.closest("tr");
      if (this.checked) {
        row.classList.add("selected-row");
      } else {
        row.classList.remove("selected-row");
      }
    });
  });

  if (selectAll) {
    selectAll.addEventListener("change", function () {
      const checked = this.checked;
      checkboxes.forEach((cb) => {
        cb.checked = checked;
        const row = cb.closest("tr");
        if (checked) {
          row.classList.add("selected-row");
        } else {
          row.classList.remove("selected-row");
        }
      });
    });
  }

  btnGO.addEventListener("click", function () {
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
    // console.log(selectedIds);

    if (selectedIds.length > 0) {
      if (actionValue == "delete") {
        deleteMultiple(selectedIds, "client", "client");
      } else if (actionValue == "payment") {
        //functionChangeStatusPaymentMultiple
      } else {
        Swal.fire({
          title: "Pilih Action terlebih dahulu!",
          icon: "warning",
        });
      }
    } else {
      Swal.fire({
        title: "Pilih Data terlebih dahulu!",
        icon: "warning",
      });
    }
  });
});
