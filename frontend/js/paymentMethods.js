const form = document.getElementById('paymentMethodForm');
const paymentType = document.getElementById('paymentType');
const paymentMethodId = document.getElementById('paymentMethodId');
const submitPaymentButton = document.getElementById('submitPaymentButton');
const cancelEditButton = document.getElementById('cancelEditButton');
const searchPaymentType = document.getElementById('searchPaymentType');
const paymentMethodList = document.getElementById('paymentMethodList');
const emptyPaymentMessage = document.getElementById('emptyPaymentMessage');
const addPaymentButton = document.getElementById('addPaymentButton');
const paymentModal = document.getElementById('paymentModal');
const closePaymentModal = document.getElementById('closePaymentModal');
const deleteConfirmModal = document.getElementById('deleteConfirmModal');
const confirmDeleteButton = document.getElementById('confirmDeleteButton');
const cancelDeleteButton = document.getElementById('cancelDeleteButton');

const API_BASE_URL = 'http://127.0.0.1:8080';

let paymentMethods = [];
let paymentMethodIdToDelete = '';
let canManagePaymentMethods = true;

function getPaymentHeaders() {
    return {
        'Content-Type': 'application/json'
    };
}

function getStoredUserId() {
    return sessionStorage.getItem('userId');
}

function withStoredUserId(path) {
    const userId = getStoredUserId();

    if (!userId) {
        return path;
    }

    const separator = path.includes('?') ? '&' : '?';
    return `${path}${separator}user_id=${encodeURIComponent(userId)}`;
}

function checkCustomerControls() {
    const role = sessionStorage.getItem('userRole');
    if (role !== 'customer') {
        addPaymentButton.style.display = 'none';
    } else {
        addPaymentButton.style.display = 'block';
    }
}

function showApiError(message) {
    alert(message || 'Something went wrong. Please try again.');
}

async function requestPaymentMethods(path, options) {
    const response = await fetch(`${API_BASE_URL}${withStoredUserId(path)}`, {
        credentials: 'include',
        ...options,
        headers: {
            ...getPaymentHeaders(),
            ...(options && options.headers ? options.headers : {})
        }
    });

    if (response.status === 204) {
        return null;
    }

    const data = await response.json();

    if (!response.ok) {
        const error = new Error(data.error || 'Payment method request failed');
        error.errors = data.errors;
        throw error;
    }

    return data;
}

async function loadPaymentMethods() {
    if (!getStoredUserId()) {
        window.location.href = 'login.html';
        return;
    }

    try {
        paymentMethods = await requestPaymentMethods('/payment-methods/');
        canManagePaymentMethods = true;
        searchPaymentType.disabled = false;
        addPaymentButton.disabled = false;
        renderPaymentMethods();
    } catch (error) {
        canManagePaymentMethods = false;
        paymentMethods = [];
        paymentMethodList.innerHTML = '';
        searchPaymentType.disabled = true;
        addPaymentButton.disabled = true;
        emptyPaymentMessage.textContent = error.message;
        emptyPaymentMessage.classList.add('is-error');
        emptyPaymentMessage.style.display = 'block';
    }
}

function showPaymentForm() {
    if (!canManagePaymentMethods) {
        return;
    }

    paymentModal.classList.remove('hidden');
    document.body.classList.add('modal-open');
    paymentType.focus();
}

function hidePaymentForm() {
    paymentModal.classList.add('hidden');
    document.body.classList.remove('modal-open');
}

function showDeleteConfirm(methodId) {
    if (!canManagePaymentMethods) {
        return;
    }

    paymentMethodIdToDelete = methodId;
    deleteConfirmModal.classList.remove('hidden');
    document.body.classList.add('modal-open');
    confirmDeleteButton.focus();
}

function hideDeleteConfirm() {
    paymentMethodIdToDelete = '';
    deleteConfirmModal.classList.add('hidden');
    document.body.classList.remove('modal-open');
}

// delete the selected payment method after the confirmation popup is confirmed
async function deleteSelectedPaymentMethod() {
    if (paymentMethodIdToDelete === '') {
        return;
    }

    try {
        await requestPaymentMethods(getPaymentMethodEndpoint(paymentMethodIdToDelete), {
            method: 'DELETE'
        });
        hideDeleteConfirm();
        await loadPaymentMethods();
    } catch (error) {
        showApiError(error.message);
    }
}

