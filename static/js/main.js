// CampusSkill AI — Client JavaScript Helpers
document.addEventListener("DOMContentLoaded", () => {
  // 1. Auto-dismiss flash alerts after 6 seconds
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach((alert) => {
    setTimeout(() => {
      try {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        bsAlert.close();
      } catch (e) {}
    }, 6000);
  });

  // 2. Interactive Roadmap AJAX Toggle
  const roadmapForms = document.querySelectorAll(".roadmap-toggle-form");
  roadmapForms.forEach((form) => {
    const checkbox = form.querySelector(".roadmap-checkbox");
    if (checkbox) {
      checkbox.addEventListener("change", async () => {
        const itemRow = form.closest(".roadmap-item");
        const actionUrl = form.action;
        const csrfToken = form.querySelector('input[name="csrf_token"]')?.value;

        try {
          const response = await fetch(actionUrl, {
            method: "POST",
            headers: {
              "X-Requested-With": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({ csrf_token: csrfToken }),
          });

          if (response.ok) {
            const data = await response.json();
            if (data.is_completed) {
              itemRow.classList.add("completed");
            } else {
              itemRow.classList.remove("completed");
            }

            // Update progress bar & label if present
            const progressBar = document.getElementById("roadmapProgressBar");
            const progressLabel = document.getElementById("roadmapProgressLabel");
            if (progressBar && data.completion_percentage !== undefined) {
              progressBar.style.width = `${data.completion_percentage}%`;
            }
            if (progressLabel && data.completion_percentage !== undefined) {
              progressLabel.textContent = `${data.completion_percentage}%`;
            }
          }
        } catch (err) {
          // Fallback to standard form submit if fetch fails
          form.submit();
        }
      });
    }
  });

  // 3. Assessment Countdown Timer
  const timerElem = document.getElementById("assessmentTimer");
  if (timerElem) {
    let durationSeconds = parseInt(timerElem.dataset.duration || "900", 10);
    const form = document.getElementById("assessmentForm");
    const timeTakenInput = document.getElementById("timeTakenInput");
    let elapsedSeconds = 0;

    const timerInterval = setInterval(() => {
      durationSeconds--;
      elapsedSeconds++;

      if (timeTakenInput) {
        timeTakenInput.value = elapsedSeconds;
      }

      if (durationSeconds <= 0) {
        clearInterval(timerInterval);
        alert("Time is up! Submitting your assessment automatically.");
        if (form) form.submit();
        return;
      }

      const mins = Math.floor(durationSeconds / 60);
      const secs = durationSeconds % 60;
      timerElem.textContent = `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;

      if (durationSeconds <= 60) {
        timerElem.classList.add("text-danger");
      }
    }, 1000);
  }
});
