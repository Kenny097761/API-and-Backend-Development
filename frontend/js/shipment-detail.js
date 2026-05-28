const API_BASE = "http://127.0.0.1:8080";

const NEXT_STATUS = {
  pending: ["shipped"],
  shipped: ["delivered"],
};

document.addEventListener("DOMContentLoaded", function () {
  const detailsEl = document.getElementById("shipmentDetails");
  const updateSection = document.getElementById("updateSection");
  const statusSelect = document.getElementById("statusSelect");
  const updateBtn = document.getElementById("updateBtn");
  const cancelSection = document.getElementById("cancelSection");
  const cancelBtn = document.getElementById("cancelBtn");
  const messageEl = document.getElementById("messageArea");

  const params = new URLSearchParams(window.location.search);
  const shipmentId = parseInt(params.get("id"), 10);

  updateSection.style.display = "none";
  cancelSection.style.display = "none";

  function showMessage(text) {
    messageEl.textContent = text;
    messageEl.hidden = false;
  }

  function clearMessage() {
    messageEl.hidden = true;
    messageEl.textContent = "";
  }

  function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function statusClass(status) {
    const known = ["pending", "shipped", "delivered", "cancelled"];
    return known.includes(status) ? `status-${status}` : "status-pending";
  }

  function formatAddress(s) {
    return `${escapeHtml(s.street_number)} ${escapeHtml(s.street_name)}, ${escapeHtml(s.suburb)} ${escapeHtml(s.postcode)}`;
  }

  function renderDetails(s) {
    detailsEl.innerHTML = `
      <article class="shipment-card">
        <div class="shipment-card-header">
          <span class="shipment-card-title">Shipment #${escapeHtml(s.shipment_id)}</span>
          <span class="status-badge ${statusClass(s.status)}">${escapeHtml(s.status)}</span>
        </div>
        <div class="shipment-card-row"><span class="label">Order:</span>#${escapeHtml(s.order_id)}</div>
        <div class="shipment-card-row"><span class="label">Assigned staff:</span>${escapeHtml(s.staff_name) || "-"}</div>
        <div class="shipment-card-row"><span class="label">Delivery address:</span>${formatAddress(s)}</div>
      </article>
    `;
  }

  function hideUpdateForm() {
    updateSection.style.display = "none";
    updateSection.hidden = true;
    statusSelect.innerHTML = "";
  }

  function showUpdateForm(nextOptions) {
    statusSelect.innerHTML = nextOptions
      .map((s) => `<option value="${s}">${s}</option>`)
      .join("");
    updateSection.hidden = false;
    updateSection.style.display = "";
  }

  function nextStatusesFor(status) {
    return NEXT_STATUS[status] ? NEXT_STATUS[status].slice() : [];
  }

  function isAssignedStaff(session, shipment) {
    return (
      session &&
      session.logged_in &&
      session.is_staff &&
      shipment.staff_id === session.user_id
    );
  }

  function maybeShowUpdateForm(session, shipment) {
    const nextOptions = nextStatusesFor(shipment.status);
    if (!isAssignedStaff(session, shipment) || nextOptions.length === 0) {
      hideUpdateForm();
      return;
    }
    showUpdateForm(nextOptions);
  }

  function maybeShowCancelButton(session, shipment) {
    if (isAssignedStaff(session, shipment) && shipment.status === "pending") {
      cancelSection.hidden = false;
      cancelSection.style.display = "";
    } else {
      cancelSection.hidden = true;
      cancelSection.style.display = "none";
    }
  }

  function renderShipmentState(session, shipment) {
    renderDetails(shipment);
    maybeShowUpdateForm(session, shipment);
    maybeShowCancelButton(session, shipment);
  }

  function loadShipment() {
    clearMessage();
    return Promise.all([
      fetch(`${API_BASE}/shipments/me/session`, { credentials: "include" }).then((r) =>
        r.json(),
      ),
      fetch(`${API_BASE}/shipments/${shipmentId}`, { credentials: "include" }).then(
        async (r) => {
          if (r.status === 401) return { error: "auth", status: 401 };
          if (r.status === 403) return { error: "forbidden", status: 403 };
          if (r.status === 404) return { error: "notfound", status: 404 };
          if (!r.ok) return { error: "http", status: r.status };
          return r.json();
        },
      ),
    ])
      .then(([session, shipmentResp]) => {
        if (shipmentResp.error) {
          const msg = {
            auth: "Please log in to view this shipment.",
            forbidden: "You are not allowed to view this shipment.",
            notfound: "Shipment not found.",
          }[shipmentResp.error] || `Could not load shipment (HTTP ${shipmentResp.status}).`;
          showMessage(msg);
          hideUpdateForm();
          maybeShowCancelButton(null, {});
          return;
        }
        renderShipmentState(session, shipmentResp.shipment);
      })
      .catch(() => {
        showMessage("Network error. Is the backend running on port 8080?");
      });
  }

  updateBtn.addEventListener("click", function () {
    clearMessage();
    const newStatus = statusSelect.value;
    if (!newStatus) return;
    updateBtn.disabled = true;
    fetch(`${API_BASE}/shipments/${shipmentId}`, {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    })
      .then(async (response) => {
        const body = await response.json().catch(() => ({}));
        if (response.ok) {
          clearMessage();
          renderShipmentState(
            { logged_in: true, is_staff: true, user_id: body.shipment.staff_id },
            body.shipment,
          );
          showMessage(`Status updated to "${body.shipment.status}".`);
        } else {
          showMessage(body.error || "Update failed.");
        }
      })
      .catch(() => {
        showMessage("Network error. Is the backend running on port 8080?");
      })
      .finally(() => {
        updateBtn.disabled = false;
      });
  });

  cancelBtn.addEventListener("click", function () {
    const confirmed = window.confirm(
      "Are you sure? This will cancel the shipment. This cannot be undone.",
    );
    if (!confirmed) return;
    clearMessage();
    cancelBtn.disabled = true;
    fetch(`${API_BASE}/shipments/${shipmentId}`, {
      method: "DELETE",
      credentials: "include",
    })
      .then(async (response) => {
        const body = await response.json().catch(() => ({}));
        if (response.ok) {
          return loadShipment().then(() => showMessage("Shipment cancelled."));
        }
        showMessage(body.error || `Cancel failed (HTTP ${response.status}).`);
      })
      .catch(() => {
        showMessage("Network error. Is the backend running on port 8080?");
      })
      .finally(() => {
        cancelBtn.disabled = false;
      });
  });

  if (!shipmentId) {
    showMessage("No shipment id provided in the URL (expected ?id=...).");
  } else {
    loadShipment();
  }
});
