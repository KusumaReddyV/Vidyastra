document.addEventListener("DOMContentLoaded", () => {
  const $ = (id) => document.getElementById(id);
  const refreshBtn = $("plannerRefresh");
  const loading = $("plannerLoading");
  const error = $("plannerError");
  const goals = $("plannerGoals");
  const reminders = $("plannerReminders");
  const badges = $("plannerBadges");
  const weak = $("plannerWeak");
  const streak = $("plannerStreak");

  const setVisible = (el, visible) => el && el.classList.toggle("d-none", !visible);
  const setError = (msg) => {
    if (!error) return;
    error.textContent = msg || "";
    setVisible(error, !!msg);
  };

  const parseApiError = async (res) => {
    const text = await res.text();
    try {
      const data = JSON.parse(text);
      return data.error || data.details || data.message || text;
    } catch (e) {
      if (text.length > 200) return "Could not load study plan. Please try again.";
      return text;
    }
  };

  const pill = (text, kind = "secondary") =>
    `<span class="badge bg-${kind}">${String(text || "").replace(/</g, "&lt;")}</span>`;

  const renderStudyPlan = (data) => {
    if (streak) streak.textContent = `${data.learning_streak_days || data.streak_days || 0} day streak`;

    const goalItems = data.daily_goals || [];
    goalItems.forEach((g) => {
      const text = typeof g === "string" ? g : g.title || g.task || "";
      const div = document.createElement("div");
      div.className = "card p-3 vid-plan-card border-0";
      div.innerHTML = `<div class="text-white fw-semibold">${text}</div>`;
      goals.appendChild(div);
    });
    if (!goals.children.length) goals.innerHTML = `<div class="text-muted">No goals yet.</div>`;

    (data.revision_reminders || data.study_tips || []).forEach((r) => {
      const message = typeof r === "string" ? r : r.message || r.tip || "";
      const time = typeof r === "string" ? "" : r.time || "";
      const div = document.createElement("div");
      div.className = "vid-reminder-row";
      div.innerHTML = `<div class="text-white">${message}</div><div class="text-muted small">${time}</div>`;
      reminders.appendChild(div);
    });
    if (!reminders.children.length) reminders.innerHTML = `<div class="text-muted">No reminders yet.</div>`;

    (data.badges || []).forEach((b) => {
      const div = document.createElement("div");
      div.className = "card p-3 vid-plan-card border-0";
      div.innerHTML = `<div class="text-white fw-semibold">${b.name || "Badge"}</div><div class="text-muted small mt-1">${b.description || ""}</div>`;
      badges.appendChild(div);
    });
    if (!badges.children.length) badges.innerHTML = `<div class="text-muted">Complete quizzes to earn badges.</div>`;

    const weakList = data.weak_subjects || data.focus_areas || [];
    weakList.forEach((t) => {
      const label = typeof t === "string" ? t : t.topic || t.name || "";
      if (label) weak.insertAdjacentHTML("beforeend", pill(label, "danger"));
    });
    if (!weak.children.length) weak.innerHTML = pill("No weak topics yet", "success");

    setError("");
  };

  async function loadPlan() {
    setError("");
    setVisible(loading, true);
    goals.innerHTML = "";
    reminders.innerHTML = "";
    badges.innerHTML = "";
    weak.innerHTML = "";

    try {
      const res = await fetch("/api/study-plan?hours=2");
      const data = await res.json().catch(() => ({}));
      if (!res.ok && !data.daily_goals) {
        throw new Error(await parseApiError(res));
      }
      renderStudyPlan(data);
      setVisible(loading, false);
    } catch (e) {
      setVisible(loading, false);
      setError(e?.message || "Failed to load study plan.");
    }
  }

  if (refreshBtn) refreshBtn.addEventListener("click", loadPlan);
  loadPlan();
});
