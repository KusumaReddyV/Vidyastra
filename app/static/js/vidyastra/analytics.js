document.addEventListener("DOMContentLoaded", () => {
  const results = Array.isArray(window.analyticsQuizResults) ? window.analyticsQuizResults : [];
  const meta = window.analyticsData || {};
  const summary = meta.summary || {};

  if (!window.Chart) return;

  const trendEl = document.getElementById("scoreTrendChart");
  const trendEmpty = document.getElementById("scoreTrendEmpty");
  if (trendEl) {
    const ordered = [...results].reverse().filter((r) => r.score != null);
    if (!ordered.length) {
      trendEl.classList.add("d-none");
      trendEmpty?.classList.remove("d-none");
    } else {
      trendEmpty?.classList.add("d-none");
      new Chart(trendEl, {
        type: "line",
        data: {
          labels: ordered.map((_, i) => `#${i + 1}`),
          datasets: [{
            label: "Score (%)",
            data: ordered.map((r) => Number(r.score || 0)),
            borderColor: "#30a14e",
            backgroundColor: "rgba(48, 161, 78, 0.15)",
            tension: 0.35,
            fill: true,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, max: 100 } },
          plugins: { legend: { display: false } },
        },
      });
    }
  }

  const diffEl = document.getElementById("difficultyBars");
  if (diffEl && summary.difficulty_breakdown) {
    const colors = { easy: "#9be9a8", medium: "#40c463", hard: "#216e39" };
    diffEl.innerHTML = Object.entries(summary.difficulty_breakdown)
      .map(
        ([level, pct]) => `
        <div>
          <div class="d-flex justify-content-between small mb-1">
            <span class="text-white text-capitalize">${level}</span>
            <span class="text-muted">${pct}%</span>
          </div>
          <div class="progress" style="height: 8px;">
            <div class="progress-bar" style="width: ${pct}%; background: ${colors[level] || "#40c463"}"></div>
          </div>
        </div>`
      )
      .join("");
  }

  const weeklyEl = document.getElementById("weeklyProgressChart");
  if (weeklyEl) {
    const buckets = [0, 0, 0, 0, 0, 0, 0];
    results.forEach((_, idx) => (buckets[idx % 7] += 1));
    new Chart(weeklyEl, {
      type: "bar",
      data: {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets: [{
          label: "Sessions",
          data: buckets,
          backgroundColor: "rgba(64, 196, 99, 0.55)",
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
      },
    });
  }
});
