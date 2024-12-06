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
// Handle delete modal visibility
document.addEventListener("DOMContentLoaded", function () {
    // Select buttons and modals using classes
    const openDeleteModalBtns = document.querySelectorAll(".open-delete-modal-btn");
    const deleteModals = document.querySelectorAll(".delete-modal");
    const cancelDeleteBtns = document.querySelectorAll(".cancel-delete-btn");
    const confirmDeleteBtns = document.querySelectorAll(".confirm-delete-btn");

    // Open the delete modal
    openDeleteModalBtns.forEach((btn, index) => {
        btn.addEventListener("click", function () {
            deleteModals[index]?.classList.remove("hidden");
            deleteModals[index]?.classList.add("flex");
        });
    });

    // Close the delete modal
    cancelDeleteBtns.forEach((btn, index) => {
        btn.addEventListener("click", function () {
            deleteModals[index]?.classList.remove("flex");
            deleteModals[index]?.classList.add("hidden");
        });
    });

    // Handle the delete action
    confirmDeleteBtns.forEach((btn, index) => {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

            const passwordInput = deleteModals[index]?.querySelector(".delete-password-input");
            const password = passwordInput?.value.trim();

            if (!password) {
                passwordInput?.classList.add("bg-red-200");
                return;
            }

            const accountPk = btn.getAttribute("mix-delete");

            fetch(accountPk, {
                method: "DELETE",
                headers: {
                    "X-User-Confirmation": password
                }
            })
                .then(response => response.text())
                .then(html => {
                    console.log(html);
                    if (html.includes('<template mix-redirect="/login"></template>')) {
                        console.log("Your account has been deleted.");
                        window.location.reload();
                    } else {
                        console.log("An error occurred during account deletion.");
                    }
                })
                .catch(error => {
                    console.error("Error deleting account:", error);
                });
        });
    });
});
