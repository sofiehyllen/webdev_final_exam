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
});

