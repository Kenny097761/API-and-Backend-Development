const API_BASE = "http://127.0.0.1:8080";
const orderSelect = document.getElementById("orderSelect");
const paymentMethodSelect = document.getElementById("paymentMethodSelect");
const orderAmount = document.getElementById("orderAmount");
const orderStatus = document.getElementById("orderStatus");
const paymentForm = document.getElementById("paymentForm");
const messageBox = document.getElementById("message");

let payableOrders = [];

function showMessage(text, type) {
  messageBox.textContent = text;
  messageBox.className = `message ${type}`;
}

function clearMessage() {
  messageBox.textContent = "";
  messageBox.className = "message";
}

function formatMoney(value) {
  return `$${Number(value).toFixed(2)}`;
}

async function loadOrders() {
  const response = await fetch(`${API_BASE}/api/orders/payable`, {
    credentials: "include",
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to load payable orders");
  }

  payableOrders = data;
  orderSelect.innerHTML = `<option value="">Select an order</option>`;

  if (!data.length) {
    orderSelect.innerHTML = `<option value="">No eligible orders available</option>`;
    orderAmount.textContent = "-";
    orderStatus.textContent = "-";
    return;
  }

  data.forEach((order) => {
    const option = document.createElement("option");
    option.value = order.order_id;
    option.textContent = `Order #${order.order_id} — ${formatMoney(order.total_price)}`;
    option.dataset.amount = order.total_price;
    option.dataset.status = order.status;
    orderSelect.appendChild(option);
  });
}

async function loadPaymentMethods() {
  const response = await fetch(`${API_BASE}/api/payment-methods/me`, {
    credentials: "include",
  });
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Failed to load payment methods");
  }

  paymentMethodSelect.innerHTML = `<option value="">Select a payment method</option>`;

  if (!data.length) {
    paymentMethodSelect.innerHTML = `<option value="">No payment methods found</option>`;
    return;
  }

  data.forEach((method) => {
    const option = document.createElement("option");
    option.value = method.payment_method_id;
    const details = method.method_type === "paypal"
      ? `${method.provider} — ${method.account_name}`
      : `${method.provider} ending in ${method.card_last4}`;
    option.textContent = `${method.method_type} — ${details}`;
    paymentMethodSelect.appendChild(option);
  });
}

orderSelect.addEventListener("change", () => {
  const selected = payableOrders.find(
    (order) => String(order.order_id) === orderSelect.value
  );

  if (!selected) {
    orderAmount.textContent = "-";
    orderStatus.textContent = "-";
    return;
  }

  orderAmount.textContent = formatMoney(selected.total_price);
  orderStatus.textContent = selected.status;
});

paymentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();

  const order_id = Number(orderSelect.value);
  const payment_method_id = Number(paymentMethodSelect.value);

  if (!order_id || !payment_method_id) {
    showMessage("Please select both an order and a payment method.", "error");
    return;
  }

  const response = await fetch(`${API_BASE}/api/payments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ order_id, payment_method_id }),
  });

  const data = await response.json();

  if (!response.ok) {
    showMessage(data.error || "Payment failed.", "error");
    return;
  }

  showMessage(`Payment successful for Order #${data.order_id}.`, "success");
  await loadOrders();
});

async function initPage() {
  try {
    await loadOrders();
    await loadPaymentMethods();
  } catch (error) {
    showMessage(error.message, "error");
  }
}

initPage();