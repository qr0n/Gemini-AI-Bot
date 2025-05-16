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

    loadPersonalityData();
    setupFormAutoSave();
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

// Load personality data when page loads
async function loadPersonalityData() {
    const nuggetAlias = document.querySelector('[data-nugget-alias]')?.dataset.nuggetAlias;
    if (!nuggetAlias) return;

    try {
        const response = await fetch(`/api/${nuggetAlias}/personality`);
        const data = await response.json();
        if (data && !data.error) {
            document.getElementById('name').value = data.name || '';
            document.getElementById('age').value = data.age || '';
            document.getElementById('role').value = data.role || '';
            document.getElementById('description').value = data.description || '';
            document.getElementById('likes').value = data.likes || '';
            document.getElementById('dislikes').value = data.dislikes || '';
        }
    } catch (error) {
        console.error('Error loading personality data:', error);
    }
}

// Save personality data
async function savePersonalityData() {
    const nuggetAlias = document.querySelector('[data-nugget-alias]')?.dataset.nuggetAlias;
    if (!nuggetAlias) return;

    const data = {
        name: document.getElementById('name').value,
        age: document.getElementById('age').value,
        role: document.getElementById('role').value,
        description: document.getElementById('description').value,
        likes: document.getElementById('likes').value,
        dislikes: document.getElementById('dislikes').value
    };

    try {
        const response = await fetch(`/api/${nuggetAlias}/personality`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        if (result.success) {
            alert('Personality traits saved successfully!');
        } else {
            alert('Error saving personality traits: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error saving personality data:', error);
        alert('Error saving personality traits. Please try again.');
    }
}

// Add form auto-save functionality
function setupFormAutoSave() {
    const formElements = document.querySelectorAll('.personality-container input, .personality-container textarea');
    formElements.forEach(element => {
        element.addEventListener('change', () => {
            savePersonalityData();
        });
    });
}

function showAddBotModal() {
    document.getElementById('addBotModal').style.display = 'block';
}

function closeAddBotModal() {
    document.getElementById('addBotModal').style.display = 'none';
}

async function addNewBot() {
    const data = {
        bot_name: document.getElementById('botName').value,
        discord_id: document.getElementById('discordId').value,
        avatar_url: document.getElementById('avatarUrl').value
    };

    try {
        const response = await fetch('/api/bots', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        if (result.success) {
            alert('Bot added successfully!');
            window.location.reload();
        } else {
            alert('Error adding bot: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error adding bot:', error);
        alert('Error adding bot. Please try again.');
    }

    closeAddBotModal();
}

async function deleteBot(botName) {
    if (!confirm(`Are you sure you want to delete ${botName}?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/bots/${botName}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (result.success) {
            alert('Bot deleted successfully!');
            window.location.reload();
        } else {
            alert('Error deleting bot: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting bot:', error);
        alert('Error deleting bot. Please try again.');
    }
}