// shows only the form fields that match the selected payment method type
function showFieldsForSelectedType() {
    document.querySelectorAll('[data-payment-fields]').forEach(function (fieldGroup) {
        fieldGroup.classList.toggle('hidden', fieldGroup.dataset.paymentFields !== paymentType.value);
    });
    clearErrors();
}

function clearErrors() {
    document.querySelectorAll('.error').forEach(function (error) {
        error.textContent = '';
        error.style.display = 'none';
    });

    document.querySelectorAll('input, select').forEach(function (field) {
        field.classList.remove('invalid');
    });
}

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const error = document.getElementById(`${fieldId}Error`);

    if (field) {
        field.classList.add('invalid');
    }

    if (error) {
        error.textContent = message;
        error.style.display = 'block';
    }
}

function showBackendErrors(errors) {
    Object.keys(errors || {}).forEach(function (fieldId) {
        showError(fieldId, errors[fieldId]);
    });
}

function getNumbersOnly(value) {
    return value.replace(/\D/g, ''); // \D not a digit, g globally
}

function isNumbersOnly(value) {
    return /^\d+$/.test(value); // \d+ means one or more digits
}

function isLettersOnly(value) {
    return /^[A-Za-z ]+$/.test(value); 
}

function isValidExpiry(expiryDate) {
    const match = expiryDate.match(/^(0[1-9]|1[0-2])\/(\d{2})$/); // MM/YY

    if (!match) {
        return false;
    }

    const month = Number(match[1]);
    const year = Number(`20${match[2]}`);
    const lastDayOfExpiryMonth = new Date(year, month, 0);
    const today = new Date();

    today.setHours(0, 0, 0, 0);
    return lastDayOfExpiryMonth >= today;
}

function getNextPaymentMethodId() {
    const highestId = paymentMethods.reduce(function (highest, method) {
        const numericId = Number(method.id);
        return Number.isNaN(numericId) ? highest : Math.max(highest, numericId);
    }, 0);

    return String(highestId + 1).padStart(3, '0');
}

// checks all visible payment method fields before allowing the method is added
function validatePaymentMethod() {
    clearErrors();

    const type = paymentType.value;
    const existingMethod = paymentMethods.find(function (method) {
        return method.id === paymentMethodId.value;
    });
    let isValid = true;

    if (type === 'card') {
        const cardholderName = document.getElementById('cardholderName').value.trim();
        const cardNumber = document.getElementById('cardNumber').value.trim();
        const expiryDate = document.getElementById('expiryDate').value.trim();
        const cvv = document.getElementById('cvv').value.trim();
        const isUsingSavedCardNumber = existingMethod && cardNumber.includes('*');

        if (cardholderName === '') {
            showError('cardholderName', 'Cardholder name is required');
            isValid = false;
        } else if (!isLettersOnly(cardholderName)) {
            showError('cardholderName', 'Cardholder name can only contain letters');
            isValid = false;
        }

        if (!isUsingSavedCardNumber && !isNumbersOnly(cardNumber)) {
            showError('cardNumber', 'Card number can only contain numbers');
            isValid = false;
        }

        if (!isValidExpiry(expiryDate)) {
            showError('expiryDate', 'Use a valid future expiry date');
            isValid = false;
        }

        if (!existingMethod && !isNumbersOnly(cvv)) {
            showError('cvv', 'CVV can only contain numbers');
            isValid = false;
        }
    }

    if (type === 'bank') {
        const accountName = document.getElementById('accountName').value.trim();
        const bsbValue = document.getElementById('bsb').value;
        const accountNumberValue = document.getElementById('accountNumber').value;
        const isUsingSavedBsb = existingMethod && bsbValue.includes('*');
        const isUsingSavedAccountNumber = existingMethod && accountNumberValue.includes('*');

        if (accountName === '') {
            showError('accountName', 'Account name is required');
            isValid = false;
        } else if (!isLettersOnly(accountName)) {
            showError('accountName', 'Account name can only contain letters');
            isValid = false;
        }

        if (!isUsingSavedBsb && !isNumbersOnly(bsbValue)) {
            showError('bsb', 'BSB can only contain numbers');
            isValid = false;
        }

        if (!isUsingSavedAccountNumber && !isNumbersOnly(accountNumberValue)) {
            showError('accountNumber', 'Account number can only contain numbers');
            isValid = false;
        }
    }

    if (type === 'paypal') {
        const paypalEmail = document.getElementById('paypalEmail').value.trim();
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!existingMethod && !emailPattern.test(paypalEmail)) {
            showError('paypalEmail', 'Enter a valid PayPal email');
            isValid = false;
        }

        if (existingMethod && paypalEmail !== '' && !emailPattern.test(paypalEmail)) {
            showError('paypalEmail', 'Enter a valid PayPal email');
            isValid = false;
        }
    }

    return isValid;
}

