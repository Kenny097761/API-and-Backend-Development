function loadLogs() {

    fetch("http://127.0.0.1:8080/me", {
        credentials: "include"
    })
        .then(res => {
            if (!res.ok) {
                alert("Please log in first.");
                window.location.href = "./index.html";
                return null;
            }
            return res.json();
        })
        .then(userData => {

            if (!userData || userData.status !== "success") {
                alert("Not logged in");
                window.location.href = "./index.html";
                return null;
            }

            const date = document.getElementById("dateFilter")?.value;
            let url = `http://127.0.0.1:8080/access-logs`;

            if (date) {
                url += `?date=${date}`;
            }

            return fetch(url, {
                credentials: "include"
            });
        })
        .then(res => {
            if (!res) return null;
            return res.json();
        })
        .then(data => {

            if (!data) return;

            const table = document.getElementById("logTable");
            table.innerHTML = "";

            if (!data.logs || data.logs.length === 0) {
                table.innerHTML = `
                    <tr>
                        <td colspan="4">No records found.</td>
                    </tr>
                `;
                return;
            }

            data.logs.forEach(log => {
                table.innerHTML += `
                    <tr>
                        <td>${log.log_id}</td>
                        <td>${log.login_time}</td>
                        <td>${log.logout_time ?? "-"}</td>
                        <td>${log.log_date}</td>
                    </tr>
                `;
            });
        })
        .catch(err => console.error(err));
}

document.addEventListener("DOMContentLoaded", loadLogs);