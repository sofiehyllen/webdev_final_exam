const fileInput = document.getElementById('item_image_name');
const fileList = document.getElementById('fileList');
let files = []; // Array to store selected files

fileInput.addEventListener('change', (event) => {
    for (const file of event.target.files) {
        files.push(file);
    }

    //fileInput.value = '';

    renderFileList();
});

function renderFileList() {
    fileList.innerHTML = ''; // Clear the existing list
    files.forEach((file, index) => {
        const li = document.createElement('li');
        li.textContent = `${file.name}`;

        // Add a remove button for each file
        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Remove';
        removeBtn.addEventListener('click', () => {
            files.splice(index, 1); // Remove the file from the array
            renderFileList(); // Re-render the list
        });

        li.appendChild(removeBtn);
        fileList.appendChild(li);
    });
}
