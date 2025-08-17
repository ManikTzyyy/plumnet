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

    showLoader();

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
          Swal.fire("Terhapus!", "Data berhasil dihapus.", "success").then(() => {
            location.href = `/${url}`;
          });
        } else {
          throw new Error(data.message || "Gagal menghapus data");
        }
      })
      .catch((err) => {
        hideLoader(); // jangan showLoader lagi
        Swal.fire("Gagal!", err.message, "error");
      });
  });
}


function cekModifyClientData(id, name, alamat, phone, server, paket, idpppoe) {
  Swal.fire({
    title: "Detail Perubahan",
    html: `
    <div style="text-align:left; font-size:14px; line-height:1.5;">
      <h3 style="margin-bottom:5px;">Informasi Pelanggan</h3>
      <table>
        <tr><td><strong>Nama</strong></td><td>: ${name}</td></tr>
        <tr><td><strong>Alamat</strong></td><td>: ${alamat}</td></tr>
        <tr><td><strong>No HP</strong></td><td>: ${phone}</td></tr>
      </table>

      <h3 style="margin-top:15px; margin-bottom:5px;">Informasi Server</h3>
      <table>
        <tr><td><strong>Server</strong></td><td>: ${server}</td></tr>
        <tr><td><strong>Paket</strong></td><td>: ${paket}</td></tr>
        <tr><td><strong>ID PPPoE</strong></td><td>: ${idpppoe}</td></tr>
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
          Swal.fire("Gagal!", err.message, "error");
        });
    }
  });
}
