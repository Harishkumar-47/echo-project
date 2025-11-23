async function loadDrives() {
  try {
    const res = await fetch("/api/drives");
    const data = await res.json();
    const select = document.getElementById("device_path");
    select.innerHTML = "";

    data.drives.forEach(drive => {
      const option = document.createElement("option");
      option.value = drive;
      option.textContent = drive;
      select.appendChild(option);
    });
  } catch (err) {
    console.error("Failed to load drives:", err);
  }
}

async function scanUnified() {
  const mode = document.getElementById("scan_mode").value;
  const device_path = document.getElementById("device_path").value.trim();
  const fileType = document.getElementById("file_type").value.trim();
  const start_date = document.getElementById("start_date").value;
  const end_date = document.getElementById("end_date").value;
  const nameFilter = document.getElementById("name_filter").value.trim();
  const minSize = parseInt(document.getElementById("min_size").value) || 512;
  const statusEl = document.getElementById("status");

  statusEl.textContent = `Scanning (${mode})...`;

  let endpoint = mode === "deleted" ? "/api/deleted_scan" : "/api/scan";
  let payload = {
    image_path: device_path,
    extension: fileType || "jpg",
    start_date: start_date || null,
    end_date: end_date || null
  };

  if (mode === "deleted") {
    payload = {
      image_path: device_path,
      extensions: fileType ? [fileType] : [],
      start_date: start_date || null,
      end_date: end_date || null,
      min_size: minSize,
      name_filter: nameFilter || null
    };
  }

  try {
    const resp = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await resp.json();
    if (!resp.ok) {
      statusEl.textContent = "Error: " + (data.error || "Unknown error");
      return;
    }

    statusEl.textContent = `Recovered ${data.count} file(s).`;
    renderResults(data.results);
  } catch (e) {
    statusEl.textContent = "Error: " + e.message;
  }
}

function renderResults(results) {
  const tbody = document.querySelector("#results-table tbody");
  tbody.innerHTML = "";
  results.forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.filename}</td>
      <td>${r.type}</td>
      <td>${(r.size / 1024).toFixed(1)} KB</td>
      <td>${r.mtime || "—"}</td>
      <td><a href="/downloads/${encodeURIComponent(r.filename)}" download>Download</a></td>
    `;
    tbody.appendChild(tr);
  });
}
function runDeepCarve(imagePath, tool = "photorec") {
    fetch("/api/deep_carve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_path: imagePath, tool: tool })
    })
    .then(res => res.json())
    .then(data => {
        console.log("Deep carve results:", data.results);
        // TODO: Display results in your UI
    });
}

document.addEventListener("DOMContentLoaded", () => {
  loadDrives();
  document.getElementById("scan-form").addEventListener("submit", (e) => {
    e.preventDefault();
    scanUnified();
  });
});

