document.addEventListener("DOMContentLoaded", function () {

  const welcomeUser = document.getElementById("welcomeUser");

  fetch("http://127.0.0.1:8080/me", {
    method: "GET",
    credentials: "include"
  })
    .then(res => res.json())
    .then(data => {

      if (!welcomeUser) return;

      if (data.status === "success") {
        const who = data.user.name || data.user.email;
        welcomeUser.textContent = `Signed in as ${who}`;
      } else {
        welcomeUser.textContent = "Signed in as guest";
      }

    })
    .catch(err => {
      console.error(err);

      if (welcomeUser) {
        welcomeUser.textContent = "Signed in as guest";
      }
    });

});