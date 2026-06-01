document.addEventListener("DOMContentLoaded", () => {
  const $ = (id) => document.getElementById(id);
  const tabs = document.querySelectorAll("[data-reco-tab]");
  const refresh = $("recoRefresh");
  const loading = $("recoLoading");
  const panes = {
    learning: $("recoPaneLearning"),
    roadmap: $("recoPaneRoadmap"),
    internships: $("recoPaneInternships"),
  };

  let errorEl = $("recoError");
  if (!errorEl) {
    errorEl = document.createElement("div");
    errorEl.id = "recoError";
    errorEl.className = "alert alert-danger border-0 d-none mb-3";
    document.querySelector(".card.p-3")?.prepend(errorEl);
  }

  const setVisible = (el, visible) => el && el.classList.toggle("d-none", !visible);
  const setError = (msg) => {
    if (!errorEl) return;
    errorEl.textContent = msg || "";
    setVisible(errorEl, !!msg);
  };

  const esc = (s) =>
    String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  const insightCard = (title, items, type = "text") => {
    if (!items?.length) return "";
    const body =
      type === "list"
        ? `<ul class="text-muted mb-0 ps-3">${items.map((x) => `<li class="mb-2">${esc(typeof x === "string" ? x : x.body || x.title)}</li>`).join("")}</ul>`
        : type === "cards"
          ? `<div class="vstack gap-3">${items
              .map(
                (c) => `
            <div class="vid-insight-card p-3">
              <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
                <h6 class="text-white mb-0">${esc(c.title || c.role)}</h6>
                ${c.badge ? `<span class="badge bg-primary-subtle text-primary">${esc(c.badge)}</span>` : ""}
              </div>
              <p class="text-muted small mb-2">${esc(c.body)}</p>
              ${c.cta && c.href ? `<a href="${c.href}" class="btn btn-sm btn-outline-primary">${esc(c.cta)}</a>` : ""}
            </div>`
              )
              .join("")}</div>`
          : `<p class="text-muted mb-0">${esc(items[0])}</p>`;
    return `
      <div class="col-12">
        <div class="card p-3 bg-secondary-subtle border-0 h-100">
          <h6 class="text-white mb-3">${esc(title)}</h6>
          ${body}
        </div>
      </div>`;
  };

  const renderLearning = (data) => {
    panes.learning.innerHTML = `
      <div class="row g-3">
        ${insightCard("Profile Highlights", data.profile_highlights, "list")}
        ${insightCard("Suggested Improvements", data.suggested_improvements, "cards")}
        ${insightCard("Skill Growth Opportunities", data.skill_growth, "cards")}
        ${insightCard("Recommended Next Projects", data.recommended_projects, "cards")}
        ${insightCard("Career Alignment", data.career_alignment, "cards")}
      </div>
      <div class="row g-3 mt-1">
        <div class="col-lg-8">
          <div class="card p-3 bg-secondary-subtle border-0">
            <h6 class="text-white mb-2">This week's focus</h6>
            <ul class="text-muted mb-0">${(data.daily_goals || []).map((x) => `<li class="mb-2">${esc(x)}</li>`).join("") || "<li>—</li>"}</ul>
            <p class="text-muted small mt-3 mb-0">${esc(data.study_plan || "")}</p>
          </div>
        </div>
        <div class="col-lg-4">
          <div class="card p-3 bg-secondary-subtle border-0">
            <div class="d-flex justify-content-between"><h6 class="text-white mb-0">Streak</h6><span class="badge bg-success">${data.learning_streak_days || 0} days</span></div>
            <hr class="border-secondary-subtle my-3">
            <h6 class="text-white mb-2">Practice focus</h6>
            <div class="d-flex flex-wrap gap-2">
              ${(data.weak_subjects || []).map((t) => `<span class="badge bg-danger">${esc(t)}</span>`).join("") || '<span class="badge bg-success">Balanced</span>'}
            </div>
          </div>
        </div>
      </div>
    `;
  };

  const renderRoadmap = (data) => {
    const steps = Array.isArray(data.steps) ? data.steps : [];
    panes.roadmap.innerHTML = `
      <div class="card p-3 bg-secondary-subtle border-0 mb-3">
        <p class="text-muted mb-2">${esc(data.intro || "")}</p>
        <div class="d-flex flex-wrap gap-2">
          <span class="badge bg-secondary">${esc(data.target_role)}</span>
          <span class="badge bg-outline-light text-muted">${esc(data.timeline)}</span>
        </div>
      </div>
      <div class="roadmap-steps">
        ${steps
          .map(
            (s, idx) => `
          <div class="vid-insight-card p-3 mb-3">
            <div class="d-flex gap-3">
              <div class="roadmap-dot">${idx + 1}</div>
              <div>
                <div class="text-white fw-semibold">${esc(s.title || s)}</div>
                <div class="text-muted small mt-1">${esc(s.description || "")}</div>
              </div>
            </div>
          </div>`
          )
          .join("") || '<p class="text-muted">Complete your profile to generate a roadmap.</p>'}
      </div>
    `;
  };

  const renderInternships = (data) => {
    panes.internships.innerHTML = `
      <div class="row g-3">
        <div class="col-lg-7">
          <div class="card p-3 bg-secondary-subtle border-0">
            <h6 class="text-white mb-2">Internships</h6>
            <div class="vstack gap-2">
              ${(data.internships || [])
                .map(
                  (i) => `
                <div class="vid-insight-card p-3">
                  <div class="text-white fw-semibold">${esc(i.title)}</div>
                  <div class="text-muted small">${esc(i.company || "")}</div>
                  <p class="text-muted small mt-2 mb-0">${esc(i.match_reason)}</p>
                </div>`
                )
                .join("")}
            </div>
          </div>
        </div>
        <div class="col-lg-5">
          <div class="card p-3 bg-secondary-subtle border-0 mb-3">
            <h6 class="text-white mb-2">Hackathons</h6>
            <ul class="text-muted mb-0">${(data.hackathons || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
          </div>
          <div class="card p-3 bg-secondary-subtle border-0">
            <h6 class="text-white mb-2">Coding contests</h6>
            <ul class="text-muted mb-0">${(data.coding_contests || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
          </div>
        </div>
      </div>
    `;
  };

  let activeTab = (window.recoInitialTab || "learning").toLowerCase();

  const switchTab = (tab) => {
    activeTab = tab;
    tabs.forEach((t) => t.classList.toggle("active", t.dataset.recoTab === tab));
    Object.entries(panes).forEach(([k, el]) => setVisible(el, k === tab));
  };

  async function load(tab) {
    setError("");
    setVisible(loading, true);
    try {
      let data;
      if (tab === "learning") {
        const res = await fetch("/api/recommendation/learning");
        data = await res.json();
        if (!res.ok) throw new Error(data.error || "Could not load insights.");
        renderLearning(data);
      } else if (tab === "roadmap") {
        const res = await fetch("/api/recommendation/roadmap");
        data = await res.json();
        if (!res.ok) throw new Error(data.error || "Could not load roadmap.");
        renderRoadmap(data);
      } else {
        const res = await fetch("/api/recommendation/internships");
        data = await res.json();
        if (!res.ok) throw new Error(data.error || "Could not load opportunities.");
        renderInternships(data);
      }
      setVisible(loading, false);
    } catch (e) {
      setVisible(loading, false);
      setError(e?.message || "Failed to load recommendations.");
    }
  }

  tabs.forEach((t) => {
    t.addEventListener("click", () => {
      switchTab(t.dataset.recoTab);
      load(t.dataset.recoTab);
    });
  });

  refresh?.addEventListener("click", () => load(activeTab));

  switchTab(activeTab);
  load(activeTab);
});
