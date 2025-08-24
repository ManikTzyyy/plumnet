// Loader & error
const loadingComponent = () => 
  
  `
    <span class="loader-form"></span>
    <p class="text-center">Load Data....</p>
  `;

const errorComponent = (msg) => `
    <p class="text-center error-msg">Error: ${msg}</p>
  `;

// Generator card donut
function cardDonut({ id, icon, title, number, desc }) {
  return `
      <div class="card-donut column">
        <div class="donut-name row">
          <i class="${icon}"></i><div>${title}</div>
        </div>
        <div class="donut-content">
          <canvas id="${id}"></canvas>
          <div class="number">${number}</div>
        </div>
        <div class="donut-desc">${desc}</div>
      </div>
    `;
}

// Server info view
function serverInfoComponent(data) {
  const free = data.free_memory;
  const total = data.total_memory;
  const used = total - free;
  const usedPercent = ((used / total) * 100).toFixed(2);

  const client = data.client_count
  const client_active = data.client_active
  const activePercent = ((client_active / client) *100).toFixed(2)

  return `
      <div class="row monitor-wrapper">
        ${cardDonut({
          id: "cpuLoad",
          icon: "fa-solid fa-microchip",
          title: "CPU usage",
          number: `${data.cpu_load}%`,
          desc: `<span class="text-main">${data.cpu_load}%</span> used`,
        })}

        ${cardDonut({
          id: "memoryUsage",
          icon: "fa-solid fa-hard-drive",
          title: "Memory usage",
          number: `${usedPercent}%`,
          desc: `free <span class="text-main">${free} MB</span> 
                 <span class="text-grey"> from </span>
                 <span class="text-main">${total} MB</span>`,
        })}

        ${cardDonut({
          id: "pppClient",
          icon: "fa-solid fa-user-check",
          title: "PPPoE Active",
          number: `${activePercent}`,
          desc: `<span class="text-main">${client_active} active</span>
                 <span class="text-grey"> from </span>
                 <span class="text-main">${client} List</span>`,
        })}

        <div class="card-donut column device">
          <div class="donut-name row">
            <i class="fa-solid fa-circle-info"></i><div>Device Information</div>
          </div>
          <div class="card-device-wrapper-main column">
            <div class="device-text column">
              <div>${data.cpu_freq} GHz</div>
              <div class="text-grey">${data.cpu_count} CPU</div>
            </div>
            <div class="device-content">
              <div class="circle"></div>
              <div class="number">${data.uptime}</div>
            </div>
            <div class="device-text-wrapper row">
              <div class="device-text column">
                <div>${data.cpu}</div>
                <div class="text-grey">${data.version}</div>
              </div>
              <div class="device-text">${data.board_name}</div>
            </div>
          </div>
        </div>
      </div>
    `;
}

// Chart helper
function renderDonutChart(elId, value) {
  const ctx = document.getElementById(elId);
  if (!ctx) return;
  new Chart(ctx, {
    type: "doughnut",
    data: {
      datasets: [
        {
          rotation: 180,
          cutout: 60,
          data: [value, 100 - value],
          backgroundColor: ["#211C84", "#E8E2F5"],
        },
      ],
    },
  });
}

// Load server info
async function loadServerInfo(serverId) {
  const infoDiv = document.getElementById("server-info");
  infoDiv.innerHTML = loadingComponent();

  showLoaderForm()

  try {
    const res = await fetch(`/get-server-info/${serverId}/`);
    const data = await res.json();


    if (data.error) {
      infoDiv.innerHTML = errorComponent(data.error);
      ["cpuLoad", "memoryUsage", "pppClient"].forEach((id) =>
        renderDonutChart(id, 0)
      );
      return;
    }

    infoDiv.innerHTML = serverInfoComponent(data);

    // Render charts
    renderDonutChart("cpuLoad", data.cpu_load);
    const usedPercent = (
      ((data.total_memory - data.free_memory) / data.total_memory) *
      100
    ).toFixed(2);
    renderDonutChart("memoryUsage", usedPercent);

    const activePercent = ((data.client_active / data.client_count)*100).toFixed(2)
   

    renderDonutChart("pppClient", activePercent);
   
  } catch (err) {
    infoDiv.innerHTML = errorComponent(err.message);

    hideLoaderForm()
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const selectEl = document.getElementById("server");
  const infoDiv = document.getElementById("server-info");

  if (selectEl?.value) {
    loadServerInfo(selectEl.value);
    selectEl.addEventListener("change", () => loadServerInfo(selectEl.value));
  } else {
    infoDiv.innerHTML = `
        <div class="no-data column">
          <div class="img-wrapper">
           <img src="${NO_DATA_IMG}" alt="" />
          </div>
          <h3>Belum ada data yang ditambahkan</h3>
          <p>Silakan tambahkan data <a href="{% url 'server' %}">disini</a></p>
        </div>
      `;
  }
});
