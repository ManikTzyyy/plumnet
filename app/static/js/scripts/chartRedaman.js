  function getLast7Days() {
      const dates = [];
      const today = new Date();
      for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(today.getDate() - i);
        dates.push(d.toLocaleDateString("id-ID", { day: "2-digit", month: "short" }));
      }
      return dates;
    }

    const labels = getLast7Days();

    // fungsi bikin angka random antara min & max
    function randomData(count, min, max) {
      let arr = [];
      for (let i = 0; i < count; i++) {
        arr.push(Math.floor(Math.random() * (max - min + 1)) + min);
      }
      return arr;
    }

    // bikin data
    const data = {
      labels: labels,
      datasets: [
        {
          label: 'Redaman',
          data: randomData(labels.length, -50, 7),
          borderColor: 'blue',
          backgroundColor: 'rgba(0, 0, 255, 0.3)',
        }
      ]
    };

    // config chart
    const config = {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
          title: { display: true, text: 'Redaman 7 Hari Terakhir' }
        },
        scales: {
          y: {
            min: -60,
            max: 10
          }
        }
      },
    };

    // render chart
    new Chart(
      document.getElementById('redamanChart'),
      config
    );