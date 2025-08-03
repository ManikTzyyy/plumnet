// Komponen loading
function loadingComponent() {
  return `
    <span class="loader-form" style="display: block;"></span>
    <p class="text-center">Load Data....</p>
  `;
}



  function initChartsWithDummy() {
    new Chart(document.getElementById("cpuLoad"), {
      type: "doughnut",
      data: {
        datasets: [
          {
            rotation: 180,
            cutout: 60,
            data: [0, 100],
            backgroundColor: ["#cccccc", "#f0f0f0"],
          },
        ],
      },
    });

    new Chart(document.getElementById("memoryUsage"), {
      type: "doughnut",
      data: {
        datasets: [
          {
            rotation: 180,
            cutout: 60,
            data: [0, 100],
            backgroundColor: ["#cccccc", "#f0f0f0"],
          },
        ],
      },
    });

    new Chart(document.getElementById("pppClient"), {
      type: "doughnut",
      data: {
        datasets: [
          {
            rotation: 180,
            cutout: 60,
            data: [0, 100],
            backgroundColor: ["#cccccc", "#f0f0f0"],
          },
        ],
      },
    });
  }

// Komponen error
function errorComponent(errorMessage) {

  return `
  <p class="text-center error-msg" style="color:red;">Error coy: ${errorMessage}</p>
   <div class="row monitor-wrapper">
      <!-- CPU Card -->
      <div class="card-donut column">
        <div class="donut-name row">
          <i class="fa-solid fa-microchip"></i>
          <div class="">CPU usage</div>
        </div>
        <div class="donut-content">
          <canvas id="cpuLoad"></canvas>
          <div class="number">0</div>
        </div>
        <div class="donut-desc">
          <span class="text-main">0</span> used
        </div>
      </div>

      <!-- Memory Card -->
      <div class="card-donut column">
        <div class="donut-name row">
          <i class="fa-solid fa-hard-drive"></i>
          <div class="">Memory usage</div>
        </div>
        <div class="donut-content">
          <canvas id="memoryUsage"></canvas>
          <div class="number">0</div>
        </div>
        <div class="donut-desc">
          free<span class="text-main"> 0 MB</span>
          <span class="text-grey"> from </span><span class="text-main">0 MB</span>
        </div>
      </div>

      <!-- PPPoE -->
      <div class="card-donut column">
        <div class="donut-name row">
          <i class="fa-solid fa-user-check"></i>
          <div class="">PPPoE Active</div>
        </div>
        <div class="donut-content">
          <canvas id="pppClient"></canvas>
          <div class="number">0</div>
        </div>
        <div class="donut-desc">
          <span class="text-main"> 0 active</span>
          <span class="text-grey"> from </span><span class="text-main">0 List</span>
        </div>
      </div>

      <!-- Device Info -->
      <div class="card-donut column device">
        <div class="donut-name row">
          <i class="fa-solid fa-circle-info"></i>
          <div class="">Device Information</div>
        </div>
        <div class="card-device-wrapper-main column">
          <div class="device-text column">
            <div class="">0 GHz</div>
            <div class="text-grey">0 CPU</div>
          </div>
          <div class="device-content">
            <div class="number">No Data</div>
          </div>
          <div class="device-text-wrapper row">
            <div class="device-text column">
              <div class="">0</div>
              <div class="text-grey">0</div>
            </div>
            <div class="device-text">0</div>
          </div>
        </div>
      </div>
    </div>
  
  `;
}

// Komponen data server
function serverInfoComponent(data) {
  const free = data.free_memory;
  const total = data.total_memory;
  const used = total - free;
  const usedPercent = ((used / total) * 100).toFixed(2);

  return `
    <div class="row monitor-wrapper">
      <!-- CPU Card -->
      <div class="card-donut column">
        <div class="donut-name row">
          <i class="fa-solid fa-microchip"></i>
          <div class="">CPU usage</div>
        </div>
        <div class="donut-content">
          <canvas id="cpuLoad"></canvas>
          <div class="number">${data.cpu_load}%</div>
        </div>
        <div class="donut-desc">
          <span class="text-main">${data.cpu_load}%</span> used
        </div>
      </div>

      <!-- Memory Card -->
      <div class="card-donut column">
        <div class="donut-name row">
          <i class="fa-solid fa-hard-drive"></i>
          <div class="">Memory usage</div>
        </div>
        <div class="donut-content">
          <canvas id="memoryUsage"></canvas>
          <div class="number">${usedPercent}%</div>
        </div>
        <div class="donut-desc">
          free<span class="text-main"> ${data.free_memory} MB</span>
          <span class="text-grey"> from </span><span class="text-main">${data.total_memory} MB</span>
        </div>
      </div>

      <!-- PPPoE -->
      <div class="card-donut column">
        <div class="donut-name row">
          <i class="fa-solid fa-user-check"></i>
          <div class="">PPPoE Active</div>
        </div>
        <div class="donut-content">
          <canvas id="pppClient"></canvas>
          <div class="number">90%</div>
        </div>
        <div class="donut-desc">
          <span class="text-main"> 90 active</span>
          <span class="text-grey"> from </span><span class="text-main">60 List</span>
        </div>
      </div>

      <!-- Device Info -->
      <div class="card-donut column device">
        <div class="donut-name row">
          <i class="fa-solid fa-circle-info"></i>
          <div class="">Device Information</div>
        </div>
        <div class="card-device-wrapper-main column">
          <div class="device-text column">
            <div class="">${data.cpu_freq} GHz</div>
            <div class="text-grey">${data.cpu_count} CPU</div>
          </div>
          <div class="device-content">
            <div class="circle"></div>
            <div class="number">${data.uptime}</div>
          </div>
          <div class="device-text-wrapper row">
            <div class="device-text column">
              <div class="">${data.cpu}</div>
              <div class="text-grey">${data.version}</div>
            </div>
            <div class="device-text">${data.board_name}</div>
          </div>
        </div>
      </div>
    </div>
  `;
}
