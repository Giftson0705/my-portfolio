// Mobile hamburger menu functionality
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

// Toggle mobile menu
hamburger.addEventListener('click', function() {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close mobile menu when clicking on a nav link
document.querySelectorAll('.nav-link').forEach(function(link) {
    link.addEventListener('click', function() {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    });
});

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    const isClickInsideNav = navMenu.contains(event.target);
    const isClickOnHamburger = hamburger.contains(event.target);
    
    if (!isClickInsideNav && !isClickOnHamburger && navMenu.classList.contains('active')) {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }
});

// Contact form validation and submission
document.querySelector(".contact-form").addEventListener("submit", function(e) {
    e.preventDefault();

    // Clear old errors
    document.querySelectorAll(".error").forEach(function(el) {
        el.innerText = "";
    });

    let name = document.getElementById("name").value.trim();
    let email = document.getElementById("email").value.trim();
    let subject = document.getElementById("subject").value.trim();
    let message = document.getElementById("message").value.trim();

    let valid = true;

    // Name validation
    if (name.length < 6) {
        document.getElementById("nameError").innerText = "Name must be at least 6 characters long.";
        valid = false;
    } else if (/\d/.test(name)) {
        document.getElementById("nameError").innerText = "Name should not contain numbers.";
        valid = false;
    }

    // Email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        document.getElementById("emailError").innerText = "Please enter a valid email address.";
        valid = false;
    }

    // Subject validation
    if (subject === "") {
        document.getElementById("subjectError").innerText = "Subject cannot be empty.";
        valid = false;
    }

    // Message validation
    if (message === "") {
        document.getElementById("messageError").innerText = "Message cannot be empty.";
        valid = false;
    }

    // Make errors disappear after 3 seconds
    if (!valid) {
        setTimeout(function() {
            document.querySelectorAll(".error").forEach(function(el) {
                el.innerText = "";
            });
        }, 3000);
    }

    // If valid, submit and clear fields
    if (valid) {
        // Create or select success message element
        let successMsg = document.getElementById("successMsg");
        if (!successMsg) {
            successMsg = document.createElement("p");
            successMsg.id = "successMsg";
            successMsg.style.color = "green";
            successMsg.style.marginTop = "10px";
            document.querySelector(".contact-form").appendChild(successMsg);
        }

        successMsg.innerText = "Form submitted successfully!";
        successMsg.style.display = "block";

        // Hide after 3 seconds
        setTimeout(function() {
            successMsg.style.display = "none";
        }, 3000);

        console.log({ name, email, subject, message });

        // Clear fields after submission
        document.getElementById("name").value = "";
        document.getElementById("email").value = "";
        document.getElementById("subject").value = "";
        document.getElementById("message").value = "";
    }
});