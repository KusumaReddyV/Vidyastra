document.addEventListener("DOMContentLoaded", () => {
  const themeSelect = document.getElementById("themeSelect");
  if (!themeSelect) return;

  const applyTheme = (value) => {
    const root = document.documentElement;
    const v = (value || "system").toLowerCase();
    if (v === "light" || v === "dark") {
      root.setAttribute("data-bs-theme", v);
      localStorage.setItem("vid_theme", v);
      return;
    }
    // system: clear override, fallback handled by theme.js
    localStorage.removeItem("vid_theme");
  };

  themeSelect.addEventListener("change", () => applyTheme(themeSelect.value));
  applyTheme(window.currentTheme || themeSelect.value);
});

