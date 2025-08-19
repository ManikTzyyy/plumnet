function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}
function getCSRFToken() {
  return getCookie("csrftoken");
}

// console.log(getCSRFToken());

window.addEventListener("pageshow", function (event) {
  if (event.persisted) {
    // Halaman datang dari cache (back/forward)
    window.location.reload();
  }
});

function deleteData(id, object, url) {
  Swal.fire({
    title: "Hapus data ini?",
    text: "Aksi ini tidak dapat dibatalkan!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#aaa",
    confirmButtonText: "Ya, hapus!",
    cancelButtonText: "Batal",
  }).then((result) => {
    if (!result.isConfirmed) return;

    showMyLoader();

    fetch(`/${object}/${id}/delete/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
        Accept: "application/json",
      },
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (data.success) {
          Swal.fire("Terhapus!", "Data berhasil dihapus.", "success").then(
            () => {
              location.href = `/${url}`;
            }
          );
        } else {
          throw new Error(data.message || "Gagal menghapus data");
        }
      })
      .catch((err) => {
        hideLoader();
        Swal.fire("Gagal!", err.message, "error");
      });
  });
}

function cekModifyClientData(
  id,
  name,
  alamat,
  phone,
  server,
  paket,
  idpppoe,
  lat,
  long,
  local_ip
) {
  Swal.fire({
    title: "Detail Perubahan",
    html: `
    <div style="text-align:left; font-size:14px; line-height:1.5;">
      <h3 style="margin-bottom:5px;">Informasi Pelanggan</h3>
      <table>
        <tr><td><strong>Nama</strong></td><td>: ${name}</td></tr>
        <tr><td><strong>Alamat</strong></td><td>: ${alamat}</td></tr>
        <tr><td><strong>No HP</strong></td><td>: ${phone}</td></tr>
        <tr><td><strong>Latitude</strong></td><td>: ${lat}</td></tr>
        <tr><td><strong>Longitude</strong></td><td>: ${long}</td></tr>
      </table>

      <h3 style="margin-top:15px; margin-bottom:5px;">Informasi Server</h3>
      <table>
        <tr><td><strong>Server</strong></td><td>: ${server}</td></tr>
        <tr><td><strong>Paket</strong></td><td>: ${paket}</td></tr>
        <tr><td><strong>ID PPPoE</strong></td><td>: ${idpppoe}</td></tr>
        <tr><td><strong>Local IP</strong></td><td>: ${local_ip}</td></tr>
      </table>
    </div>
  `,
    icon: "info",
    confirmButtonColor: "#316ac4",
    confirmButtonText: "Konfirmasi perubahan",
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        title: "Konfirmasi Perubahan?",
        text: "Aksi ini tidak dapat dibatalkan!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#13542d",
        cancelButtonColor: "#aaa",
        confirmButtonText: "Ya!",
        cancelButtonText: "Batal",
      }).then((result) => {
        if (result.isConfirmed) {
          fetch(`/client/${id}/verification/`, {
            method: "POST",
            headers: {
              "X-CSRFToken": getCSRFToken(),
              Accept: "application/json",
            },
          })
            .then((res) => {
              // console.log("Status:", res.status);
              if (res.status === 401) {
                throw new Error(
                  "Anda harus login dahulu untuk melakukan verifikasi."
                );
              }
              if (!res.ok) {
                throw new Error(`Server error: ${res.status}`);
              }
              return res.json();
              //  return res.text();
            })
            .then((data) => {
              if (data.success) {
                Swal.fire("Sukses!", data.message, "success").then(() => {
                  location.href = "/client";
                });
              } else {
                Swal.fire("Gagal!", data.message, "error");
              }
            })
            .catch((err) => {
              //  console.error("Fetch error:", err);
              Swal.fire("Gagal!", err.message, "error");
            });
        }
      });
    }
  });
}

function toggleActivasiClient(clientId, name, status, url) {
  let msg;

  if (status === "false") {
    msg = "Activasi";
  } else {
    msg = "Nonaktifkan";
  }

  Swal.fire({
    title: `${msg} ${name}?`,
    text: "Aksi ini tidak dapat dibatalkan!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#13542d",
    cancelButtonColor: "#aaa",
    confirmButtonText: `Ya, ${msg}!`,
    cancelButtonText: "Batal",
  }).then((result) => {
    if (result.isConfirmed) {
      showMyLoader();
      fetch(`/client/${clientId}/toggle/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCSRFToken(),
          Accept: "application/json",
        },
      })
        .then(async (res) => {
          const data = await res.json(); // <-- parse JSON di sini

          if (res.status === 401) {
            Swal.fire({
              icon: "error",
              title: `Gagal ${msg} !`,
              text: data.message, // langsung pakai dari JSON
              confirmButtonText: "OK",
            });
            return;
          }

          if (!res.ok) {
            Swal.fire({
              icon: "error",
              title: `Gagal ${msg} !`,
              text: data.message || `Server error: ${res.status}`,
              confirmButtonText: "OK",
            });
            return;
          }

          if (data.success) {
            Swal.fire({
              icon: "success",
              title: `Client Berhasil di ${msg} !`,
              confirmButtonText: "OK",
            }).then(() => {
              if (url === "activation") {
                location.href = "/verifikasi";
              } else if (url === "detail-client") {
                location.href = `/client/id=${clientId}`;
              }
            });
          } else {
            Swal.fire({
              icon: "error",
              title: `Client Gagal di ${msg} !`,
              text: data.message || "Terjadi kesalahan.",
              confirmButtonText: "OK",
            });
          }
        })
        .catch((err) => {
          hideLoader();
          Swal.fire("Gagal!", err.message, "error");
        });
    }
  });
}

