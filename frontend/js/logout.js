document.addEventListener("DOMContentLoaded", function () {

  const logoutButton = document.getElementById("logoutButton");

  if (!logoutButton) return;

  logoutButton.addEventListener("click", function () {

    fetch("http://127.0.0.1:8080/logout", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      }
    })
      .then(res => res.json())
      .then(data => {

        console.log(data.message);

        sessionStorage.removeItem('userId');
        sessionStorage.removeItem('userRole');

        window.location.href = "./index.html";
      })
      .catch(err => console.error("Logout error:", err));

  });

});