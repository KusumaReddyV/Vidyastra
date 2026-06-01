document.addEventListener("DOMContentLoaded", () => {
  // Animated counters
  const counters = document.querySelectorAll(".counter");
  const runCounter = (counter) => {
    const target = Number(counter.dataset.target || "0");
    if (!target) return;
    const duration = 1200;
    const start = performance.now();
    const tick = (now) => {
      const progress = Math.min(1, (now - start) / duration);
      const value = Math.floor(target * progress);
      counter.textContent = value >= 1000 ? `${(value / 1000).toFixed(0)}k+` : String(value);
      if (progress < 1) requestAnimationFrame(tick);
      else counter.textContent = target >= 1000 ? `${Math.round(target / 1000)}k+` : String(target);
    };
    requestAnimationFrame(tick);
  };

  const counterObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        runCounter(entry.target);
        counterObserver.unobserve(entry.target);
      });
    },
    { threshold: 0.3 }
  );
  counters.forEach((c) => counterObserver.observe(c));

  // Smooth scroll for in-page links
  document.querySelectorAll('a[href^="#"], .vid-scroll-link').forEach((link) => {
    link.addEventListener("click", (e) => {
      const href = link.getAttribute("href");
      if (!href || !href.startsWith("#")) return;
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // Fade-in on scroll
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("vid-reveal-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );
  document.querySelectorAll(".vid-reveal").forEach((el) => revealObserver.observe(el));
});
