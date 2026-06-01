document.addEventListener("DOMContentLoaded", () => {
  const $ = (id) => document.getElementById(id);
  const messages = $("mentorMessages");
  const input = $("mentorInput");
  const send = $("mentorSend");
  const clear = $("mentorClear");
  const error = $("mentorError");
  const hint = $("mentorHint");

  const setError = (msg) => {
    if (!error) return;
    error.textContent = msg || "";
    error.classList.toggle("d-none", !msg);
  };

  const formatText = (text) => {
    return String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  };

  const append = (role, text) => {
    if (!messages) return;
    const div = document.createElement("div");
    div.className = "mb-3 p-3 rounded-3";
    div.style.background = role === "You" ? "rgba(99,102,241,0.08)" : "rgba(255,255,255,0.04)";
    div.innerHTML = `
      <div class="text-muted small mb-1">${role}</div>
      <div class="mentor-msg text-white">${formatText(text)}</div>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  };

  const ask = async () => {
    const q = (input?.value || "").trim();
    if (!q) return;
    setError("");
    append("You", q);
    input.value = "";
    if (send) send.disabled = true;

    try {
      const res = await fetch("/api/chatbot/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Request failed");
      append("Mentor", data.answer || "No answer returned.");
    } catch (e) {
      setError(e?.message || "Could not get a response.");
    } finally {
      if (send) send.disabled = false;
      input?.focus?.();
    }
  };

  send?.addEventListener("click", ask);
  input?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") ask();
  });
  clear?.addEventListener("click", async () => {
    setError("");
    if (messages) messages.innerHTML = "";
    try {
      await fetch("/api/chatbot/reset", { method: "POST" });
    } catch (_) {}
    append(
      "Mentor",
      "Hi! I can help with study plans, resume tips, DSA, placements, and career roadmaps. Ask a question or pick a suggested prompt."
    );
    input?.focus?.();
  });

  document.querySelectorAll(".mentor-suggestion").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (!input) return;
      input.value = btn.textContent.trim();
      ask();
    });
  });

  if (hint) {
    hint.textContent =
      "Personalized guidance from your profile and resume. Suggested prompts are on the right.";
  }

  append(
    "Mentor",
    "Hi! I can help with study plans, resume tips, DSA, placements, and career roadmaps. Ask a question or pick a suggested prompt."
  );
});
