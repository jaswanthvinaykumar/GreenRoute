/**
 * GreenRoute - Client-side Reactive Controller
 */

let currentData = null;
let activeLogText = "";

document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
});

function setupEventListeners() {
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("file-input");
  const btnLoadSample = document.getElementById("btn-load-sample");
  const btnEmptySample = document.getElementById("btn-empty-sample");
  const btnReoptimize = document.getElementById("btn-reoptimize");
  const btnOpenCert = document.getElementById("btn-open-cert");

  // Slider feedback
  const sliderRepl = document.getElementById("input-replication");
  const valRepl = document.getElementById("val-replication");
  sliderRepl.addEventListener("input", (e) => {
    valRepl.textContent = `${e.target.value}x`;
  });

  const sliderRet = document.getElementById("input-retention");
  const valRet = document.getElementById("val-retention");
  sliderRet.addEventListener("input", (e) => {
    valRet.textContent = `${e.target.value} Days`;
  });

  const sliderFleet = document.getElementById("input-fleet");
  const valFleet = document.getElementById("val-fleet");
  if (sliderFleet && valFleet) {
    sliderFleet.addEventListener("input", (e) => {
      valFleet.textContent = `${e.target.value} GB / Day`;
      const bannerScale = document.getElementById("banner-fleet-scale");
      if (bannerScale) bannerScale.textContent = `${e.target.value} GB/day`;
    });
  }

  // Drag and Drop
  ["dragenter", "dragover"].forEach(evtName => {
    dropZone.addEventListener(evtName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add("drag-over");
    });
  });

  ["dragleave", "drop"].forEach(evtName => {
    dropZone.addEventListener(evtName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove("drag-over");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });

  // Buttons
  btnLoadSample.addEventListener("click", () => triggerSampleRun(5000));
  if (btnEmptySample) {
    btnEmptySample.addEventListener("click", () => triggerSampleRun(5000));
  }

  btnReoptimize.addEventListener("click", () => {
    if (activeLogText) {
      runOptimizationOnText(activeLogText);
    } else {
      triggerSampleRun(5000);
    }
  });

  btnOpenCert.addEventListener("click", openCertModal);

  // Auto-refresh certificate if org inputs change
  document.getElementById("cert-org-name").addEventListener("input", debounce(updateCertificateIframe, 400));
  document.getElementById("cert-sys-name").addEventListener("input", debounce(updateCertificateIframe, 400));
}

function showLoading(show = true, title = "Sanitizing & Optimizing Telemetry...") {
  const overlay = document.getElementById("loading-overlay");
  document.getElementById("loading-title").textContent = title;
  if (show) {
    overlay.classList.remove("hidden");
  } else {
    overlay.classList.add("hidden");
  }
}

function getParameters() {
  return {
    region: document.getElementById("select-region").value,
    storage_type: document.getElementById("select-storage").value,
    replication_factor: parseInt(document.getElementById("input-replication").value, 10),
    retention_days: parseInt(document.getElementById("input-retention").value, 10),
    filter_healthchecks: document.getElementById("chk-healthchecks").checked,
    dedup_repeats: document.getElementById("chk-dedup").checked,
    mask_pii: document.getElementById("chk-pii").checked,
    normalize_user_agents: document.getElementById("chk-ua").checked,
    fleet_daily_gb: parseFloat(document.getElementById("input-fleet") ? document.getElementById("input-fleet").value : 50),
  };
}

async function triggerSampleRun(lines = 5000) {
  showLoading(true, `Generating ${lines.toLocaleString()} Production Log Lines...`);
  try {
    const params = getParameters();
    params.lines = lines;

    const res = await fetch("/api/generate-sample", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });

    const data = await res.json();
    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    currentData = data;
    renderDashboard(data);
  } catch (err) {
    console.error(err);
    alert("Failed to run sample generation: " + err.message);
  } finally {
    showLoading(false);
  }
}

