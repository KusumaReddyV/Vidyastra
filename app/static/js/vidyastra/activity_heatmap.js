document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("activityHeatmap");
  const data = window.activityHeatmap;
  if (!root || !data?.weeks) return;

  const weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const wrap = document.createElement("div");
  wrap.className = "vid-heatmap-grid";

  const labelCol = document.createElement("div");
  labelCol.className = "vid-heatmap-labels";
  labelCol.innerHTML = `<div class="vid-heatmap-month"></div>` + weekdays.map((d) => `<div class="vid-heatmap-wd">${d}</div>`).join("");
  wrap.appendChild(labelCol);

  const weeksEl = document.createElement("div");
  weeksEl.className = "vid-heatmap-weeks";

  data.weeks.forEach((week) => {
    const col = document.createElement("div");
    col.className = "vid-heatmap-week-col";
    week.forEach((day) => {
      const cell = document.createElement("div");
      cell.className = `vid-heat-cell level-${day.level || 0}`;
      cell.title = day.count
        ? `${day.count} learning activities on ${day.date}`
        : `No activity on ${day.date}`;
      col.appendChild(cell);
    });
    weeksEl.appendChild(col);
  });

  wrap.appendChild(weeksEl);
  root.appendChild(wrap);

  if (!data.total_active_days) {
    const empty = document.createElement("p");
    empty.className = "text-muted small mt-3 mb-0";
    empty.textContent = "Your learning streak will appear here once you begin.";
    root.appendChild(empty);
  }
});
