// Contact form validation and submission with API integration
document.querySelector(".contact-form").addEventListener("submit", async function(e) {
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
        return;
    }

    // If validation passes, submit to API
    try {
        const response = await fetch('http://localhost:8000/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                subject: subject,
                message: message
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Success - show success message
            let successMsg = document.getElementById("successMsg");
            if (!successMsg) {
                successMsg = document.createElement("p");
                successMsg.id = "successMsg";
                successMsg.style.color = "green";
                successMsg.style.marginTop = "10px";
                document.querySelector(".contact-form").appendChild(successMsg);
            }

            successMsg.innerText = "Message sent successfully!";
            successMsg.style.display = "block";

            // Clear form fields
            document.getElementById("name").value = "";
            document.getElementById("email").value = "";
            document.getElementById("subject").value = "";
            document.getElementById("message").value = "";

            // Hide success message after 3 seconds
            setTimeout(function() {
                successMsg.style.display = "none";
            }, 3000);

        } else {
            throw new Error(data.detail || 'Failed to send message');
        }

    } catch (error) {
        console.error('Error:', error);
        
        // Show error message
        let errorMsg = document.getElementById("errorMsg");
        if (!errorMsg) {
            errorMsg = document.createElement("p");
            errorMsg.id = "errorMsg";
            errorMsg.style.color = "red";
            errorMsg.style.marginTop = "10px";
            document.querySelector(".contact-form").appendChild(errorMsg);
        }

        errorMsg.innerText = "Failed to send message. Please try again.";
        errorMsg.style.display = "block";

        // Hide error message after 3 seconds
        setTimeout(function() {
            errorMsg.style.display = "none";
        }, 3000);
    }
});