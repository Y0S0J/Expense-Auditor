document.addEventListener("DOMContentLoaded", async () => {
  const bossId = localStorage.getItem("boss_id");
  const bossName = localStorage.getItem("boss_name");

  if (!bossId) {
    window.location.href = "/static/login.html";
    return;
  }

  document.getElementById("bossWelcome").textContent = `Welcome, ${bossName || bossId}`;
  await loadPendingBossClaims();
});

function logout() {
  localStorage.clear();
  window.location.href = "/static/login.html";
}

async function loadPendingBossClaims() {
  const bossId = localStorage.getItem("boss_id");
  const container = document.getElementById("bossClaimsContainer");
  container.innerHTML = `<div class="muted">Loading pending approvals...</div>`;

  try {
    const res = await fetch(`${API_BASE}/boss/pending/${encodeURIComponent(bossId)}`);
    const data = await res.json();

    if (!Array.isArray(data) || data.length === 0) {
      container.innerHTML = `<div class="muted">No pending boss approvals.</div>`;
      return;
    }

    container.innerHTML = data
      .map(
        (claim) => `
          <div class="history-card">
            <div class="history-top">
              <div>
                <div class="history-seq">${claim.sequence_code}</div>
                <div class="history-meta">${claim.claim_type} • ${claim.planned_date}</div>
              </div>
              <span class="status-pill pending">${claim.status}</span>
            </div>

            <div class="history-purpose"><strong>Employee:</strong> ${claim.employee_id}</div>
            <div class="history-purpose">${claim.planned_purpose}</div>

            <div class="action-row">
              <button class="primary-btn" onclick="openBossDecisionModal('${claim.sequence_code}', 'APPROVE', '${claim.employee_id}', '${claim.claim_type}', '${escapeHtml(claim.planned_purpose)}')">Approve</button>
              <button class="danger-btn" onclick="openBossDecisionModal('${claim.sequence_code}', 'DECLINE', '${claim.employee_id}', '${claim.claim_type}', '${escapeHtml(claim.planned_purpose)}')">Decline</button>
            </div>
          </div>
        `
      )
      .join("");
  } catch (err) {
    container.innerHTML = `<div class="error-text">Could not load boss approvals.</div>`;
  }
}

function openBossDecisionModal(sequenceCode, decisionType, employeeId, claimType, purpose) {
  document.getElementById("bossDecisionModal").classList.remove("hidden");
  document.getElementById("bossDecisionSequence").value = sequenceCode;
  document.getElementById("bossDecisionType").value = decisionType;
  document.getElementById("bossDecisionReason").value = "";
  document.getElementById("bossDecisionInfo").innerHTML = `
    <div><strong>Sequence:</strong> ${sequenceCode}</div>
    <div><strong>Employee:</strong> ${employeeId}</div>
    <div><strong>Type:</strong> ${claimType}</div>
    <div><strong>Purpose:</strong> ${purpose}</div>
    <div><strong>Decision:</strong> ${decisionType}</div>
  `;
  hideInlineMessage("bossDecisionMessage");
}

function closeBossDecisionModal() {
  document.getElementById("bossDecisionModal").classList.add("hidden");
}

async function submitBossDecision() {
  const sequenceCode = document.getElementById("bossDecisionSequence").value;
  const decision = document.getElementById("bossDecisionType").value;
  const reason = document.getElementById("bossDecisionReason").value.trim();

  if (!reason) {
    showInlineMessage("bossDecisionMessage", "Please enter a reason.", true);
    return;
  }

  try {
    const res = await fetch(
      `${API_BASE}/boss/decision?sequence_code=${encodeURIComponent(sequenceCode)}&decision=${encodeURIComponent(decision)}&reason=${encodeURIComponent(reason)}`,
      { method: "POST" }
    );

    const data = await res.json();

    if (!res.ok || data.error) {
      showInlineMessage("bossDecisionMessage", data.error || "Could not record decision.", true);
      return;
    }

    showInlineMessage("bossDecisionMessage", `Decision saved: ${data.new_status}`, false);

    await loadPendingBossClaims();

    setTimeout(() => {
      closeBossDecisionModal();
    }, 700);
  } catch (err) {
    showInlineMessage("bossDecisionMessage", "Could not connect to backend.", true);
  }
}

function showInlineMessage(id, message, isError = false) {
  const el = document.getElementById(id);
  el.classList.remove("hidden");
  el.className = `inline-message ${isError ? "error" : "success"}`;
  el.textContent = message;
}

function hideInlineMessage(id) {
  const el = document.getElementById(id);
  el.classList.add("hidden");
  el.textContent = "";
}

function escapeHtml(text) {
  return text.replace(/'/g, "&#39;").replace(/"/g, "&quot;");
}