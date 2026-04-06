const API_BASE_URL = "http://127.0.0.1:8000";

const policyForm = document.getElementById("policyForm");
const policyStatus = document.getElementById("policyStatus");

const uploadForm = document.getElementById("uploadForm");
const uploadStatus = document.getElementById("uploadStatus");

const auditForm = document.getElementById("auditForm");
const auditResult = document.getElementById("auditResult");
const resultContent = document.getElementById("resultContent");

policyForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("policyFile");
  if (!fileInput.files.length) {
    showStatus(policyStatus, "Please select a policy PDF.", true);
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    showStatus(policyStatus, "Uploading and processing policy...");

    const response = await fetch(`${API_BASE_URL}/upload-policy`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "Policy upload failed.");
    }

    showStatus(policyStatus, "Policy uploaded and rules generated successfully.");
  } catch (err) {
    showStatus(policyStatus, `Error: ${err.message}`, true);
  }
});

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("receiptFile");
  const description = document.getElementById("description").value;

  if (!fileInput.files.length) {
    showStatus(uploadStatus, "Please choose a receipt file.", true);
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("description", description);

  try {
    showStatus(uploadStatus, "Uploading receipt...");

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "Receipt upload failed.");
    }

    const filenameInput = document.getElementById("filename");
    if (filenameInput) {
      filenameInput.value = data.filename;
    }

    showStatus(uploadStatus, `Receipt uploaded successfully: ${data.filename}`);
  } catch (err) {
    showStatus(uploadStatus, `Error: ${err.message}`, true);
  }
});

auditForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData();
  formData.append("filename", document.getElementById("filename").value);
  formData.append("category", document.getElementById("category").value);
  formData.append("claimed_amount", document.getElementById("claimedAmount").value);
  formData.append("claimed_date", document.getElementById("claimedDate").value);
  formData.append("business_purpose", document.getElementById("businessPurpose").value);

  try {
    auditResult.classList.remove("hidden");
    resultContent.innerHTML = `<div class="loading-text">Running audit...</div>`;

    const response = await fetch(`${API_BASE_URL}/audit`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "Audit failed.");
    }

    renderAuditResult(data);
  } catch (err) {
    resultContent.innerHTML = `
      <div class="result-card flagged">
        <div class="result-title">⚠️ Error</div>
        <div class="result-reason">${err.message}</div>
      </div>
    `;
  }
});

function renderAuditResult(data) {
  const status = data.result?.status || "Flagged";
  const reason = data.result?.reason || "No reason provided.";

  let statusClass = "flagged";
  let icon = "⚠️";

  if (status === "Approved") {
    statusClass = "approved";
    icon = "✅";
  } else if (status === "Declined") {
    statusClass = "declined";
    icon = "❌";
  } else if (status === "Flagged") {
    statusClass = "flagged";
    icon = "⚠️";
  }

  const merchant = data.ocr_data?.merchant || "Not detected";
  const detectedAmount = data.ocr_data?.detected_amount ?? "Not detected";
  const receiptDate = data.ocr_data?.receipt_date || "Not detected";
  const claimedAmount = data.expense?.claimed_amount ?? "Not provided";
  const claimedDate = data.expense?.claimed_date || "Not provided";
  const category = data.expense?.category || "Not provided";

  resultContent.innerHTML = `
    <div class="result-card ${statusClass}">
      <div class="result-title">${icon} ${status}</div>
      <div class="result-reason">${reason}</div>

      <div class="result-grid">
        <div class="result-item">
          <span class="label">Category</span>
          <span class="value">${category}</span>
        </div>
        <div class="result-item">
          <span class="label">Merchant</span>
          <span class="value">${merchant}</span>
        </div>
        <div class="result-item">
          <span class="label">Claimed Amount</span>
          <span class="value">${claimedAmount}</span>
        </div>
        <div class="result-item">
          <span class="label">Detected Amount</span>
          <span class="value">${detectedAmount}</span>
        </div>
        <div class="result-item">
          <span class="label">Claimed Date</span>
          <span class="value">${claimedDate}</span>
        </div>
        <div class="result-item">
          <span class="label">Receipt Date</span>
          <span class="value">${receiptDate}</span>
        </div>
      </div>
    </div>
  `;
}

function showStatus(el, message, isError = false) {
  el.classList.remove("hidden");
  el.textContent = message;
  el.style.background = isError ? "#fef2f2" : "#eef6ff";
  el.style.border = `1px solid ${isError ? "#fca5a5" : "#bfdbfe"}`;
}