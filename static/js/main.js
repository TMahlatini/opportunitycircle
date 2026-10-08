(() => {
  const SECOND = 1000;
  const MINUTE = 60 * SECOND;
  const HOUR = 60 * MINUTE;
  const DAY = 24 * HOUR;

  function initCountdown(root) {
    const end = Date.parse(root.dataset.end);
    if (Number.isNaN(end)) return;

    const values = {};
    root.querySelectorAll("[data-unit]").forEach((el) => {
      values[el.dataset.unit] = el;
    });
    const label = root.querySelector("[data-countdown-label]");
    const announce = root.querySelector("[data-countdown-announce]");
    const launch = root.dataset.launch || "11 Dec 2026";
    let lastAnnouncedDays = null;
    let timer = null;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const rollSeconds = (el, text) => {
      const shown = el.querySelector(".roll-in")?.textContent || el.textContent;
      if (shown === text) return;
      if (reduceMotion) {
        el.textContent = text;
        return;
      }
      const pair = document.createElement("span");
      pair.className = "roll-pair";
      const outgoing = document.createElement("span");
      outgoing.className = "roll-out";
      outgoing.textContent = shown;
      const incoming = document.createElement("span");
      incoming.className = "roll-in";
      incoming.textContent = text;
      pair.append(outgoing, incoming);
      el.replaceChildren(pair);
    };

    const setValue = (unit, number) => {
      const el = values[unit];
      const text = String(number).padStart(2, "0");
      if (!el) return;
      if (unit === "seconds") {
        rollSeconds(el, text);
        return;
      }
      if (el.textContent === text) return;
      el.textContent = text;
      el.classList.remove("is-ticking");
      void el.offsetWidth;
      el.classList.add("is-ticking");
    };

    const render = () => {
      const remaining = Math.max(end - Date.now(), 0);
      const days = Math.floor(remaining / DAY);

      setValue("days", days);
      setValue("hours", Math.floor((remaining % DAY) / HOUR));
      setValue("minutes", Math.floor((remaining % HOUR) / MINUTE));
      setValue("seconds", Math.floor((remaining % MINUTE) / SECOND));

      if (days !== lastAnnouncedDays && announce) {
        announce.textContent = `${days} days remaining until ${launch}.`;
        lastAnnouncedDays = days;
      }

      if (remaining === 0) {
        root.setAttribute("data-complete", "");
        if (label) label.textContent = "Solution launched";
        if (announce) announce.textContent = "The solution has launched.";
        clearInterval(timer);
      }
    };

    render();
    timer = setInterval(render, SECOND);
  }

  function initReveal() {
    const items = document.querySelectorAll("[data-fade]");
    if (!items.length || !("IntersectionObserver" in window)) {
      items.forEach((el) => el.classList.add("is-in"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.15 }
    );
    items.forEach((el) => observer.observe(el));
  }

  function initBios() {
    const bios = document.querySelectorAll(".bio");
    if (!bios.length) return;

    const fits = (bio) => {
      bio.classList.add("is-clamped");
      const overflows = bio.scrollHeight > bio.clientHeight + 1;
      if (!overflows) bio.classList.remove("is-clamped");
      return overflows;
    };

    bios.forEach((bio) => {
      const button = bio.parentElement.querySelector(".read-more");
      if (!button) return;

      const sync = () => {
        if (bio.classList.contains("is-open")) return;
        button.hidden = !fits(bio);
      };

      sync();
      button.addEventListener("click", () => {
        const open = bio.classList.toggle("is-open");
        bio.classList.toggle("is-clamped", !open);
        button.setAttribute("aria-expanded", open ? "true" : "false");
        button.textContent = open ? "Read less" : "Read more";
      });

      window.addEventListener("resize", sync);
    });

    if (document.fonts) document.fonts.ready.then(() => {
      bios.forEach((bio) => {
        if (bio.classList.contains("is-open")) return;
        const button = bio.parentElement.querySelector(".read-more");
        if (button) button.hidden = !fits(bio);
      });
    });
  }

  document.querySelectorAll("[data-countdown]").forEach(initCountdown);
  initReveal();
  initBios();
})();
