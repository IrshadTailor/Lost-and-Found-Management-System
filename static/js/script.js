// =============================
// Confirm before delete (optional)
// =============================
function confirmDelete() {
    return confirm("Are you sure you want to delete this item?");
}

// =============================
// Flash message fade-out
// =============================
document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelector(".flashes");

    if (flashes) {
        setTimeout(() => {
            flashes.style.transition = "0.7s ease";
            flashes.style.opacity = "0";
        }, 2500);
    }
});

// =============================
// Search input auto-focus
// =============================
document.addEventListener("DOMContentLoaded", () => {
    const searchField = document.getElementById("searchInput");
    if (searchField) {
        searchField.focus();
    }
});

// =============================
// Mobile Menu Toggle
// (if you add a hamburger for mobile UI)
// =============================
const menuBtn = document.getElementById("menuBtn");
const nav = document.querySelector("header nav");

if (menuBtn && nav) {
    menuBtn.addEventListener("click", () => {
        nav.classList.toggle("show");
    });
}

// =============================
// Preview Image Before Upload
// (For lost & found report forms)
// =============================
function previewImage(event) {
    const preview = document.getElementById("previewImg");
    if (preview) {
        preview.src = URL.createObjectURL(event.target.files[0]);
        preview.style.display = "block";
    }
}

// =============================
// Clear form after submission (optional)
// =============================
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) form.reset();
}
