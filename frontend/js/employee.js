document.addEventListener("DOMContentLoaded", async () => {
  const employeeId = localStorage.getItem("employee_id");
  const employeeName = localStorage.getItem("employee_name");

  if (!employeeId) {
    window.location.href = "/static/login.html";
    return;
  }

  document.getElementById("employeeWelcome").textContent = `Welcome, ${employeeName || employeeId}`;
  await loadHistory();
  await loadNotifications();
});

function logout() {
  localStorage.clear();
  window.location.href = "/static/login.html";
}

function openRequestModal() {
  document.getElementById("requestModal").classList.remove("hidden");
}

function closeRequestModal() {
  document.getElementById("requestModal").classList.add("hidden");
}

function openSubmitModal(sequenceCode, claimType, plannedPurpose, plannedDate, estimatedBudget, approvedBudget) {
  document.getElementById("submitModal").classList.remove("hidden");
  document.getElementById("submitSequenceCode").value = sequenceCode;
  document.getElementById("submitCategory").value = claimType || "Meals";
  document.getElementById("submitPurpose").value = plannedPurpose || "";
  document.getElementById("submitDate").value = plannedDate || "";
  document.getElementById("submitAmount").value = "";
  document.getElementById("submitFile").value = "";
  hideInlineMessage("submitMessage");

  const budgetInfo = document.getElementById("budgetInfo");
  budgetInfo.classList.remove("hidden");
  budgetInfo.innerHTML = `
    <div><strong>Estimated Budget:</strong> ${estimatedBudget ?? "-"}</div>
    <div><strong>Boss Approved Budget:</strong> ${approvedBudget ?? "-"}</div>
  `;
}

function closeSubmitModal() {
  document.getElementById("submitModal").classList.add("hidden");
}

async function requestClaim() {
  const employeeId = localStorage.getItem("employee_id");
  const claimType = document.getElementById("claimType").value;
  const purpose = document.getElementById("claimPurpose").value.trim();
  const date = document.getElementById("claimDate").value;
  const estimatedBudget = document.getElementById("estimatedBudget").value;

  if (!purpose || !date || !estimatedBudget) {
    showInlineMessage("requestMessage", "Please fill all fields.", true);
    return;
  }

  try {
    const res = await fetch(
      `${API_BASE}/claims/request?employee_id=${encodeURIComponent(employeeId)}&claim_type=${encodeURIComponent(claimType)}&purpose=${encodeURIComponent(purpose)}&date=${encodeURIComponent(date)}&estimated_budget=${encodeURIComponent(estimatedBudget)}`,
      { method: "POST" }
    );
    const data = await res.json();

    if (!res.ok || data.error) {
      showInlineMessage("requestMessage", data.error || "Request failed.", true);
      return;
    }

    showInlineMessage(
      "requestMessage",
      `Claim request created successfully. Internal sequence: ${data.sequence_code}`,
      false
    );

    await loadHistory();
    await loadNotifications();

    setTimeout(() => {
      closeRequestModal();
      document.getElementById("claimPurpose").value = "";
      document.getElementById("claimDate").value = "";
      document.getElementById("estimatedBudget").value = "";
      document.getElementById("claimType").value = "Meals";
      hideInlineMessage("requestMessage");
    }, 700);
  } catch (err) {
    showInlineMessage("requestMessage", "Could not submit request.", true);
  }
}

