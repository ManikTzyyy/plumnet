const checkboxes = document.querySelectorAll(".client-checkbox");
const selectedList = document.getElementById("selected-list");
const activateBtn = document.getElementById("activate-all");

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
    const selected = document.createElement("div");
    selected.classList.add("item-selected");
    selected.textContent = `${client.name} (${client.paket})`;
    selectedList.appendChild(selected);
  });

  if (selected.length == 0) {
    activateBtn.disabled = true;
    activateBtn.classList.add("disbale-button");
    activateBtn.classList.remove("success-button");
    selectedList.style.display = "none";
  } else {
    activateBtn.disabled = false;
    activateBtn.classList.remove("disbale-button");
    activateBtn.classList.add("success-button");
    selectedList.style.display = "flex";
  }
}

checkboxes.forEach((cb) => cb.addEventListener("change", updateSelected));

// contoh event untuk tombol aktivasi
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
