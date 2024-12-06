const dropdowns = Array.from(document.getElementsByClassName('dropdown-container'));

dropdowns.forEach(dropdown => {
    const button = dropdown.querySelector('button');
    const menu = dropdown.querySelector('div');
    
    // Show the dropdown menu when the button is clicked
    button.addEventListener('click', () => {
        menu.classList.toggle('hidden');
    });
});

function showResults() {
    document.getElementById('search-results').classList.remove('hidden');
}

///////////////////////////////////////////////
// Open and close modal for deleting profile
document.addEventListener("DOMContentLoaded", function () {
    const openModalBtn = document.getElementById("open-delete-modal-btn");
    const deleteModal = document.getElementById("delete-modal");
    const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    const deletePasswordInput = document.getElementById("delete-password-input"); // Ensure you have an input for the password

    // Open the modal when the "Delete account" button is clicked
    openModalBtn.addEventListener("click", function (e) {
        e.preventDefault(); 
        deleteModal.classList.remove("hidden");
        deleteModal.classList.add("flex");
    });

    // Close the modal when the "Cancel" button is clicked
    cancelDeleteBtn.addEventListener("click", function (e) {
        e.preventDefault();  
        deleteModal.classList.remove("flex");
        deleteModal.classList.add("hidden");
    });



    // Handle the delete action
    confirmDeleteBtn.addEventListener("click", function (e) {
        e.preventDefault();

        const password = deletePasswordInput.value.trim();  // Get the entered password

        if (!password) {
            console.log("Please enter your password to confirm deletion.");
            return;
        }

        const accountPk = this.getAttribute("mix-delete"); // Get account_pk from the button attribute

        fetch(accountPk, {
            method: "DELETE",
            headers: {
                "X-Delete-Password": password // Send the password in the header
            }
        })
        .then(response => response.text())  // Expect HTML text
        .then(html => {
            // Check if the response contains a redirect template
            if (html.includes('<template mix-redirect="/login"></template>')) {
                console.log("Your account has been deleted.");
            } else {
                console.log("An error occurred during account deletion.");
            }
        })
        .catch(error => {
            console.error("Error deleting account:", error);
            console.log("There was an error with the request.");
        });
    });
});
