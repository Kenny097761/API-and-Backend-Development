function checkAdminControls() {
    const role = sessionStorage.getItem("userRole");
    const adminControls = document.getElementById("adminControls");

    if (role !== "admin") {
        adminControls.style.display = "none";
    } else {
        adminControls.style.display = "block";
    }
}

function logout() {
    sessionStorage.clear();

    window.location.href = "login.html";
}

async function loadDevices() {
    const response = await fetch("http://127.0.0.1:8080/devices");
    const devices = await response.json();

    displayDevices(devices);
}


async function searchDevices() {
    const name = document.getElementById("searchName").value;
    const type = document.getElementById("searchType").value;
    const response = await fetch(
        `http://127.0.0.1:8080/devices/search?name=${name}&type=${type}`
    );
    const devices = await response.json();

    displayDevices(devices);
}


function displayDevices(devices) {
    const deviceList = document.getElementById("deviceList");
    deviceList.innerHTML = "";
    
    if (devices.length === 0) {
        deviceList.innerHTML = "<p>No devices found.</p>";
        return;
    }
    
    const role = sessionStorage.getItem("userRole");
    
    devices.forEach(device => {

    let adminButtons = "";

    if (role === "admin") {
        adminButtons = `
            <input type="text" id="name-${device.device_id}" value="${device.name}">
            <input type="text" id="type-${device.device_id}" value="${device.type}">
            <input type="number" id="price-${device.device_id}" value="${device.unit_price}">
            <input type="number" id="stock-${device.device_id}" value="${device.stock}">

            <button onclick="updateDevice(${device.device_id})">Update</button>
            <button onclick="deleteDevice(${device.device_id})">Delete</button>
        `;
    }
    deviceList.innerHTML += `
        <div class="device-card">
            <h3>${device.name}</h3>

            <p><strong>Type:</strong> ${device.type}</p>
            <p><strong>Price:</strong> $${device.unit_price}</p>
            <p><strong>Stock:</strong> ${device.stock}</p>

            ${adminButtons}
        </div>
    `;
});
}

checkAdminControls();
loadDevices();

// staff operations

async function addDevice() {
    const name = document.getElementById("deviceName").value;
    const type = document.getElementById("deviceType").value;
    const unit_price = document.getElementById("devicePrice").value;
    const stock = document.getElementById("deviceStock").value;
    const formData = new FormData();

    formData.append("name", name);
    formData.append("type", type);
    formData.append("unit_price", unit_price);
    formData.append("stock", stock);

    const response = await fetch(
        "http://127.0.0.1:8080/devices/add",
        {
            method: "POST",
            body: formData
        }
    );

    const message = await response.text();

    document.getElementById("message").innerText = message;

    loadDevices();
}

async function updateDevice(device_id) {

    const name = document.getElementById("name-" + device_id).value;
    const type = document.getElementById("type-" + device_id).value;
    const unit_price = document.getElementById("price-" + device_id).value;
    const stock = document.getElementById("stock-" + device_id).value;
    const formData = new FormData();

    formData.append("name", name);
    formData.append("type", type);
    formData.append("unit_price", unit_price);
    formData.append("stock", stock);

    const response = await fetch(
        "http://127.0.0.1:8080/devices/update/" + device_id,
        {
            method: "PUT",
            body: formData
        }
    );

    const message = await response.text();

    document.getElementById("message").innerText = message;

    loadDevices();
}

async function deleteDevice(device_id) {

    const response = await fetch(
        "http://127.0.0.1:8080/devices/delete/" + device_id,
        {
            method: "DELETE"
        }
    );

    const message = await response.text();

    document.getElementById("message").innerText = message;

    loadDevices();
}