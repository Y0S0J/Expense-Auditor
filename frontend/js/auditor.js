document.addEventListener("DOMContentLoaded", async () => {
  const auditorId = localStorage.getItem("auditor_id");
  const auditorName = localStorage.getItem("auditor_name");

  if (!auditorId) {
    window.location.href = "/static/login.html";
    return;
  }

  document.getElementById("auditorWelcome").textContent = `Welcome, ${auditorName || auditorId}`;
  await loadFlaggedClaims();
});

function logout() {
  localStorage.clear();
  window.location.href = "/static/login.html";
}

async function loadFlaggedClaims() {
  const res = await fetch(`${API_BASE}/auditor/flagged`);
  const data = await res.json();

  const container = document.getElementById("claims");
  container.innerHTML = "";

  if (!Array.isArray(data) || data.length === 0) {
    container.innerHTML = `<div class="muted">No flagged claims found.</div>`;
    return;
  }

  data.forEach((claim) => {
    const div = document.createElement("div");
    const encoded = encodeClaim(claim);

    div.innerHTML = `
      <div class="history-card">
        <div class="history-top">
          <div>
            <div class="history-seq">${claim.sequence_code}</div>
            <div class="history-meta">${claim.claim_type} • ${claim.actual_date || claim.planned_date || "-"}</div>
          </div>
          <span class="status-pill flagged">${claim.status}</span>
        </div>

        <div class="history-purpose"><strong>Employee:</strong> ${claim.employee_id}</div>
        <div class="history-purpose"><strong>Planned Purpose:</strong> ${claim.planned_purpose}</div>
        <div class="history-purpose"><strong>Actual Purpose:</strong> ${claim.actual_purpose || "-"}</div>
        <div class="history-purpose"><strong>Claimed Amount:</strong> ${claim.actual_amount ?? "-"}</div>
        <div class="history-purpose"><strong>Adjusted Amount:</strong> ${claim.adjusted_amount ?? "-"}</div>
        <div class="history-purpose"><strong>OCR Amount:</strong> ${claim.ocr_amount ?? "-"}</div>
        <div class="history-reason"><strong>System Reason:</strong> ${claim.system_reason || "-"}</div>

        <div class="action-row">
          <button class="primary-btn" onclick="openAuditorDecisionModal('${encoded}', 'APPROVED')">Approve</button>
          <button class="danger-btn" onclick="openAuditorDecisionModal('${encoded}', 'DECLINED')">Decline</button>
          <button class="sidebar-btn secondary" onclick="openAuditorDecisionModal('${encoded}', 'RESUBMIT')">Ask To Resubmit</button>
        </div>
      </div>
    `;

    container.appendChild(div);
  });
}

function encodeClaim(claim) {
  return btoa(unescape(encodeURIComponent(JSON.stringify(claim))));
}

function decodeClaim(encoded) {
  return JSON.parse(decodeURIComponent(escape(atob(encoded))));
}

function openAuditorDecisionModal(encodedClaim, decisionType) {
  const claim = decodeClaim(encodedClaim);

  document.getElementById("auditorDecisionModal").classList.remove("hidden");
  document.getElementById("auditorDecisionSequence").value = claim.sequence_code;
  document.getElementById("auditorDecisionType").value = decisionType;
  document.getElementById("auditorDecisionReason").value = "";
  hideInlineMessage("auditorDecisionMessage");

  document.getElementById("auditorDecisionInfo").innerHTML = `
    <div><strong>Sequence:</strong> ${claim.sequence_code}</div>
    <div><strong>Employee:</strong> ${claim.employee_id}</div>
    <div><strong>Claim Type:</strong> ${claim.claim_type}</div>
    <div><strong>Planned Purpose:</strong> ${claim.planned_purpose}</div>
    <div><strong>Actual Purpose:</strong> ${claim.actual_purpose || "-"}</div>
    <div><strong>Claimed Amount:</strong> ${claim.actual_amount ?? "-"}</div>
    <div><strong>Adjusted Amount:</strong> ${claim.adjusted_amount ?? "-"}</div>
    <div><strong>OCR Amount:</strong> ${claim.ocr_amount ?? "-"}</div>
    <div><strong>Decision:</strong> ${decisionType}</div>
  `;

  const receiptImg = document.getElementById("auditorReceiptPreview");
  const noReceipt = document.getElementById("auditorNoReceipt");

  if (claim.receipt_path) {
    const filename = claim.receipt_path.split(/[\\/]/).pop();
    receiptImg.src = `/receipts/${filename}`;
    receiptImg.classList.remove("hidden");
    noReceipt.classList.add("hidden");
  } else {
    receiptImg.classList.add("hidden");
    noReceipt.classList.remove("hidden");
  }
}

function closeAuditorDecisionModal() {
  document.getElementById("auditorDecisionModal").classList.add("hidden");
}

async function submitAuditorDecision() {
  const seq = document.getElementById("auditorDecisionSequence").value;
  const decision = document.getElementById("auditorDecisionType").value;
  const reason = document.getElementById("auditorDecisionReason").value.trim();

  if (!reason) {
    showInlineMessage("auditorDecisionMessage", "Please enter a reason.", true);
    return;
  }

  const res = await fetch(
    `${API_BASE}/auditor/decision?sequence_code=${encodeURIComponent(seq)}&decision=${encodeURIComponent(decision)}&reason=${encodeURIComponent(reason)}`,
    { method: "POST" }
  );

  const data = await res.json();

  if (!res.ok || data.error) {
    showInlineMessage("auditorDecisionMessage", data.error || "Could not update claim.", true);
    return;
  }

  showInlineMessage("auditorDecisionMessage", "Updated successfully.", false);
  await loadFlaggedClaims();

  setTimeout(() => {
    closeAuditorDecisionModal();
  }, 700);
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