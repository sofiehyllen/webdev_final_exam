const dropdowns = Array.from(document.getElementsByClassName('dropdown-container'));

dropdowns.forEach(dropdown => {
    const button = dropdown.querySelector('button');
    const menu = dropdown.querySelector('div');
    
    // Show the dropdown menu when the button is clicked
    button.addEventListener('click', () => {
        menu.classList.toggle('hidden');
    });
});