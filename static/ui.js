// dropdoen
const dropdowns = Array.from(document.getElementsByClassName('dropdown-container'));

dropdowns.forEach(dropdown => {
    const button = dropdown.querySelector('button');
    const menu = dropdown.querySelector('div');
    
    // Show the dropdown menu when the button is clicked
    button.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevent click event from propagating to the window
        menu.classList.toggle('hidden');
    });

    // Close the dropdown when clicking outside
    window.addEventListener('click', (event) => {
        if (!menu.classList.contains('hidden')) {
            menu.classList.add('hidden');
        }
    });
});



// show search results
function showResults() {
    document.getElementById('search-results').classList.remove('hidden');
}






document.addEventListener("DOMContentLoaded", function () {
    const openDeleteModalBtns = document.querySelectorAll(".open-delete-modal-btn");
    const deleteModals = document.querySelectorAll(".delete-modal");
    const cancelDeleteBtns = document.querySelectorAll(".cancel-delete-btn");
    
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
    

    const confirmDeleteBtns = document.querySelectorAll(".confirm-delete-btn");
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











document.addEventListener('DOMContentLoaded', function () {
    function showSlide(itemPk, index) {
        const slider = document.getElementById(`slider-${itemPk}`);  // Use the full item_pk as the ID
    
        const images = slider.querySelectorAll(".slider-image");
        if (index >= images.length) index = 0;
        if (index < 0) index = images.length - 1;
    
        images.forEach(slide => slide.classList.add('hidden'));  // Hide all images
        images[index]?.classList.remove('hidden');  // Show the current image
    }
    
    function moveSlide(itemPk, direction) {
        const slider = document.getElementById(`slider-${itemPk}`);
        const images = slider.querySelectorAll(".slider-image");

        let currentIndex = Array.from(images).findIndex(slide => !slide.classList.contains('hidden'));
        currentIndex += direction;
        showSlide(itemPk, currentIndex);
    }

    // Add event listeners for the buttons for each item
    document.querySelectorAll('.prev-arrow').forEach(prevButton => {
        const itemPk = prevButton.closest('.group').id.replace('slider-', '');  // Extract item_pk from parent ID
        prevButton.addEventListener('click', function() {
            moveSlide(itemPk, -1);  // Move to the previous slide
        });
    });

    document.querySelectorAll('.next-arrow').forEach(nextButton => {
        const itemPk = nextButton.closest('.group').id.replace('slider-', '');  // Extract item_pk from parent ID
        nextButton.addEventListener('click', function() {
            moveSlide(itemPk, 1);   // Move to the next slide
        });
    });

    // Initialize each slider to show the first image
    document.querySelectorAll('.image-slider').forEach(slider => {
        const itemPk = slider.id.replace('slider-', '');  // Extract item_pk from slider ID
        showSlide(itemPk, 0);  // Show the first image on initialization
    });
});