async function submitClaimDetails() {
  const sequenceCode = document.getElementById("submitSequenceCode").value;
  const category = document.getElementById("submitCategory").value;
  const amount = document.getElementById("submitAmount").value;
  const date = document.getElementById("submitDate").value;
  const purpose = document.getElementById("submitPurpose").value.trim();
  const file = document.getElementById("submitFile").files[0];

  if (!sequenceCode || !amount || !date || !purpose || !file) {
    showInlineMessage("submitMessage", "Please fill all fields and attach a receipt.", true);
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(
      `${API_BASE}/claims/submit-details?sequence_code=${encodeURIComponent(sequenceCode)}&category=${encodeURIComponent(category)}&amount=${encodeURIComponent(amount)}&date=${encodeURIComponent(date)}&purpose=${encodeURIComponent(purpose)}`,
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await res.json();

    if (!res.ok || data.error) {
      showInlineMessage("submitMessage", data.error || "Submission failed.", true);
      return;
    }

    const deductionText = (data.deductions && data.deductions.length)
      ? `<br><strong>Deducted Items:</strong> ${data.deductions.map(d => `${d.group} (${d.amount})`).join(", ")}`
      : "";

    showInlineMessage(
      "submitMessage",
      `Submission completed. Status: ${data.status}. ${data.reason}${deductionText}`,
      false
    );

    await loadHistory();
    await loadNotifications();

    setTimeout(() => {
      closeSubmitModal();
      hideInlineMessage("submitMessage");
    }, 1000);
  } catch (err) {
    showInlineMessage("submitMessage", "Could not submit claim details.", true);
  }
}

async function loadHistory() {
  const employeeId = localStorage.getItem("employee_id");
  const container = document.getElementById("historyContainer");
  container.innerHTML = `<div class="muted">Loading history...</div>`;

  try {
    const res = await fetch(`${API_BASE}/claims/history/${encodeURIComponent(employeeId)}`);
    const data = await res.json();

    if (!Array.isArray(data) || data.length === 0) {
      container.innerHTML = `<div class="muted">No claims found.</div>`;
      return;
    }

    container.innerHTML = data
      .map((claim) => {
        const statusClass = getStatusClass(claim.status);
        const canSubmit = claim.status === "PENDING_SUBMISSION";

        return `
          <div class="history-card">
            <div class="history-top">
              <div>
                <div class="history-seq">${claim.sequence_code}</div>
                <div class="history-meta">${claim.claim_type} • ${claim.planned_date}</div>
              </div>
              <span class="status-pill ${statusClass}">${claim.status}</span>
            </div>

            <div class="history-purpose">${claim.planned_purpose}</div>
            <div class="history-reason"><strong>Estimated Budget:</strong> ${claim.estimated_budget ?? "-"}</div>
            <div class="history-reason"><strong>Approved Budget:</strong> ${claim.approved_budget ?? "-"}</div>

            ${claim.system_reason ? `<div class="history-reason"><strong>System:</strong> ${claim.system_reason}</div>` : ""}
            ${claim.boss_reason ? `<div class="history-reason"><strong>Boss:</strong> ${claim.boss_reason}</div>` : ""}
            ${claim.auditor_reason ? `<div class="history-reason"><strong>Auditor:</strong> ${claim.auditor_reason}</div>` : ""}

            ${canSubmit ? `
              <button class="primary-btn" onclick="openSubmitModal('${claim.sequence_code}', '${claim.claim_type}', '${escapeHtml(claim.planned_purpose)}', '${claim.planned_date}', '${claim.estimated_budget ?? ""}', '${claim.approved_budget ?? ""}')">
                Submit Expense Details
              </button>
            ` : ""}
          </div>
        `;
      })
      .join("");
  } catch (err) {
    container.innerHTML = `<div class="error-text">Could not load history.</div>`;
  }
}

async function loadNotifications() {
  const employeeId = localStorage.getItem("employee_id");
  const container = document.getElementById("notificationContainer");
  container.innerHTML = `<div class="muted">Loading notifications...</div>`;

  try {
    const res = await fetch(`${API_BASE}/notifications/employee/${encodeURIComponent(employeeId)}`);
    const data = await res.json();

    if (!Array.isArray(data) || data.length === 0) {
      container.innerHTML = `<div class="muted">No notifications yet.</div>`;
      return;
    }

    container.innerHTML = data
      .map(
        (n) => `
          <div class="notification-card">
            <div>${n.message}</div>
            <small>${n.created_at}</small>
          </div>
        `
      )
      .join("");
  } catch (err) {
    container.innerHTML = `<div class="error-text">Could not load notifications.</div>`;
  }
}

function getStatusClass(status) {
  if (status === "APPROVED") return "approved";
  if (status === "DECLINED" || status === "DECLINED_BY_BOSS") return "declined";
  if (status === "FLAGGED") return "flagged";
  if (status === "PENDING_BOSS_APPROVAL" || status === "PENDING_SUBMISSION") return "pending";
  return "neutral";
}

function showInlineMessage(id, message, isError = false) {
  const el = document.getElementById(id);
  el.classList.remove("hidden");
  el.className = `inline-message ${isError ? "error" : "success"}`;
  el.innerHTML = message;
}

function hideInlineMessage(id) {
  const el = document.getElementById(id);
  el.classList.add("hidden");
  el.textContent = "";
}

function escapeHtml(text) {
  return text.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
}