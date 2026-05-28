let orderItems = [];
let editingOrderId = null;

function addToCart(deviceId, quantity, deviceName, devicePrice, deviceStock) {
    quantity = Number(quantity);
    if (quantity < 1) { showError("Quantity must be at least 1"); return; }
    if (quantity > deviceStock) { showError("Only " + deviceStock + " in stock"); return; }

    for (let i = 0; i < orderItems.length; i++) {
        if (orderItems[i].device_id === deviceId) {
            if (orderItems[i].quantity + quantity > deviceStock) { showError("Not enough stock"); return; }
            orderItems[i].quantity += quantity;
            updateCartDisplay();
            return;
        }
    }
    orderItems.push({ device_id: deviceId, name: deviceName, quantity: quantity, price: devicePrice });
    updateCartDisplay();
}

function removeFromCart(index) {
    let newItems = [];
    for (let i = 0; i < orderItems.length; i++) {
        if (i !== index) { newItems.push(orderItems[i]); }
    }
    orderItems = newItems;
    updateCartDisplay();
}

function updateCartDisplay() {
    const container = document.getElementById("cartItems");
    const totalSpan = document.getElementById("cartTotal");
    if (orderItems.length === 0) {
        container.innerHTML = '<div class="empty-message">Cart is empty</div>';
        totalSpan.innerHTML = "0";
        return;
    }
    let total = 0;
    container.innerHTML = "";
    for (let i = 0; i < orderItems.length; i++) {
        const item = orderItems[i];
        const lineTotal = item.quantity * item.price;
        total += lineTotal;
        const div = document.createElement("div");
        div.className = "cart-item";
        div.innerHTML = "<span>" + item.quantity + " x " + item.name + " = $" + lineTotal + "</span>";
        const btn = document.createElement("button");
        btn.innerHTML = "Remove";
        btn.className = "remove-btn";
        btn.addEventListener("click", (function (idx) { return function () { removeFromCart(idx); }; })(i));
        div.appendChild(btn);
        container.appendChild(div);
    }
    totalSpan.innerHTML = total;
}

function showCreateForm() {
    editingOrderId = null;
    document.getElementById("orderForm").style.display = "block";
    document.getElementById("showFormBtn").style.display = "none";
    document.querySelector("#orderForm h2").innerHTML = "New Order";
    document.getElementById("submitOrderBtn").innerHTML = "Submit Order";
    orderItems = [];
    updateCartDisplay();
}

function showEditForm(order) {
    editingOrderId = order.order_id;
    document.getElementById("orderForm").style.display = "block";
    document.getElementById("showFormBtn").style.display = "none";
    document.querySelector("#orderForm h2").innerHTML = "Edit Order #" + order.order_id;
    document.getElementById("submitOrderBtn").innerHTML = "Save Changes";
    orderItems = [];
    const items = order.items || [];
    for (let i = 0; i < items.length; i++) {
        orderItems.push({
            device_id: items[i].device_id,
            name: items[i].device_name || items[i].name || "Device",
            quantity: items[i].quantity,
            price: items[i].unit_price
        });
    }
    updateCartDisplay();
}

function hideCreateForm() {
    document.getElementById("orderForm").style.display = "none";
    document.getElementById("showFormBtn").style.display = "inline-block";
    editingOrderId = null;
    orderItems = [];
    updateCartDisplay();
}

async function submitOrder() {
    if (orderItems.length === 0) { showError("Please add at least one item"); return; }
    const items = [];
    for (let i = 0; i < orderItems.length; i++) {
        items.push({ device_id: orderItems[i].device_id, quantity: orderItems[i].quantity });
    }

    let response;
    if (editingOrderId !== null) {
        response = await fetch(API_BASE + "/orders/update/" + editingOrderId, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ items: items })
        });
        const result = await response.json();
        if (result.error) { showError(result.error); return; }
        alert("Order #" + editingOrderId + " updated!");
    } else {
        response = await fetch(API_BASE + "/orders/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ items: items })
        });
        const result = await response.json();
        if (result.error) { showError(result.error); return; }
        alert("Order #" + result.order.order_id + " created!");
    }

    hideCreateForm();
    loadOrders();
}

async function cancelOrder(orderId) {
    if (!confirm("Cancel Order #" + orderId + "?")) { return; }
    const response = await fetch(API_BASE + "/orders/cancel/" + orderId, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ confirmed: true })
    });
    const result = await response.json();
    if (result.error) { showError(result.error); return; }
    alert("Order #" + orderId + " cancelled");
    loadOrders();
}
