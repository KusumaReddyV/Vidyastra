document.addEventListener("DOMContentLoaded", () => {
  const scores = window.quizScores || [];
  const chartTarget = document.getElementById("progressChart");
  if (chartTarget) {
    new Chart(chartTarget, {
      type: "line",
      data: {
        labels: scores.map((_, idx) => `Attempt ${idx + 1}`),
        datasets: [
          {
            label: "Quiz Score",
            data: scores,
            borderColor: "#8b5cf6",
            backgroundColor: "rgba(139, 92, 246, 0.2)",
            tension: 0.35,
            fill: true,
          },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  const chatToggle = document.getElementById("chatToggle");
  const chatPanel = document.getElementById("chatPanel");
  const chatInput = document.getElementById("chatInput");
  const chatSend = document.getElementById("chatSend");
  const chatMessages = document.getElementById("chatMessages");
  const chatError = document.getElementById("chatError");

  if (chatToggle && chatPanel) {
    chatToggle.addEventListener("click", () => chatPanel.classList.toggle("d-none"));
  }

  async function askMentor() {
    const question = (chatInput?.value || "").trim();
    if (!question) return;
    if (chatError) chatError.classList.add("d-none");
    chatMessages.innerHTML += `<div class="mb-2"><strong>You:</strong> ${question}</div>`;
    chatInput.value = "";
    try {
      const res = await fetch("/api/chatbot/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Request failed");
      chatMessages.innerHTML += `<div class="mb-2"><strong>AI Mentor:</strong> ${data.answer}</div>`;
    } catch (e) {
      if (chatError) {
        chatError.textContent = e?.message || "Failed to contact AI Mentor.";
        chatError.classList.remove("d-none");
      }
      chatMessages.innerHTML += `<div class="mb-2"><strong>AI Mentor:</strong> Sorry—something went wrong. Please try again.</div>`;
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  if (chatSend) chatSend.addEventListener("click", askMentor);
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") askMentor();
    });
  }
});
