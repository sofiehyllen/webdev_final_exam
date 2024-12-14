let allFiles = []; // Array to store all selected files
let selDiv = "";

document.addEventListener("DOMContentLoaded", init, false);

function init() {
    document.querySelector('#item_image_name').addEventListener('change', handleFileSelect, false);
    selDiv = document.querySelector("#selectedFiles");
}

function handleFileSelect(e) {
    if (!e.target.files || !window.FileReader) return;

    let files = e.target.files;
    let filesArr = Array.prototype.slice.call(files);

    filesArr.forEach(function(f) {
        if (!f.type.match("image.*")) {
            return;
        }

        // Add the file to the array
        allFiles.push(f);

        let reader = new FileReader();
        reader.onload = function (e) {
            // Append the image to the preview div with a unique ID
            const fileIndex = allFiles.length - 1; // Unique index based on array length
            const html = `
            <div id="file-${fileIndex}" class="flex items-center gap-4 mt-4">
                <div class="w-36 h-16 overflow-hidden flex justify-center items-center rounded-md relative">
                    <img src="${e.target.result}" alt="${f.name}" class="h-full w-full object-cover">
                </div>
                <span class="text-sm text-zinc-500">${f.name}</span>
                <button type="button" class="remove-btn text-red-500" data-index="${fileIndex}">Remove</button>
            </div>`;
            selDiv.innerHTML += html;
        };
        reader.readAsDataURL(f);
    });

    // Clear the input so it can accept new files
    e.target.value = "";

    // Update the hidden input to hold all files
    updateFileInput();
}

function updateFileInput() {
    // Create a new DataTransfer object to hold the files
    let dataTransfer = new DataTransfer();

    allFiles.forEach(file => {
        dataTransfer.items.add(file);
    });

    // Update the file input with the new list of files
    document.querySelector('#item_image_name').files = dataTransfer.files;
}

document.addEventListener('click', function (e) {
    if (e.target && e.target.classList.contains('remove-btn')) {
        const fileIndex = e.target.getAttribute('data-index');
        removeFile(fileIndex);
    }
});

function removeFile(index) {
    // Remove the file from the allFiles array
    allFiles.splice(index, 1);

    // Remove the preview
    const fileDiv = document.querySelector(`#file-${index}`);
    if (fileDiv) fileDiv.remove();

    // Update the file input
    updateFileInput();

    // Reassign data-index for remaining files
    const remainingFiles = document.querySelectorAll('.remove-btn');
    remainingFiles.forEach((btn, newIndex) => {
        btn.setAttribute('data-index', newIndex);
        btn.parentElement.id = `file-${newIndex}`;
    });
}
