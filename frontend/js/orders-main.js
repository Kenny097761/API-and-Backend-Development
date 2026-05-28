const API_BASE = "http://127.0.0.1:8080";


let userRole = sessionStorage.getItem("userRole") || null;

function showError(msg) {
    document.getElementById("errorMessage").innerHTML = msg;
    document.getElementById("errorMessage").style.display = "block";
}

async function initPage() {

    const res = await fetch(API_BASE + "/api/user/info", { credentials: "include" });
    if (res.status === 401) {
        window.location.href = "login.html";
        return;
    }
    const data = await res.json();
    userRole = data.role;
    sessionStorage.setItem("userRole", userRole);

    if (userRole === "customer") {
        document.getElementById("createOrderSection").style.display = "block";
        document.getElementById("searchSection").style.display = "flex";
        document.getElementById("ordersTitle").innerHTML = "My Orders";
        loadDevices();
    } else {
        document.getElementById("ordersTitle").innerHTML = "All Customer Orders";
    }
    loadOrders();
}

async function loadOrders() {
    const url = userRole === "customer" ? API_BASE + "/orders/customer" : API_BASE + "/orders/all";
    const response = await fetch(url, { credentials: "include" });
    const orders = await response.json();
    const container = document.getElementById("ordersList");
    container.innerHTML = "";
    if (!orders || orders.length === 0) {
        container.innerHTML = '<div class="empty-message">No orders found</div>';
        return;
    }
    for (let i = 0; i < orders.length; i++) {
        const r = await fetch(API_BASE + "/orders/" + orders[i].order_id, { credentials: "include" });
        const detail = await r.json();
        if (!detail.error) {
            detail.order.items = detail.items;
            container.appendChild(createOrderCard(detail.order));
        }
    }
}

function createOrderCard(order) {
    const div = document.createElement("div");
    div.className = "order-card";
    const items = order.items || [];
    let itemsHtml = "";
    for (let i = 0; i < items.length; i++) {
        const name = items[i].device_name || items[i].name || "Device";
        itemsHtml += '<div class="order-item">' + items[i].quantity + " x " + name + " — $" + items[i].total_price + "</div>";
    }
    const statusClass = "status-" + order.status.replace(/ /g, "-");
    div.innerHTML =
        '<div class="order-header">' +
        '<span class="order-id">Order #' + order.order_id + "</span>" +
        '<span class="status ' + statusClass + '">' + order.status + "</span>" +
        "</div>" +
        '<div class="order-date">' + order.created_at + "</div>" +
        '<div class="order-items">' + (itemsHtml || "<div>No items</div>") + "</div>" +
        '<div class="order-total">Total: $' + order.total_price + "</div>";

    if (userRole === "customer" && order.status === "saved") {
        const editBtn = document.createElement("button");
        editBtn.innerHTML = "Edit Order";
        editBtn.className = "edit-order-btn";
        editBtn.addEventListener("click", function () { showEditForm(order); });
        div.appendChild(editBtn);

        const cancelBtn = document.createElement("button");
        cancelBtn.innerHTML = "Cancel Order";
        cancelBtn.className = "cancel-order-btn";
        cancelBtn.addEventListener("click", function () { cancelOrder(order.order_id); });
        div.appendChild(cancelBtn);
    }
    return div;
}

async function loadDevices() {
    const response = await fetch(API_BASE + "/api/devices", { credentials: "include" });
    const devices = await response.json();
    const container = document.getElementById("devicesList");
    container.innerHTML = "";
    for (let i = 0; i < devices.length; i++) {
        const d = devices[i];
        container.innerHTML += `
            <div class="device-card">
                <div class="device-info">
                    <div class="device-name">${d.name}</div>
                    <div class="device-details">${d.type} | Stock: ${d.stock}</div>
                    <div class="device-price">$${d.unit_price}</div>
                </div>
                <div class="add-to-cart">
                    <input type="number" id="qty_${d.device_id}" min="1" max="${d.stock}" value="1">
                    <button onclick="addToCart(${d.device_id}, document.getElementById('qty_${d.device_id}').value, '${d.name}', ${d.unit_price}, ${d.stock})">Add to Order</button>
                </div>
            </div>`;
    }
}

async function searchOrders() {
    document.getElementById("errorMessage").style.display = "none";
    const orderId = document.getElementById("searchOrderId").value.trim();
    const date = document.getElementById("searchDate").value.trim();

    if (!orderId && !date) {
        loadOrders();
        return;
    }

    let orders = [];
    if (orderId) {
        const r = await fetch(API_BASE + "/orders/search/" + orderId, { credentials: "include" });
        const data = await r.json();
        if (Array.isArray(data)) orders = data;
    } else if (date) {
        const r = await fetch(API_BASE + "/orders/search_by_date/" + date, { credentials: "include" });
        const data = await r.json();
        if (Array.isArray(data)) orders = data;
    }

    const container = document.getElementById("ordersList");
    container.innerHTML = "";
    if (!orders || orders.length === 0) {
        container.innerHTML = '<div class="empty-message">No orders found</div>';
        return;
    }
    for (let i = 0; i < orders.length; i++) {
        const r = await fetch(API_BASE + "/orders/" + orders[i].order_id, { credentials: "include" });
        const detail = await r.json();
        if (!detail.error) {
            detail.order.items = detail.items;
            container.appendChild(createOrderCard(detail.order));
        }
    }
}

function clearSearch() {
    document.getElementById("searchOrderId").value = "";
    document.getElementById("searchDate").value = "";
    document.getElementById("errorMessage").style.display = "none";
    loadOrders();
}

document.getElementById("homeLink").addEventListener("click", function (e) {
    e.preventDefault();
    window.location.href = "login.html";
});

document.getElementById("logoutBtn").addEventListener("click", function () {
    fetch(API_BASE + "/logout", { method: "POST", credentials: "include" })
        .then(function () {
            sessionStorage.clear();
            window.location.href = "login.html";
        });
});

document.getElementById("showFormBtn").addEventListener("click", showCreateForm);
document.getElementById("submitOrderBtn").addEventListener("click", submitOrder);
document.getElementById("cancelFormBtn").addEventListener("click", hideCreateForm);
document.getElementById("searchBtn").addEventListener("click", searchOrders);
document.getElementById("clearSearchBtn").addEventListener("click", clearSearch);

initPage();
