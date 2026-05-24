const toggle = document.getElementById("menu-toggle");
const menu = document.getElementById("dropdown-menu");

toggle.addEventListener("click", () => {
    menu.classList.toggle("active");
});

// Fermer le menu si on clique ailleurs
document.addEventListener("click", (e) => {
    if (!toggle.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove("active");
    }
});