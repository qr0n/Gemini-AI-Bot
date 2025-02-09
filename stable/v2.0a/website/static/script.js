// const modeSwitch = document.getElementById('modeSwitch');
//         modeSwitch.addEventListener('click', () => {
//         document.body.classList.toggle('dark-mode');
// });

document.addEventListener('DOMContentLoaded', () => {
    const toggleSidebar = document.getElementById('toggleSidebar');
    const pref = document.getElementById("pref");
    const home = document.getElementById("home");
    const aec = document.getElementById("AEC");
    
    toggleSidebar.addEventListener('click', () => {
        document.body.classList.toggle('sidebar-collapsed');
        if (toggleSidebar.textContent == "☰ Nugget Tech") {
            
            toggleSidebar.textContent = "☰";
            pref.textContent = "";
            home.textContent = "";
            aec.textContent = "";
        }
        else {
            toggleSidebar.textContent = "☰ Nugget Tech";
            pref.textContent = "Preferences";
            home.textContent = "Home";
            aec.textContent = "AI Engine Configuration";
        }
    });
});

function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
    const button_text = document.getElementById("modeSwitch");

    // Store user preference in localStorage
    if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("darkMode", "enabled");
        button_text.textContent = "Dark Mode";
        
    } else {
        localStorage.setItem("darkMode", "disabled");
        button_text.textContent = "Light Mode";
    }
}

// Apply dark mode on page load if it was enabled before
document.addEventListener("DOMContentLoaded", () => {
    const button_text = document.getElementById("modeSwitch");
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
        button_text.textContent = "Dark Mode";
    }
    else {
        button_text.textContent = "Light Mode";
    }
});

window.addEventListener("unload", () => {
    console.log("Page is being closed or navigated away.");
});

function editMemory(button) {
    var memorySpecialText = button.parentElement.querySelector('.memory-special-text').innerText;
    var memoryText = button.parentElement.querySelector('.memory-text').innerText;
    document.getElementById('topContentInput').value = memorySpecialText;
    document.getElementById('bottomContentInput').value = memoryText;
    document.getElementById('editModal').style.display = 'block';
}

function saveMemory() {
    var memorySpecialText = document.getElementById('topContentInput').value;
    var memoryText = document.getElementById('bottomContentInput').value;
    // Save the memory text (implement the save logic here)
    closeModal();
}

function confirmDelete(button) {
    document.getElementById('editModal').style.display = 'none';
    document.getElementById('confirmDeleteModal').style.display = 'block';
    // Store the memory to be deleted (implement the logic here)
}

function deleteMemory() {
    // Delete the memory (implement the delete logic here)
    closeModal();
}

function closeModal() {
    document.getElementById('editModal').style.display = 'none';
    document.getElementById('confirmDeleteModal').style.display = 'none';
}