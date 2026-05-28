const API_BASE = "http://127.0.0.1:8080";

const STATUS_CLASSES = {
  pending: "status-pending",
  shipped: "status-shipped",
  delivered: "status-delivered",
  cancelled: "status-cancelled",
};

const ESC_MAP = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

const state = {
  shipments: [],
  filter: "all",
  showCustomer: false,
};

function esc(value) {
  if (value === null || value === undefined) return "";
  return String(value).replace(/[&<>"']/g, (ch) => ESC_MAP[ch]);
}

function buildCard(s, opts) {
  const showCustomer = opts && opts.showCustomer;
  const cls = STATUS_CLASSES[s.status] || "status-pending";
  const address = `${esc(s.street_number)} ${esc(s.street_name)}, ${esc(s.suburb)} ${esc(s.postcode)}`;
  const staff = s.staff_name ? esc(s.staff_name) : "-";
  const customerRow = showCustomer
    ? `<div class="shipment-card-row"><span class="label">Customer:</span>${esc(s.customer_name) || "-"}</div>`
    : "";
  return `
    <article class="shipment-card">
      <div class="shipment-card-header">
        <span class="shipment-card-title">Shipment #${esc(s.shipment_id)}</span>
        <span class="status-badge ${cls}">${esc(s.status)}</span>
      </div>
      ${customerRow}
      <div class="shipment-card-row"><span class="label">Order:</span>#${esc(s.order_id)}</div>
      <div class="shipment-card-row"><span class="label">Assigned staff:</span>${staff}</div>
      <div class="shipment-card-row"><span class="label">Delivery address:</span>${address}</div>
      <div class="shipment-card-row"><a href="./shipment-detail.html?id=${encodeURIComponent(s.shipment_id)}">View details</a></div>
    </article>
  `;
}

function render() {
  const listEl = document.getElementById("shipmentsList");
  const emptyEl = document.getElementById("emptyState");

  const filtered =
    state.filter === "all"
      ? state.shipments
      : state.shipments.filter((s) => s.status === state.filter);

  if (filtered.length === 0) {
    listEl.innerHTML = "";
    emptyEl.textContent =
      state.shipments.length === 0
        ? "No shipments yet."
        : `No ${state.filter} shipments.`;
    emptyEl.hidden = false;
    return;
  }

  emptyEl.hidden = true;
  listEl.innerHTML = filtered
    .map((s) => buildCard(s, { showCustomer: state.showCustomer }))
    .join("");
}

function setupTabs() {
  const tabsEl = document.getElementById("shipmentsTabs");
  if (!tabsEl) return;
  tabsEl.addEventListener("click", (event) => {
    const btn = event.target.closest(".shipments-tab");
    if (!btn) return;
    const status = btn.dataset.status;
    if (!status || status === state.filter) return;
    state.filter = status;
    tabsEl
      .querySelectorAll(".shipments-tab")
      .forEach((b) => b.classList.toggle("is-active", b === btn));
    render();
  });
}

async function loadShipments() {
  const headingEl = document.getElementById("pageHeading");
  const errorEl = document.getElementById("errorMessage");

  let session;
  try {
    const sessionRes = await fetch(`${API_BASE}/shipments/me/session`, {
      credentials: "include",
    });
    session = await sessionRes.json();
  } catch (err) {
    errorEl.textContent = "Network error. Is the backend running on port 8080?";
    errorEl.hidden = false;
    return;
  }

  if (!session.logged_in) {
    errorEl.textContent = "Please log in to view shipments.";
    errorEl.hidden = false;
    return;
  }

  const isStaff = session.is_staff;
  state.showCustomer = isStaff;
  headingEl.textContent = isStaff ? "All Shipments" : "My Shipments";
  const endpoint = isStaff ? `${API_BASE}/shipments/` : `${API_BASE}/shipments/my`;

  try {
    const response = await fetch(endpoint, { credentials: "include" });

    if (response.status === 401) {
      errorEl.textContent = "Please log in to view shipments.";
      errorEl.hidden = false;
      return;
    }
    if (!response.ok) {
      errorEl.textContent = `Could not load shipments (HTTP ${response.status}).`;
      errorEl.hidden = false;
      return;
    }

    const data = await response.json();
    state.shipments = data.shipments || [];
    render();
  } catch (err) {
    errorEl.textContent = "Network error. Is the backend running on port 8080?";
    errorEl.hidden = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  loadShipments();
});