function test_connection(host, username, password) {
  // console.log(host, username, password);

  // munculin modal loading
  Swal.fire({
    title: "Testing koneksi...",
    allowOutsideClick: false,
    didOpen: () => {
      Swal.showLoading();
    },
  });

  fetch("/test-conn/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      host: host,
      username: username,
      password: password,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        Swal.fire({
          icon: "success",
          title: "Success",
          text: data.message,
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Failed to connect",
          text: data.message,
        });
      }
    })
    .catch((error) => {
      Swal.fire({
        icon: "error",
        title: "Failed to connect",
        text: error,
      });
    });
}

function addServerWithConfig() {
  Swal.fire({
    title: "Auto Config PPPoE Server",
    icon: "info",
    text: "Mohon Setting IP Address pada port ether yang digunakan untuk konfigurasi",
    footer: '<a href="#">Cara setting IP Address?</a>',
    showCancelButton: true,
    cancelButtonColor: "#aaa",
    cancelButtonText: "Batal",
    confirmButtonColor: "#13542d",
    confirmButtonText: "Lanjut",
    allowOutsideClick: false,
  }).then((firstStep) => {
    if (firstStep.isConfirmed) {
      Swal.fire({
        title: "Input Data",
        html: `
          <input id="host" class="swal2-input" placeholder="Host">
          <input id="config" type="number" class="swal2-input" placeholder="Port Ether">
          <input id="username" class="swal2-input" placeholder="New Username">
          <input id="oldPassword" type="password" class="swal2-input" placeholder="Old Password">
          <input id="password" type="password" class="swal2-input" placeholder="New Password">
          <input id="pppoe" type="number" class="swal2-input" placeholder="Port Ether Untuk Service PPPoE">
        `,
        focusConfirm: false,
        showCancelButton: true,
        cancelButtonColor: "#aaa",
        cancelButtonText: "Batal",
        confirmButtonColor: "#13542d",
        confirmButtonText: "Confirm!",
        allowOutsideClick: false,
        preConfirm: () => {
          const host = document.getElementById("host").value;
          const username = document.getElementById("username").value;
          const oldPassword = document.getElementById("oldPassword").value;
          const password = document.getElementById("password").value;
          const config = "ether" + document.getElementById("config").value;
          const pppoe = "ether" + document.getElementById("pppoe").value;

          if (!host || !username || !password || !config || !pppoe) {
            Swal.showValidationMessage("Semua field wajib diisi!");
            return false;
          }

          return { host, username, oldPassword, password, config, pppoe };
        },
      }).then((result) => {
        if (result.isConfirmed) {
          // ✅ Tampilkan loading
          Swal.fire({
            title: "Mengonfigurasi...",
            text: "Mohon tunggu sebentar",
            allowOutsideClick: false,
            allowEscapeKey: false,
            didOpen: () => {
              Swal.showLoading();
            },
          });

          // 🔥 Kirim ke Django
          fetch("/auto-conf/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
              host: result.value.host,
              hostEther: result.value.config,
              username: result.value.username,
              oldPassword: result.value.oldPassword,
              password: result.value.password,
              pppoeEther: result.value.pppoe,
            }),
          })
            .then((res) => res.json())
            .then((data) => {
              if (data.success) {
                Swal.fire({
                  icon: "success",
                  title: "Sukses 🚀",
                  text: data.message || "Konfigurasi berhasil dijalankan!",
                }).then(()=>{
                  location.href = `/server-list`;
                })
              } else {
                Swal.fire({
                  icon: "error",
                  title: "Gagal ❌",
                  text: data.message || "Terjadi kesalahan.",
                });
              }
            })
            .catch((err) => {
              Swal.fire({
                icon: "error",
                title: "Error ❌",
                text: err.message,
              });
            });
        }
      });
    }
  });
}

