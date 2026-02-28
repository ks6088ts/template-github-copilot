/**
 * core.js – Application shell: theme, auth, tab registry, and shared helpers.
 *
 * Tabs register themselves via `App.registerTab(id, label, { init, show, hide })`.
 * The shell renders tab buttons and delegates lifecycle calls.
 */
const App = (() => {
  // ── SVG icons (shared) ──────────────────────────────────────
  const COPY_ICON = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z"/><path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"/></svg>';
  const CHECK_ICON = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"/></svg>';

  // ── DOM refs ────────────────────────────────────────────────
  const loginScreen = document.getElementById("login-screen");
  const headerRight = document.getElementById("header-right");
  const tabBar = document.getElementById("tab-bar");

  // ── Tab registry ────────────────────────────────────────────
  const _tabs = [];     // { id, label, init, show, hide }
  let _activeTab = null;
  let _initialized = new Set();

  /**
   * Register a tab module.
   * @param {string} id      Unique tab identifier (e.g. "chat", "report")
   * @param {string} label   Display label for the tab button
   * @param {object} hooks   { init(), show(), hide() }
   */
  function registerTab(id, label, hooks) {
    _tabs.push({ id, label, ...hooks });
  }

  // ── Theme ───────────────────────────────────────────────────
  function initTheme() {
    const saved = localStorage.getItem("theme");
    if (saved) {
      document.documentElement.setAttribute("data-theme", saved);
    } else {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      document.documentElement.setAttribute("data-theme", prefersDark ? "dark" : "light");
    }
  }

  function bindThemeToggle() {
    document.getElementById("theme-toggle").addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
    });

    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("theme")) {
        document.documentElement.setAttribute("data-theme", e.matches ? "dark" : "light");
      }
    });
  }

  // ── Tab switching ───────────────────────────────────────────
  function switchTab(id) {
    _tabs.forEach((tab) => {
      const btn = tabBar.querySelector(`[data-tab="${tab.id}"]`);
      if (btn) btn.classList.toggle("active", tab.id === id);

      if (tab.id === id) {
        // Lazy-init on first activation
        if (!_initialized.has(tab.id) && typeof tab.init === "function") {
          tab.init();
          _initialized.add(tab.id);
        }
        if (typeof tab.show === "function") tab.show();
      } else {
        if (typeof tab.hide === "function") tab.hide();
      }
    });
    _activeTab = id;
  }

  function renderTabBar() {
    tabBar.innerHTML = "";
    _tabs.forEach((tab, i) => {
      const btn = document.createElement("button");
      btn.className = "tab-btn" + (i === 0 ? " active" : "");
      btn.dataset.tab = tab.id;
      btn.textContent = tab.label;
      tabBar.appendChild(btn);
    });
    tabBar.addEventListener("click", (e) => {
      const btn = e.target.closest(".tab-btn");
      if (btn) switchTab(btn.dataset.tab);
    });
  }

  // ── Auth / Bootstrap ────────────────────────────────────────
  function showLogin() {
    loginScreen.style.display = "flex";
    tabBar.style.display = "none";
    _tabs.forEach((tab) => {
      if (typeof tab.hide === "function") tab.hide();
    });
    headerRight.innerHTML = "";
  }

  function showApp(user) {
    loginScreen.style.display = "none";
    renderTabBar();
    tabBar.style.display = "flex";

    // Show first tab
    if (_tabs.length > 0) {
      switchTab(_tabs[0].id);
    }

    let avatar = "";
    if (user.avatar_url) {
      avatar = `<img src="${user.avatar_url}" alt="avatar" />`;
    }
    headerRight.innerHTML = `
      <div class="user-info">
        ${avatar}
        <span>${user.login}</span>
        <a href="/auth/logout" class="btn">Logout</a>
      </div>
    `;
  }

  async function init() {
    initTheme();
    bindThemeToggle();

    try {
      const resp = await fetch("/api/me");
      if (!resp.ok) throw new Error("not authed");
      const user = await resp.json();
      showApp(user);
    } catch {
      showLogin();
    }
  }

  // ── Copy helper (shared utility) ───────────────────────────
  function createCopyBtn(getText) {
    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.innerHTML = `${COPY_ICON} Copy`;
    btn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(getText());
        btn.innerHTML = `${CHECK_ICON} Copied`;
        btn.classList.add("copied");
        setTimeout(() => {
          btn.innerHTML = `${COPY_ICON} Copy`;
          btn.classList.remove("copied");
        }, 2000);
      } catch { /* clipboard not available */ }
    });
    return btn;
  }

  // ── Public API ──────────────────────────────────────────────
  return {
    registerTab,
    createCopyBtn,
    init,
  };
})();

// Boot after all tab scripts have been loaded
document.addEventListener("DOMContentLoaded", () => App.init());
