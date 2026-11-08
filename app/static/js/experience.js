(() => {
  const root = document.documentElement;
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  let changing = false;
  const mode = () => (root.dataset.mode === "night" ? "night" : "day");
  function syncMode() {
    const night = mode() === "night";
    document
      .querySelectorAll("[data-mood-switch]")
      .forEach((b) => b.setAttribute("aria-checked", String(night)));
    document
      .querySelector("#theme-color")
      ?.setAttribute("content", night ? "#10131b" : "#f4f0e7");
    document.dispatchEvent(
      new CustomEvent("mine:mode", { detail: { mode: mode() } }),
    );
  }
  async function changeMode(button, next) {
    if (changing || next === mode()) return;
    changing = true;
    const rect = button?.getBoundingClientRect();
    const x = rect ? rect.left + rect.width / 2 : innerWidth / 2;
    const y = rect ? rect.top + rect.height / 2 : innerHeight / 2;
    root.style.setProperty("--switch-x", `${x}px`);
    root.style.setProperty("--switch-y", `${y}px`);
    root.style.setProperty(
      "--switch-radius",
      `${Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y)) + 20}px`,
    );
    const update = () => {
      root.dataset.mode = next;
      try {
        localStorage.setItem("mine606-mode", next);
      } catch (_) {}
      syncMode();
      const status = document.querySelector(".theme-announcement");
      if (status)
        status.textContent = `${next === "night" ? "Night" : "Day"} mode is on across the site.`;
    };
    try {
      if (document.startViewTransition && !reduced.matches) {
        const transition = document.startViewTransition(update);
        await transition.finished;
      } else {
        update();
        if (!reduced.matches) {
          root.classList.add("theme-fading");
          await new Promise((resolve) => setTimeout(resolve, 520));
          root.classList.remove("theme-fading");
        }
      }
    } catch (_) {
      update();
    } finally {
      changing = false;
    }
  }
  document
    .querySelectorAll("[data-mood-switch]")
    .forEach((b) =>
      b.addEventListener("click", () =>
        changeMode(b, mode() === "night" ? "day" : "night"),
      ),
    );
  window.addEventListener("storage", (event) => {
    if (
      event.key === "mine606-mode" &&
      ["day", "night"].includes(event.newValue)
    ) {
      root.dataset.mode = event.newValue;
      syncMode();
    }
  });
  syncMode();

  const navButton = document.querySelector(".site-header .nav-toggle");
  const nav = document.querySelector("#mobile-nav");
  function closeNav() {
    if (nav) {
      nav.hidden = true;
      navButton?.setAttribute("aria-expanded", "false");
      navButton?.setAttribute("aria-label", "Open navigation");
    }
  }
  navButton?.addEventListener("click", () => {
    const open = nav.hidden;
    nav.hidden = !open;
    navButton.setAttribute("aria-expanded", String(open));
    navButton.setAttribute(
      "aria-label",
      open ? "Close navigation" : "Open navigation",
    );
  });
  nav?.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeNav();
  });
  matchMedia("(min-width: 851px)").addEventListener("change", (event) => {
    if (event.matches) closeNav();
  });

  const sidebar = document.querySelector(".admin-sidebar");
  const backdrop = document.querySelector(".admin-backdrop");
  const sidebarToggle = document.querySelector("[data-admin-nav]");
  function closeSidebar() {
    sidebar?.classList.remove("is-open");
    if (backdrop) backdrop.hidden = true;
    sidebarToggle?.setAttribute("aria-expanded", "false");
    if (sidebar && innerWidth <= 600) sidebar.inert = true;
  }
  function openSidebar() {
    if (!sidebar) return;
    sidebar.inert = false;
    sidebar.classList.add("is-open");
    backdrop.hidden = false;
    sidebarToggle?.setAttribute("aria-expanded", "true");
    sidebar.querySelector(".sidebar-close")?.focus();
  }
  if (sidebar) {
    sidebar.inert = innerWidth <= 600;
    matchMedia("(max-width:600px)").addEventListener("change", (e) => {
      closeSidebar();
      sidebar.inert = e.matches;
    });
  }
  sidebarToggle?.addEventListener("click", () =>
    sidebar.classList.contains("is-open") ? closeSidebar() : openSidebar(),
  );
  document.querySelector(".sidebar-close")?.addEventListener("click", () => {
    closeSidebar();
    sidebarToggle?.focus();
  });
  backdrop?.addEventListener("click", closeSidebar);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeNav();
      if (sidebar?.classList.contains("is-open")) {
        closeSidebar();
        sidebarToggle?.focus();
      }
    }
  });

  const dialog = document.querySelector("#photo-dialog");
  document.querySelectorAll("[data-photo]").forEach((b) =>
    b.addEventListener("click", () => {
      if (!dialog) return;
      dialog.querySelector("img").src = b.dataset.photo;
      dialog.querySelector("img").alt = b.dataset.caption || "";
      dialog.querySelector("p").textContent = b.dataset.caption || "";
      dialog.showModal();
    }),
  );
  dialog
    ?.querySelector("[data-close-dialog]")
    ?.addEventListener("click", () => dialog.close());
  dialog?.addEventListener("click", (e) => {
    if (e.target === dialog) dialog.close();
  });

  const menu = document.querySelector("[data-menu]");
  if (menu) {
    const tabs = [...menu.querySelectorAll("button[data-category]")];
    const cards = [...menu.querySelectorAll("[data-menu-item]")];
    const search = menu.querySelector("#menu-search");
    const tag = menu.querySelector("#menu-tag");
    let category = "all";
    function filter() {
      let count = 0;
      const q = search.value.trim().toLowerCase();
      cards.forEach((c) => {
        c.hidden = !(
          (category === "all" || c.dataset.category === category) &&
          (!tag.value || c.dataset.tags.split(",").includes(tag.value)) &&
          (!q || c.dataset.search.includes(q))
        );
        if (!c.hidden) count++;
      });
      menu.querySelector("#menu-count").textContent =
        `${count} ${count === 1 ? "item" : "items"}`;
      menu.querySelector("#menu-empty").hidden =
        count > 0 || cards.length === 0;
    }
    tabs.forEach((t) =>
      t.addEventListener("click", () => {
        category = t.dataset.category;
        tabs.forEach((b) => b.setAttribute("aria-pressed", String(t === b)));
        filter();
      }),
    );
    search.addEventListener("input", filter);
    tag.addEventListener("change", filter);
    menu.querySelector("[data-reset-menu]")?.addEventListener("click", () => {
      search.value = "";
      tag.value = "";
      category = "all";
      tabs.forEach((t) =>
        t.setAttribute("aria-pressed", String(t.dataset.category === "all")),
      );
      filter();
    });
  }
  document.querySelectorAll("[data-async-form]").forEach((form) =>
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const button = form.querySelector("[type=submit]");
      if (button.disabled) return;
      const status = form.querySelector(".form-status");
      const label = button.textContent;
      button.disabled = true;
      button.textContent = "SENDING…";
      status.classList.remove("is-error");
      status.textContent = "";
      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: { Accept: "application/json" },
        });
        const data = await response.json();
        if (!response.ok || !data.success)
          throw Error(
            typeof data.detail === "string"
              ? data.detail
              : "Please check your details and try again.",
          );
        status.textContent = form.dataset.success;
        form.reset();
      } catch (error) {
        status.classList.add("is-error");
        status.textContent =
          error.message === "Failed to fetch"
            ? "Couldn’t connect. Your details are still here; please try again."
            : error.message;
      } finally {
        button.disabled = false;
        button.textContent = label;
      }
    }),
  );
  document
    .querySelectorAll("input[type=file][data-image-preview]")
    .forEach((input) =>
      input.addEventListener("change", () => {
        const target = document.querySelector(input.dataset.imagePreview);
        const file = input.files[0];
        if (!target || !file) return;
        if (target.dataset.objectUrl)
          URL.revokeObjectURL(target.dataset.objectUrl);
        const url = URL.createObjectURL(file);
        target.src = url;
        target.hidden = false;
        target.dataset.objectUrl = url;
      }),
    );
  document.querySelectorAll("form[data-confirm]").forEach((form) =>
    form.addEventListener("submit", (e) => {
      if (!confirm(form.dataset.confirm)) e.preventDefault();
    }),
  );
})();
// Native validity keeps an accidental end-before-start edit in the form.
document.querySelectorAll("form").forEach((form) => {
  const start = form.querySelector('input[name="start"]');
  const end = form.querySelector('input[name="end"]');
  if (start && end) {
    const validate = () =>
      end.setCustomValidity(
        end.value && start.value && end.value < start.value
          ? "End time must be after the start time."
          : "",
      );
    start.addEventListener("input", validate);
    end.addEventListener("input", validate);
  }
});
