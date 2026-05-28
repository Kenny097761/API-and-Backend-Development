function formatNameFromEmail(email) {
  const localPart = email.split("@")[0];
  return localPart
    .split(/[._-]+/)
    .filter(Boolean)
    .map(function (part) {
      return part.charAt(0).toUpperCase() + part.slice(1);
    })
    .join(" ");
}

document
  .getElementById("loginButton")
  .addEventListener("click", function (event) {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const emailError = document.getElementById("emailError");
    const passwordError = document.getElementById("passwordError");

    emailError.textContent = "";
    passwordError.textContent = "";

    let hasError = false;

    if (email.length === 0) {
      emailError.textContent = "Email is required";
      hasError = true;
    } else if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      emailError.textContent = "Please enter a valid email address.";
      hasError = true;
    }

    if (password.length === 0) {
      passwordError.textContent = "Password is required.";
      hasError = true;
    }

    if (hasError) return;

    fetch("http://127.0.0.1:8080/login", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password })
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.status === "success") {
          sessionStorage.setItem("userId", data.user.user_id);
          sessionStorage.setItem("userRole", data.user.role);
          window.location.href = "welcome.html";
        } else {
          if (passwordError) {
            passwordError.textContent = data.message;
          } else {
            alert(data.message);
          }
        }
      })
      .catch(function (err) {
        console.error("Login error:", err);
        if (passwordError) {
          passwordError.textContent = "Unable to connect to server.";
        } else {
          alert("Unable to connect to server.");
        }
      });
  });
