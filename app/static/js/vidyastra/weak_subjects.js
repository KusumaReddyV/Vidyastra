document.addEventListener("DOMContentLoaded", () => {
  const data = Array.isArray(window.weakTopics) ? window.weakTopics : [];
  
  // Main weak topics bar chart
  const el = document.getElementById("weakTopicsChart");
  if (el && window.Chart) {
    const labels = data.map((d) => d.topic || "general");
    const values = data.map((d) => Number(d.avg_score || 0));

    new Chart(el, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "Avg Score (%)",
            data: values,
            backgroundColor: "rgba(239, 68, 68, 0.25)",
            borderColor: "rgba(239, 68, 68, 0.85)",
            borderWidth: 1,
            borderRadius: 10,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } },
        },
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: (ctx) => `${ctx.parsed.y}%` } },
        },
        animation: { duration: 450, easing: "easeOutQuart" },
      },
    });
  }

  // Performance distribution pie chart
  const distEl = document.getElementById("performanceDistributionChart");
  if (distEl && window.Chart && data.length > 0) {
    const scoreRanges = { "0-30%": 0, "31-50%": 0, "51-70%": 0, "71-100%": 0 };
    data.forEach(d => {
      const score = Number(d.avg_score || 0);
      if (score <= 30) scoreRanges["0-30%"]++;
      else if (score <= 50) scoreRanges["31-50%"]++;
      else if (score <= 70) scoreRanges["51-70%"]++;
      else scoreRanges["71-100%"]++;
    });

    new Chart(distEl, {
      type: "doughnut",
      data: {
        labels: Object.keys(scoreRanges),
        datasets: [{
          data: Object.values(scoreRanges),
          backgroundColor: [
            "rgba(239, 68, 68, 0.8)",
            "rgba(249, 115, 22, 0.8)",
            "rgba(234, 179, 8, 0.8)",
            "rgba(34, 197, 94, 0.8)",
          ],
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { color: "#9ca3af", font: { size: 11 } } },
        },
      },
    });
  }

  // Time vs Performance scatter chart
  const timeEl = document.getElementById("timePerformanceChart");
  if (timeEl && window.Chart && data.length > 0) {
    const scatterData = data.map(d => ({
      x: Number(d.avg_time_spent_seconds || 0) / 60, // Convert to minutes
      y: Number(d.avg_score || 0),
      label: d.topic || "general",
    }));

    new Chart(timeEl, {
      type: "scatter",
      data: {
        datasets: [{
          label: "Topics",
          data: scatterData,
          backgroundColor: "rgba(139, 92, 246, 0.7)",
          borderColor: "rgba(139, 92, 246, 1)",
          pointRadius: 8,
          pointHoverRadius: 10,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { 
            title: { display: true, text: "Avg Time (min)", color: "#9ca3af" },
            ticks: { color: "#9ca3af" },
            grid: { color: "rgba(255,255,255,0.1)" }
          },
          y: { 
            title: { display: true, text: "Avg Score (%)", color: "#9ca3af" },
            ticks: { color: "#9ca3af" },
            grid: { color: "rgba(255,255,255,0.1)" },
            min: 0,
            max: 100
          },
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const point = ctx.raw;
                return `${point.label}: ${point.y.toFixed(1)}% in ${point.x.toFixed(1)}min`;
              }
            }
          }
        },
      },
    });
  }
});

