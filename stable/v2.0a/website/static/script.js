// const modeSwitch = document.getElementById('modeSwitch');
//         modeSwitch.addEventListener('click', () => {
//         document.body.classList.toggle('dark-mode');
// });

document.addEventListener('DOMContentLoaded', () => {
    const toggleSidebar = document.getElementById('toggleSidebar');
    const home = document.getElementById("home");
    const aec = document.getElementById("AEC");
    const pref = document.getElementById("pref");

    toggleSidebar.addEventListener('click', () => {
        document.body.classList.toggle('sidebar-collapsed');
        if (toggleSidebar.textContent == "☰ Nugget Tech") {
            toggleSidebar.textContent = "☰";
            home.textContent = "";
            aec.textContent = "";
            pref.textContent = "";
        }
        else {
            toggleSidebar.textContent = "☰ Nugget Tech";
            home.textContent = "Home";
            aec.textContent = "AI Engine Configuration";
            pref.textContent = "Prefrences";
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
