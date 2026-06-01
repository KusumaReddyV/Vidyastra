document.addEventListener("DOMContentLoaded", () => {
  const data = window.resumeProgress || {};
  const trend = data.ats_trend || [];
  const el = document.getElementById("resumeAtsTrendChart");
  if (!el || !window.Chart || !trend.length) return;

  const isDark = document.documentElement.getAttribute("data-bs-theme") !== "light";
  const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
  const tickColor = isDark ? "#94a3b8" : "#64748b";

  new Chart(el, {
    type: "line",
    data: {
      labels: trend.map((t) => t.label),
      datasets: [
        {
          label: "ATS %",
          data: trend.map((t) => t.score),
          borderColor: "#f59e0b",
          backgroundColor: "rgba(245, 158, 11, 0.2)",
          tension: 0.35,
          fill: true,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: false,
          suggestedMin: 40,
          suggestedMax: 100,
          grid: { color: gridColor },
          ticks: { color: tickColor },
        },
        x: {
          grid: { display: false },
          ticks: { color: tickColor },
        },
      },
      plugins: { legend: { display: false } },
      animation: { duration: 500, easing: "easeOutQuart" },
    },
  });
});