// builds a payment method object from the form values, keeping sensitive details masked
function getPaymentMethodFromForm() {
    const type = paymentType.value;
    const existingMethod = paymentMethods.find(function (method) {
        return method.id === paymentMethodId.value;
    });
    const method = {
        id: paymentMethodId.value || getNextPaymentMethodId(),
        type,
        nickname: document.getElementById('nickname').value,
        createdAt: new Date().toISOString()
    };

    if (type === 'card') {
        const cardNumberValue = document.getElementById('cardNumber').value;
        method.cardholderName = document.getElementById('cardholderName').value.trim();
        method.cardNumber = cardNumberValue.includes('*') && existingMethod ? '' : cardNumberValue;
        method.expiryDate = document.getElementById('expiryDate').value.trim();
    }

    if (type === 'bank') {
        const bsbValue = document.getElementById('bsb').value;
        const accountNumberValue = document.getElementById('accountNumber').value;
        method.accountName = document.getElementById('accountName').value.trim();
        method.bsb = bsbValue.includes('*') && existingMethod ? '' : bsbValue;
        method.accountNumber = accountNumberValue.includes('*') && existingMethod ? '' : accountNumberValue;
    }

    if (type === 'paypal') {
        const paypalEmail = document.getElementById('paypalEmail').value.trim();
        method.paypalEmail = paypalEmail;
    }

    return method;
}

function getCardBrand(cardNumber) {
    if (/^4/.test(cardNumber)) {
        return 'Visa';
    }

    if (/^5[1-5]/.test(cardNumber)) {
        return 'Mastercard';
    }

    if (/^3[47]/.test(cardNumber)) {
        return 'American Express';
    }

    return 'Card';
}

function maskEmail(email) {
    const parts = email.split('@');
    const name = parts[0];
    const domain = parts[1];
    const visibleName = name.length <= 2 ? name.charAt(0) : name.slice(0, 2);

    return `${visibleName}***@${domain}`;
}

// clears the form and returns it to the default add payment state
function resetForm() {
    form.reset();
    paymentMethodId.value = '';
    paymentType.value = 'card';
    submitPaymentButton.textContent = 'Add Payment Method';
    cancelEditButton.textContent = 'Cancel';
    cancelEditButton.hidden = false;
    showFieldsForSelectedType();
}

function getTypeLabel(type) {
    const labels = {
        card: 'Credit or Debit Card',
        bank: 'Bank Account Transfer',
        paypal: 'PayPal'
    };

    return labels[type] || type;
}

function getMethodDetail(method) {
    if (method.type === 'card') {
        return `${method.cardBrand || 'Card'} ending in ${method.cardLastFour} - expires ${method.expiryDate}`;
    }

    if (method.type === 'bank') {
        return `BSB ending in ${method.bsbLastThree} - account ending in ${method.accountLastFour}`;
    }

    return method.paypalEmail;
}

// rebuilds the payment method list based on the selected search type
function renderPaymentMethods() {
    const selectedType = searchPaymentType.value;
    const filteredMethods = selectedType === 'all'
        ? paymentMethods
        : paymentMethods.filter(function (method) {
        return method.type === selectedType;
        });

    paymentMethodList.innerHTML = '';
    emptyPaymentMessage.textContent = 'No payment methods saved yet.';
    emptyPaymentMessage.classList.remove('is-error');
    emptyPaymentMessage.style.display = filteredMethods.length === 0 ? 'block' : 'none';

    filteredMethods.forEach(function (method) {
        const methodCard = document.createElement('article');
        const methodDetails = document.createElement('div');
        const typeLabel = document.createElement('span');
        const nickname = document.createElement('h3');
        const detail = document.createElement('p');
        const actions = document.createElement('div');
        const editButton = document.createElement('button');
        const deleteButton = document.createElement('button');

        methodCard.className = 'payment-method-card';
        typeLabel.className = 'payment-method-type';
        actions.className = 'payment-card-actions';
        editButton.className = 'secondary-payment-button';
        deleteButton.className = 'danger-payment-button';

        typeLabel.textContent = getTypeLabel(method.type);
        nickname.textContent = method.nickname;
        detail.textContent = getMethodDetail(method);

        editButton.type = 'button';
        editButton.dataset.action = 'edit';
        editButton.dataset.id = method.id;
        editButton.textContent = 'Edit';

        deleteButton.type = 'button';
        deleteButton.dataset.action = 'delete';
        deleteButton.dataset.id = method.id;
        deleteButton.textContent = 'Delete';

        methodDetails.append(typeLabel, nickname, detail);
        actions.append(editButton, deleteButton);
        methodCard.append(methodDetails, actions);

        paymentMethodList.appendChild(methodCard);
    });
}

