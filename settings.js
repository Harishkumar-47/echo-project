document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ Settings page loaded");

    // 🌗 DARK MODE
    const darkModeToggle = document.getElementById("darkModeToggle");
    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
        darkModeToggle.checked = true;
    }
    darkModeToggle?.addEventListener("change", () => {
        if (darkModeToggle.checked) {
            document.body.classList.add("dark-mode");
            localStorage.setItem("darkMode", "enabled");
        } else {
            document.body.classList.remove("dark-mode");
            localStorage.setItem("darkMode", "disabled");
        }
    });

    // 🔐 SET PIN
    const setPinBtn = document.getElementById("setPinBtn");
    setPinBtn?.addEventListener("click", () => {
        const pin = prompt("Enter a 4-digit PIN:");
        if (pin && /^\d{4}$/.test(pin)) {
            localStorage.setItem("appPIN", pin);
            alert("✅ PIN set successfully!");
        } else {
            alert("❌ Invalid PIN. Please enter 4 digits.");
        }
    });

    // 🧹 CLEAR HISTORY
    const clearHistoryBtn = document.getElementById("clearHistoryBtn");
    clearHistoryBtn?.addEventListener("click", () => {
        localStorage.removeItem("recoveryHistory");
        alert("🧹 History cleared!");
    });

    // 🗑️ CLEAR CACHE
    const clearCacheBtn = document.getElementById("clearCacheBtn");
    clearCacheBtn?.addEventListener("click", () => {
        caches.keys().then(names => {
            for (let name of names) caches.delete(name);
        });
        alert("🗑️ Cache cleared!");
    });

    // 📞 CONTACT SUPPORT
    const contactSupportBtn = document.getElementById("contactSupportBtn");
    contactSupportBtn?.addEventListener("click", () => {
        alert("📞 Contact form coming soon!");
    });

    // 🐛 REPORT BUG
    const reportBugBtn = document.getElementById("reportBugBtn");
    reportBugBtn?.addEventListener("click", () => {
        alert("🐛 Bug report feature coming soon!");
    });

    // 📘 USER GUIDE
    const userGuideBtn = document.getElementById("userGuideBtn");
    userGuideBtn?.addEventListener("click", () => {
        alert("📘 Help section coming soon!");
    });
});
