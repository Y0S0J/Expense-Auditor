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
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    showStatus(policyStatus, "Uploading and parsing policy...");
    const response = await fetch(`${API_BASE_URL}/upload-policy`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok || data.error) throw new Error(data.error || "Policy upload failed");
    showStatus(policyStatus, "Policy uploaded and rules generated successfully.");
  } catch (err) {
    showStatus(policyStatus, `Error: ${err.message}`, true);
  }
});

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const fileInput = document.getElementById("receiptFile");
  const description = document.getElementById("description").value;

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
    if (!response.ok || data.error) throw new Error(data.error || "Receipt upload failed");

    document.getElementById("filename").value = data.filename;
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
    resultContent.textContent = "Running audit...";

    const response = await fetch(`${API_BASE_URL}/audit`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok || data.error) throw new Error(data.error || "Audit failed");

    resultContent.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultContent.textContent = `Error: ${err.message}`;
  }
});

function showStatus(el, message, isError = false) {
  el.classList.remove("hidden");
  el.textContent = message;
  el.style.background = isError ? "#fef2f2" : "#eef6ff";
  el.style.border = `1px solid ${isError ? "#fca5a5" : "#bfdbfe"}`;
}