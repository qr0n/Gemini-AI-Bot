const modeSwitch = document.getElementById('modeSwitch');
        modeSwitch.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
});

document.addEventListener('DOMContentLoaded', () => {
    const toggleSidebar = document.getElementById('toggleSidebar');
    button_text = "☰ Nugget Tech";
    after_press = "☰";
    toggleSidebar.addEventListener('click', () => {
        document.body.classList.toggle('sidebar-collapsed');
        if (toggleSidebar.textContent == "☰ Nugget Tech") {
            toggleSidebar.textContent = "☰";
        }
        else {
            toggleSidebar.textContent = "☰ Nugget Tech";
        }
    });
});