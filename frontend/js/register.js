document.getElementById('registerForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    const firstNameError = document.getElementById('firstNameError');
    const lastNameError = document.getElementById('lastNameError');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');

    firstNameError.style.display = 'none';
    lastNameError.style.display = 'none';
    emailError.style.display = 'none';
    passwordError.style.display = 'none';

    let isValid = true;

    if (firstName === '') {
        firstNameError.textContent = 'First name is required';
        firstNameError.style.display = 'block';
        isValid = false;
    }

    if (lastName === '') {
        lastNameError.textContent = 'Last name is required';
        lastNameError.style.display = 'block';
        isValid = false;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
        emailError.textContent = 'Please enter a valid email address';
        emailError.style.display = 'block';
        isValid = false;
    }

    if (password.length < 6) {
        passwordError.textContent = 'Password must be at least 6 characters';
        passwordError.style.display = 'block';
        isValid = false;
    }

    if (!isValid) {
        return;
    }

    const fullName = `${firstName} ${lastName}`;

    const user = {
        name: fullName,
        email: email
    };

    sessionStorage.setItem('registeredUser', JSON.stringify(user));
    sessionStorage.setItem('user', JSON.stringify(user));
    sessionStorage.setItem('userName', fullName);
    sessionStorage.setItem('userEmail', email);
    sessionStorage.setItem('isLoggedIn', 'true');

    window.location.href = 'welcome.html';
});