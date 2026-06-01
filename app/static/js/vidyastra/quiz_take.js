(() => {
  const STORAGE_KEY = "vidyastra_active_quiz";
  const $ = (id) => document.getElementById(id);

  const emptyEl = $("quizTakeEmpty");
  const activeEl = $("quizTakeActive");
  const takeForm = $("takeForm");
  const takeResults = $("takeResults");
  const takeError = $("takeError");

  let quiz = null;
  let currentIndex = 0;
  let timer = { handle: null, remaining: 300, startedAt: Date.now() };

  const norm = (s) => String(s || "").trim().toLowerCase();
  const fmtTime = (s) => {
    const m = Math.max(0, Math.floor(s / 60));
    const ss = Math.max(0, s % 60);
    return `${String(m).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
  };
  const setVisible = (el, on) => el && el.classList.toggle("d-none", !on);
  const showError = (msg) => {
    if (!takeError) return;
    takeError.textContent = msg || "";
    setVisible(takeError, !!msg);
  };

  const stopTimer = () => {
    if (timer.handle) clearInterval(timer.handle);
    timer.handle = null;
  };

  const getUserAnswer = (q) => {
    const qid = q.id || `q-${currentIndex}`;
    if ((q.type || "mcq") === "mcq") {
      const checked = takeForm.querySelector(`input[name="${CSS.escape(qid)}"]:checked`);
      return checked ? checked.value : "";
    }
    const ta = takeForm.querySelector(`textarea[name="${CSS.escape(qid)}"]`);
    return (ta?.value || "").trim();
  };

  const saveAnswerForIndex = (idx) => {
    const q = quiz.questions[idx];
    if (!q) return;
    q._userAnswer = getUserAnswer(q);
  };

  const restoreAnswerForIndex = (idx) => {
    const q = quiz.questions[idx];
    if (!q) return;
    const qid = q.id || `q-${idx}`;
    if ((q.type || "mcq") === "mcq" && q._userAnswer) {
      const input = takeForm.querySelector(`input[name="${CSS.escape(qid)}"][value="${CSS.escape(q._userAnswer)}"]`);
      if (input) input.checked = true;
    } else if (q._userAnswer) {
      const ta = takeForm.querySelector(`textarea[name="${CSS.escape(qid)}"]`);
      if (ta) ta.value = q._userAnswer;
    }
  };

  const updateProgress = () => {
    const total = quiz?.questions?.length || 0;
    const answered = quiz.questions.filter((q) => q._userAnswer).length;
    $("takeProgress").textContent = `${currentIndex + 1} / ${total}`;
    $("takeProgressBar").style.width = total ? `${((currentIndex + 1) / total) * 100}%` : "0%";
    $("takePrevBtn").disabled = currentIndex <= 0;
    const isLast = currentIndex >= total - 1;
    setVisible($("takeNextBtn"), !isLast);
    setVisible($("takeSubmitBtn"), isLast);
  };

  const renderCurrentQuestion = () => {
    const q = quiz.questions[currentIndex];
    if (!q) return;
    const qid = q.id || `q-${currentIndex}`;

    $("takeQNumber").textContent = `Question ${currentIndex + 1} of ${quiz.questions.length}`;
    $("takeQuestionText").textContent = q.question || "";
    takeForm.innerHTML = "";

    if ((q.type || "mcq") === "mcq") {
      (q.options || []).forEach((opt, i) => {
        const id = `${qid}-opt-${i}`;
        const row = document.createElement("label");
        row.className = "vid-quiz-option";
        row.htmlFor = id;
        row.innerHTML = `
          <input class="form-check-input" type="radio" name="${qid}" id="${id}" value="${String(opt).replace(/"/g, "&quot;")}">
          <span class="vid-quiz-option-label">${opt}</span>
        `;
        row.querySelector("input").addEventListener("change", () => {
          q._userAnswer = opt;
          document.querySelectorAll(".vid-quiz-option").forEach((el) => el.classList.remove("selected"));
          row.classList.add("selected");
        });
        takeForm.appendChild(row);
      });
    } else {
      const ta = document.createElement("textarea");
      ta.className = "form-control vid-quiz-code-input";
      ta.rows = 5;
      ta.name = qid;
      ta.placeholder = "Write your answer here…";
      ta.addEventListener("input", () => {
        q._userAnswer = ta.value.trim();
      });
      takeForm.appendChild(ta);
    }

    restoreAnswerForIndex(currentIndex);
    document.querySelectorAll(".vid-quiz-option").forEach((el) => {
      const inp = el.querySelector("input");
      if (inp?.checked) el.classList.add("selected");
    });
    updateProgress();
  };

  const startTimer = (seconds) => {
    stopTimer();
    timer.remaining = Number(seconds || 300);
    timer.startedAt = Date.now();
    const timerEl = $("takeTimer");
    const tick = () => {
      timerEl.textContent = fmtTime(timer.remaining);
      timerEl.classList.toggle("quiz-timer-urgent", timer.remaining <= 60);
      if (timer.remaining <= 0) {
        stopTimer();
        submitQuiz(true);
      }
    };
    tick();
    timer.handle = setInterval(() => {
      timer.remaining -= 1;
      tick();
    }, 1000);
  };

  const grade = () => {
    saveAnswerForIndex(currentIndex);
    let correct = 0;
    const review = [];
    for (const q of quiz.questions) {
      const userAnswer = q._userAnswer || "";
      const expected = (q.answer || "").trim();
      const isCorrect = userAnswer && expected && norm(userAnswer) === norm(expected);
      if (isCorrect) correct += 1;
      review.push({ ...q, userAnswer, expected, isCorrect });
    }
    const total = quiz.questions.length;
    return {
      total,
      correct,
      score: total ? Math.round((correct / total) * 100) : 0,
      review,
      timeSpent: Math.min(600, Math.round((Date.now() - timer.startedAt) / 1000)),
    };
  };

  const renderReview = (graded) => {
    const reviewEl = $("takeReview");
    reviewEl.innerHTML = "";
    graded.review.forEach((r, idx) => {
      const card = document.createElement("div");
      card.className = "card p-3 vid-quiz-review-card";
      let optionsHtml = "";
      if ((r.type || "mcq") === "mcq" && Array.isArray(r.options)) {
        optionsHtml = `<div class="mt-3 vstack gap-2">`;
        r.options.forEach((opt) => {
          const isCorrectOpt = norm(opt) === norm(r.expected);
          const isUserWrong = r.userAnswer && norm(opt) === norm(r.userAnswer) && !r.isCorrect;
          let cls = "vid-quiz-option p-2";
          if (isCorrectOpt) cls += " correct";
          if (isUserWrong) cls += " wrong";
          optionsHtml += `<div class="${cls}"><span>${opt}</span></div>`;
        });
        optionsHtml += `</div>`;
      }
      card.innerHTML = `
        <div class="d-flex justify-content-between gap-2 mb-2">
          <div class="text-white fw-semibold">Q${idx + 1}. ${r.question || ""}</div>
          <span class="badge ${r.isCorrect ? "bg-success" : "bg-danger"}">${r.isCorrect ? "Correct" : "Incorrect"}</span>
        </div>
        ${optionsHtml}
        <div class="small text-muted mt-2">${r.explanation || ""}</div>`;
      reviewEl.appendChild(card);
    });
  };

  const submitQuiz = async (auto = false) => {
    if (!quiz) return;
    stopTimer();
    const graded = grade();
    document.querySelector(".vid-quiz-question-card")?.classList.add("d-none");
    $("takePrevBtn")?.classList.add("d-none");
    $("takeNextBtn")?.classList.add("d-none");
    $("takeSubmitBtn")?.classList.add("d-none");
    setVisible(takeResults, true);

    $("takeScore").textContent = `${graded.score}%`;
    $("takeScoreMeta").textContent = `${graded.correct} of ${graded.total} correct · ${fmtTime(graded.timeSpent)}${auto ? " · auto-submitted" : ""}`;
    const ring = $("takeScoreRing");
    if (ring) {
      ring.innerHTML = `<div class="progress mx-auto" style="height: 10px; max-width: 280px;"><div class="progress-bar bg-success" style="width: ${graded.score}%"></div></div>`;
    }
    renderReview(graded);

    try {
      await fetch("/api/quiz/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          quiz_id: quiz.quiz_id,
          topic: quiz.topic,
          difficulty: quiz.difficulty,
          questions: quiz.questions,
          total_questions: graded.total,
          correct_answers: graded.correct,
          score: graded.score,
          time_spent_seconds: graded.timeSpent,
        }),
      });
    } catch (e) {
      showError("Score shown locally; saving to server failed.");
    }

    sessionStorage.removeItem(STORAGE_KEY);
    if (window.opener && !window.opener.closed) {
      try {
        window.opener.postMessage({ type: "vidyastra_quiz_done", score: graded.score }, "*");
      } catch (e) {}
    }
  };

  const loadQuiz = () => {
    let raw;
    try {
      raw = sessionStorage.getItem(STORAGE_KEY);
    } catch (e) {
      raw = null;
    }
    if (!raw) return;
    try {
      quiz = JSON.parse(raw);
    } catch (e) {
      return;
    }
    if (!quiz?.questions?.length) return;

    setVisible(emptyEl, false);
    setVisible(activeEl, true);
    $("takeTopic").textContent = `${(quiz.topic || "general").toUpperCase()} · ${quiz.difficulty || "adaptive"}`;
    currentIndex = 0;
    renderCurrentQuestion();
    startTimer(quiz.timer_seconds || 300);
  };

  $("takePrevBtn")?.addEventListener("click", () => {
    saveAnswerForIndex(currentIndex);
    if (currentIndex > 0) {
      currentIndex -= 1;
      renderCurrentQuestion();
    }
  });

  $("takeNextBtn")?.addEventListener("click", () => {
    saveAnswerForIndex(currentIndex);
    if (currentIndex < quiz.questions.length - 1) {
      currentIndex += 1;
      renderCurrentQuestion();
    }
  });

  $("takeSubmitBtn")?.addEventListener("click", () => submitQuiz(false));
  loadQuiz();
})();
