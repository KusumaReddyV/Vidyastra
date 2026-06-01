(() => {
  const STORAGE_KEY = "theme";
  const LEGACY_KEY = "vid_theme";

  const migrateLegacyTheme = () => {
    try {
      const current = localStorage.getItem(STORAGE_KEY);
      if (current === "light" || current === "dark") return;
      const legacy = localStorage.getItem(LEGACY_KEY);
      if (legacy === "light" || legacy === "dark") {
        localStorage.setItem(STORAGE_KEY, legacy);
      }
    } catch (e) {}
  };

  const getSystemTheme = () => {
    try {
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches
        ? "light"
        : "dark";
    } catch (e) {
      return "dark";
    }
  };

  const getSavedTheme = () => {
    try {
      const t = localStorage.getItem(STORAGE_KEY);
      return t === "light" || t === "dark" ? t : null;
    } catch (e) {
      return null;
    }
  };

  const applyTheme = (theme) => {
    const t = theme === "light" || theme === "dark" ? theme : getSystemTheme();
    document.documentElement.setAttribute("data-bs-theme", t);
    document.documentElement.dataset.vidTheme = t;
    document.body.classList.toggle("vid-light-mode", t === "light");
    document.body.classList.toggle("vid-dark-mode", t === "dark");
    const icon = document.querySelector("[data-theme-icon]");
    if (icon) icon.className = t === "dark" ? "fas fa-moon" : "fas fa-sun";
  };

  const persistTheme = (theme) => {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
      localStorage.removeItem(LEGACY_KEY);
    } catch (e) {}
  };

  const toggleTheme = () => {
    const current = document.documentElement.getAttribute("data-bs-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    persistTheme(next);
  };

  migrateLegacyTheme();
  applyTheme(
    getSavedTheme() ||
      document.documentElement.getAttribute("data-bs-theme") ||
      getSystemTheme()
  );

  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    e.preventDefault();
    toggleTheme();
  });

  try {
    const mq = window.matchMedia("(prefers-color-scheme: light)");
    mq.addEventListener("change", () => {
      if (!getSavedTheme()) applyTheme(getSystemTheme());
    });
  } catch (e) {}
})();