async function handleFileUpload(file) {
  showLoading(true, `Reading and analyzing ${file.name}...`);
  try {
    const formData = new FormData();
    formData.append("file", file);

    const params = getParameters();
    for (const [key, val] of Object.entries(params)) {
      formData.append(key, val);
    }

    const res = await fetch("/api/optimize", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    currentData = data;
    renderDashboard(data);
  } catch (err) {
    console.error(err);
    alert("Failed to upload and optimize log: " + err.message);
  } finally {
    showLoading(false);
  }
}

async function runOptimizationOnText(text) {
  showLoading(true, "Applying new parameters & re-optimizing...");
  try {
    const params = getParameters();
    params.log_text = text;

    const res = await fetch("/api/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });

    const data = await res.json();
    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    currentData = data;
    renderDashboard(data);
  } catch (err) {
    console.error(err);
    alert("Optimization error: " + err.message);
  } finally {
    showLoading(false);
  }
}

function renderDashboard(data) {
  // Show results view, hide empty state
  document.getElementById("empty-state").classList.add("hidden");
  document.getElementById("results-view").classList.remove("hidden");
  document.getElementById("btn-open-cert").disabled = false;

  const savings = data.carbon_savings || {};
  const bytes = savings.bytes || {};
  const emissions = savings.emissions || {};
  const energy = savings.energy || {};
  const financial = savings.financial || {};
  const equiv = savings.equivalencies || {};
  const stats = data.cleaner_stats || {};
  const analytics = data.analytics || {};

  // 1. KPI Cards
  document.getElementById("kpi-badge-reduction").textContent = `-${bytes.reduction_percentage}%`;
  document.getElementById("kpi-space-saved").textContent = bytes.saved_human || "0 B";
  document.getElementById("kpi-storage-details").textContent = 
    `Raw: ${bytes.original_human} ➔ Optimized: ${bytes.optimized_human}`;

  document.getElementById("kpi-co2-saved").textContent = emissions.total_co2_formatted || "0 g";
  document.getElementById("kpi-energy-saved").textContent = energy.kwh_saved_formatted || "0 kWh";
  document.getElementById("kpi-cost-saved").textContent = `$${(financial.annual_cost_saved_usd || 0).toFixed(2)}`;

  // 2. Equivalency Pills
  document.getElementById("eq-phones").textContent = (equiv.smartphones_charged || 0).toLocaleString();
  document.getElementById("eq-car").textContent = `${(equiv.km_driven_offset || 0).toFixed(1)} km`;
  document.getElementById("eq-bottles").textContent = (equiv.plastic_bottles_equivalent || 0).toLocaleString();

  // Enterprise Fleet Scaled Banner
  const proj = savings.projections || {};
  const bannerScale = document.getElementById("banner-fleet-scale");
  if (bannerScale) bannerScale.textContent = `${proj.fleet_daily_gb || 50} GB/day`;

  const entCo2 = document.getElementById("ent-co2");
  if (entCo2) entCo2.textContent = `${(proj.fleet_annual_co2_metric_tons || 0).toFixed(2)} Tons`;

  const entKwh = document.getElementById("ent-kwh");
  if (entKwh) entKwh.textContent = `${((proj.fleet_annual_kwh || 0) / 1000).toFixed(2)} MWh`;

  const entCost = document.getElementById("ent-cost");
  if (entCost) entCost.textContent = `$${(proj.fleet_annual_cost_usd || 0).toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}`;

  const entTrees = document.getElementById("ent-trees");
  if (entTrees) entTrees.textContent = `${Math.round(proj.fleet_trees_offset || 0).toLocaleString()} Trees`;

  // 3. Multi-Algorithm Codec Visualizer
  renderCodecBenchmarks(data.benchmarks || []);

  // 4. Noise & Analytics
  document.getElementById("noise-healthchecks").textContent = `${(stats.healthchecks_filtered || 0).toLocaleString()} lines`;
  document.getElementById("noise-errors").textContent = `${(stats.repeated_lines_collapsed || 0).toLocaleString()} lines`;
  document.getElementById("noise-pii").textContent = `${(stats.pii_instances_masked || 0).toLocaleString()} items`;
  document.getElementById("noise-ua").textContent = `${(stats.user_agents_compacted || 0).toLocaleString()} strings`;

  renderStatusPills(analytics.status_groups || {});
  renderTopEndpoints(analytics.top_endpoints || []);

  // 5. Raw vs Cleaned Diff Preview
  const rawPre = document.getElementById("raw-log-preview");
  const cleanPre = document.getElementById("clean-log-preview");
  rawPre.textContent = (data.raw_preview || []).slice(0, 100).join("\n");
  cleanPre.textContent = (data.cleaned_preview || []).slice(0, 100).join("\n");
}

function renderCodecBenchmarks(benchmarks) {
  const container = document.getElementById("codec-bars");
  const tbody = document.getElementById("benchmark-table-body");
  container.innerHTML = "";
  tbody.innerHTML = "";

  if (!benchmarks || benchmarks.length === 0) return;

  const rawItem = benchmarks.find(b => b.id === "raw") || benchmarks[0];
  const maxBytes = Math.max(...benchmarks.map(b => b.size_bytes), 1);

  benchmarks.forEach(item => {
    // Bar Chart Row
    const row = document.createElement("div");
    row.className = "codec-bar-row";

    const widthPct = Math.max(5, (item.size_bytes / maxBytes) * 100);

    let fillClass = "fill-clean";
    if (item.id === "raw") fillClass = "fill-raw";
    else if (item.id === "raw_gzip" || item.id === "green_gzip") fillClass = "fill-gzip";
    else if (item.id === "green_bz2") fillClass = "fill-bz2";
    else if (item.id === "green_lzma") fillClass = "fill-lzma";

    row.innerHTML = `
      <div class="codec-name">${item.name}</div>
      <div class="codec-track">
        <div class="codec-fill ${fillClass}" style="width: ${widthPct.toFixed(1)}%;">
          ${item.reduction_pct > 0 ? `-${item.reduction_pct}%` : 'Baseline'}
        </div>
      </div>
      <div class="codec-size">${formatBytes(item.size_bytes)}</div>
    `;
    container.appendChild(row);

    // Table Row
    const tr = document.createElement("tr");

    let tagBadge = `<span class="tag-badge tag-neutral">${item.tag}</span>`;
    if (item.is_recommended) {
      tagBadge = `<span class="tag-badge tag-best">⭐ Recommended (Max Green)</span>`;
    } else if (item.is_baseline) {
      tagBadge = `<span class="tag-badge tag-danger">Worst Carbon</span>`;
    }

    tr.innerHTML = `
      <td><strong>${item.name}</strong></td>
      <td>${formatBytes(item.size_bytes)}</td>
      <td><span style="color: ${item.reduction_pct > 0 ? 'var(--emerald)' : 'inherit'}">${item.reduction_pct > 0 ? `-${item.reduction_pct}%` : '0%'}</span></td>
      <td>${item.duration_ms > 0 ? `${item.duration_ms} ms` : '—'}</td>
      <td>${item.throughput_mb_s > 0 ? `${item.throughput_mb_s} MB/s` : '—'}</td>
      <td>${tagBadge}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderStatusPills(groups) {
  const container = document.getElementById("status-pills");
  container.innerHTML = `
    <div class="status-pill status-2xx">
      <strong>${(groups["2xx_success"] || 0).toLocaleString()}</strong>
      <span>2xx Success</span>
    </div>
    <div class="status-pill status-3xx">
      <strong>${(groups["3xx_redirect"] || 0).toLocaleString()}</strong>
      <span>3xx Redirect</span>
    </div>
    <div class="status-pill status-4xx">
      <strong>${(groups["4xx_client_err"] || 0).toLocaleString()}</strong>
      <span>4xx Client Err</span>
    </div>
    <div class="status-pill status-5xx">
      <strong>${(groups["5xx_server_err"] || 0).toLocaleString()}</strong>
      <span>5xx Outage</span>
    </div>
  `;
}

function renderTopEndpoints(endpoints) {
  const container = document.getElementById("endpoints-list");
  container.innerHTML = "";
  if (!endpoints || endpoints.length === 0) {
    container.innerHTML = `<div class="text-muted" style="font-size: 12px;">No endpoints detected.</div>`;
    return;
  }

  endpoints.slice(0, 6).forEach(ep => {
    const row = document.createElement("div");
    row.className = "endpoint-row";
    row.innerHTML = `
      <span class="endpoint-path" title="${ep.path}">${ep.path}</span>
      <span class="endpoint-count">${ep.count.toLocaleString()} calls (${ep.pct}%)</span>
    `;
    container.appendChild(row);
  });
}

function switchLogTab(mode) {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(t => t.classList.remove("active"));
  event.target.classList.add("active");

  const rawPane = document.getElementById("diff-raw-pane");
  const cleanPane = document.getElementById("diff-clean-pane");
  const container = document.getElementById("log-diff-container");

  if (mode === "diff") {
    container.style.gridTemplateColumns = "1fr 1fr";
    rawPane.style.display = "block";
    cleanPane.style.display = "block";
  } else if (mode === "cleaned") {
    container.style.gridTemplateColumns = "1fr";
    rawPane.style.display = "none";
    cleanPane.style.display = "block";
  } else if (mode === "raw") {
    container.style.gridTemplateColumns = "1fr";
    rawPane.style.display = "block";
    cleanPane.style.display = "none";
  }
}

function downloadArchive(codec) {
  window.location.href = `/api/download/${codec}`;
}

function openCertModal() {
  document.getElementById("cert-modal").classList.remove("hidden");
  updateCertificateIframe();
}

function closeCertModal() {
  document.getElementById("cert-modal").classList.add("hidden");
}

async function updateCertificateIframe() {
  const org = document.getElementById("cert-org-name").value;
  const sys = document.getElementById("cert-sys-name").value;

  try {
    const res = await fetch("/api/certificate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ organization_name: org, system_name: sys }),
    });

    const html = await res.text();
    const iframe = document.getElementById("cert-iframe");
    iframe.srcdoc = html;
  } catch (err) {
    console.error("Failed to load certificate preview:", err);
  }
}

function printCertIframe() {
  const iframe = document.getElementById("cert-iframe");
  if (iframe && iframe.contentWindow) {
    iframe.contentWindow.print();
  }
}

function formatBytes(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function debounce(fn, ms) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}
