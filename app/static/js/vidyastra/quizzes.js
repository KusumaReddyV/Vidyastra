(() => {
  const STORAGE_KEY = "vidyastra_active_quiz";
  const QUIZ_WINDOW = "vidyastra_quiz_window";
  const $ = (id) => document.getElementById(id);

  const quizGenerateBtn = $("quizGenerateBtn");
  const quizResetBtn = $("quizResetBtn");
  const quizTopic = $("quizTopic");
  const quizDifficulty = $("quizDifficulty");
  const quizTimer = $("quizTimer");
  const quizStatus = $("quizStatus");
  const quizLoading = $("quizLoading");
  const quizError = $("quizError");
  const quizEmpty = $("quizEmpty");

  const setVisible = (el, visible) => el && el.classList.toggle("d-none", !visible);

  const setError = (message) => {
    if (!quizError) return;
    quizError.textContent = message || "";
    setVisible(quizError, !!message);
  };

  const setStatus = (text) => {
    if (quizStatus) quizStatus.textContent = text;
  };

  const openQuizWindow = (quiz) => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(quiz));
    } catch (e) {
      setError("Could not store quiz session.");
      return false;
    }

    const features = "width=980,height=760,scrollbars=yes,resizable=yes";
    let win = window.open("/dashboard/take-quiz", QUIZ_WINDOW, features);
    if (!win) {
      setError("Popup blocked. Allow popups for this site, or click below.");
      const link = document.createElement("a");
      link.href = "/dashboard/take-quiz";
      link.target = "_blank";
      link.className = "btn btn-primary btn-sm mt-2";
      link.textContent = "Open quiz in new tab";
      link.onclick = () => sessionStorage.setItem(STORAGE_KEY, JSON.stringify(quiz));
      quizError.appendChild(document.createElement("br"));
      quizError.appendChild(link);
      return false;
    }
    return true;
  };

  const reset = () => {
    setStatus("Ready");
    if (quizTimer) quizTimer.textContent = "05:00";
    setVisible(quizLoading, false);
    setVisible(quizEmpty, true);
    setError("");
  };

  const generateQuiz = async () => {
    reset();
    setVisible(quizLoading, true);
    setVisible(quizEmpty, false);
    setStatus("Generating");

    try {
      const res = await fetch("/api/quiz/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: (quizTopic?.value || "python").trim() || "python",
          difficulty: (quizDifficulty?.value || "adaptive").trim() || "adaptive",
        }),
      });
      const quiz = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(quiz.error || "Failed to generate quiz");

      quiz.timer_seconds = quiz.timer_seconds || 300;
      setVisible(quizLoading, false);

      if (openQuizWindow(quiz)) {
        setStatus("Quiz open");
        setVisible(quizEmpty, true);
        quizEmpty.innerHTML = `
          <div class="text-center py-4">
            <i class="fas fa-window-restore fa-2x text-primary mb-3"></i>
            <p class="text-white fw-semibold mb-1">Quiz opened in a new window</p>
            <p class="text-muted small mb-3">5-minute timer • answers shown after submit</p>
            <button type="button" class="btn btn-outline-primary btn-sm" id="quizReopenBtn">Re-open quiz window</button>
          </div>`;
        document.getElementById("quizReopenBtn")?.addEventListener("click", () => openQuizWindow(quiz));
        if (quiz.warning) setError(quiz.warning);
      }
    } catch (e) {
      setVisible(quizLoading, false);
      setStatus("Error");
      setError(e?.message || "Something went wrong generating the quiz.");
      setVisible(quizEmpty, true);
      quizEmpty.textContent = "Click Generate Quiz to try again.";
    }
  };

  window.addEventListener("message", (e) => {
    if (e.data?.type === "vidyastra_quiz_done") {
      setStatus(`Done • ${e.data.score}%`);
      setError("");
      window.location.reload();
    }
  });

  if (quizGenerateBtn) quizGenerateBtn.addEventListener("click", generateQuiz);
  if (quizResetBtn) quizResetBtn.addEventListener("click", reset);
  if (quizTimer) quizTimer.textContent = "05:00";
})();
