const API_BASE = "http://127.0.0.1:8080";
const list = document.getElementById("paymentsList");
const messageBox = document.getElementById("message");

function showMessage(text, type) {
  messageBox.textContent = text;
  messageBox.className = `message ${type}`;
}

function formatMoney(value) {
  return `$${Number(value).toFixed(2)}`;
}

async function loadAllPayments() {
  const response = await fetch(`${API_BASE}/api/payments`, {
    credentials: "include",
  });
  const data = await response.json();

  if (!response.ok) {
    showMessage(data.error || "Failed to load payments.", "error");
    return;
  }

  if (!data.length) {
    list.innerHTML = `<div class="payment-item"><h3>No payments found</h3></div>`;
    return;
  }

  list.innerHTML = data.map((payment) => `
    <article class="payment-item">
      <h3>${payment.first_name || ""} ${payment.last_name || ""} — Order #${payment.order_id}</h3>
      <p class="payment-meta">Customer email: ${payment.email}</p>
      <p class="payment-meta">Amount: ${formatMoney(payment.amount)}</p>
      <p class="payment-meta">Method: ${payment.method_type} (${payment.provider}${payment.card_last4 ? ` ending in ${payment.card_last4}` : ""})</p>
      <p class="payment-meta">Paid at: ${payment.paid_at}</p>
    </article>
  `).join("");
}

loadAllPayments();