// opens the popup and fill the form with the existing payment method for editing
function fillFormForEdit(method) {
    resetForm();
    showPaymentForm();

    paymentMethodId.value = method.id;
    paymentType.value = method.type;
    document.getElementById('nickname').value = method.nickname;
    showFieldsForSelectedType();

    if (method.type === 'card') {
        document.getElementById('cardholderName').value = method.cardholderName || '';
        document.getElementById('cardNumber').value = method.cardLastFour ? `************${method.cardLastFour}` : '';
        document.getElementById('expiryDate').value = method.expiryDate || '';
        document.getElementById('cvv').value = '';
    }

    if (method.type === 'bank') {
        document.getElementById('accountName').value = method.accountName || '';
        document.getElementById('bsb').value = method.bsbLastThree ? `***${method.bsbLastThree}` : '';
        document.getElementById('accountNumber').value = method.accountLastFour ? `******${method.accountLastFour}` : '';
    }

    if (method.type === 'paypal') {
        document.getElementById('paypalEmail').value = '';
    }

    submitPaymentButton.textContent = 'Update Payment Method';
    cancelEditButton.textContent = 'Cancel Edit';
    cancelEditButton.hidden = false;
}

// replaces the saved payment method with the updated form values
function getPaymentMethodEndpoint(methodId) {
    return `/payment-methods/${Number(methodId)}`;
}

form.addEventListener('submit', async function (event) {
    event.preventDefault();

    if (!validatePaymentMethod()) {
        return;
    }

    const method = getPaymentMethodFromForm();

    try {
        if (paymentMethodId.value) {
            await requestPaymentMethods(getPaymentMethodEndpoint(paymentMethodId.value), {
                method: 'PUT',
                body: JSON.stringify(method)
            });
        } else {
            await requestPaymentMethods('/payment-methods/', {
                method: 'POST',
                body: JSON.stringify(method)
            });
        }

        await loadPaymentMethods();
        resetForm();
        hidePaymentForm();
    } catch (error) {
        if (error.errors) {
            showBackendErrors(error.errors);
            return;
        }

        showApiError(error.message);
    }
});

paymentType.addEventListener('change', showFieldsForSelectedType);

paymentMethodList.addEventListener('click', function (event) {
    const button = event.target.closest('button[data-action]');

    if (!button) {
        return;
    }

    const methodId = button.dataset.id;
    const method = paymentMethods.find(function (paymentMethod) {
        return paymentMethod.id === methodId;
    });

    if (!method) {
        return;
    }

    if (button.dataset.action === 'edit') {
        fillFormForEdit(method);
        return;
    }

    showDeleteConfirm(methodId);
});

searchPaymentType.addEventListener('change', renderPaymentMethods);

cancelEditButton.addEventListener('click', function () {
    resetForm();
    hidePaymentForm();
});

closePaymentModal.addEventListener('click', function () {
    resetForm();
    hidePaymentForm();
});

paymentModal.addEventListener('click', function (event) {
    if (event.target === paymentModal) {
        resetForm();
        hidePaymentForm();
    }
});

confirmDeleteButton.addEventListener('click', deleteSelectedPaymentMethod);

cancelDeleteButton.addEventListener('click', hideDeleteConfirm);

deleteConfirmModal.addEventListener('click', function (event) {
    if (event.target === deleteConfirmModal) {
        hideDeleteConfirm();
    }
});

addPaymentButton.addEventListener('click', function () {
    resetForm();
    showPaymentForm();
});

checkCustomerControls();
showFieldsForSelectedType();
loadPaymentMethods();
