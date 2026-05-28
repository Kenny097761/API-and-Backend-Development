const API_BASE = "http://127.0.0.1:8080";

document.addEventListener("DOMContentLoaded", function () {
  const selectEl = document.getElementById("orderSelect");
  const createBtn = document.getElementById("createBtn");
  const messageEl = document.getElementById("messageArea");

  function showMessage(text, kind) {
    messageEl.textContent = text;
    messageEl.classList.remove("is-success", "is-error");
    messageEl.classList.add(kind === "success" ? "is-success" : "is-error");
    messageEl.hidden = false;
  }

  function clearMessage() {
    messageEl.hidden = true;
    messageEl.textContent = "";
  }

  function setSelectPlaceholder(text) {
    selectEl.innerHTML = `<option value="">${text}</option>`;
  }

  function loadOrders() {
    fetch(`${API_BASE}/shipments/orders-available`, { credentials: "include" })
      .then(async (response) => {
        if (response.status === 401) {
          setSelectPlaceholder("Please log in");
          showMessage("Please log in as staff to create shipments.", "error");
          return null;
        }
        if (response.status === 403) {
          setSelectPlaceholder("Staff only");
          showMessage("Only staff can create shipments.", "error");
          return null;
        }
        if (!response.ok) {
          setSelectPlaceholder("Could not load orders");
          showMessage(`Could not load orders (HTTP ${response.status}).`, "error");
          return null;
        }
        return response.json();
      })
      .then((data) => {
        if (!data) return;
        const orders = data.orders || [];
        if (orders.length === 0) {
          setSelectPlaceholder("No paid orders awaiting shipment");
          return;
        }
        selectEl.innerHTML = orders
          .map((o) => {
            const name = `${o.first_name} ${o.last_name}`;
            const price = Number(o.total_price).toFixed(2);
            return `<option value="${o.order_id}">Order #${o.order_id} - ${name} - $${price}</option>`;
          })
          .join("");
      })
      .catch(() => {
        setSelectPlaceholder("Network error");
        showMessage("Network error. Is the backend running on port 8080?", "error");
      });
  }

  createBtn.addEventListener("click", function () {
    clearMessage();
    const orderId = parseInt(selectEl.value, 10);
    if (!orderId) {
      showMessage("Please select an order.", "error");
      return;
    }
    createBtn.disabled = true;
    fetch(`${API_BASE}/shipments/`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ order_id: orderId }),
    })
      .then(async (response) => {
        const body = await response.json().catch(() => ({}));
        if (response.status === 201) {
          const id = body.shipment ? body.shipment.shipment_id : "";
          showMessage(`Shipment #${id} created.`, "success");
          loadOrders();
        } else {
          showMessage(body.error || `Request failed (HTTP ${response.status}).`, "error");
        }
      })
      .catch(() => {
        showMessage("Network error. Is the backend running on port 8080?", "error");
      })
      .finally(() => {
        createBtn.disabled = false;
      });
  });

  loadOrders();
});
