function openLogModal() {
  document.getElementById("logModal").style.display = "flex";
}

function closeLogModal() {
  document.getElementById("logModal").style.display = "none";
}

function openSubmitModal() {
  document.getElementById("submitModal").style.display = "flex";
}

function closeSubmitModal() {
  document.getElementById("submitModal").style.display = "none";
}

async function logClaim() {
  const user = localStorage.getItem("user");

  const purpose = document.getElementById("purpose").value;
  const date = document.getElementById("date").value;
  const type = document.getElementById("type").value;

  const res = await fetch(`${API_BASE}/claims/log?employee_id=${user}&claim_type=${type}&purpose=${purpose}&date=${date}`, {
    method: "POST"
  });

  const data = await res.json();

  document.getElementById("seq").innerText = "Sequence Code: " + data.sequence_code;
}

async function submitClaim() {
  const seq = document.getElementById("seqCode").value;
  const amount = document.getElementById("amount").value;
  const date = document.getElementById("submitDate").value;
  const purpose = document.getElementById("purpose2").value;
  const file = document.getElementById("file").files[0];

  const formData = new FormData();
  formData.append("file", file);

  const url = `${API_BASE}/claims/submit?sequence_code=${seq}&category=Meals&amount=${amount}&date=${date}&purpose=${purpose}`;

  const res = await fetch(url, {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  document.getElementById("result").innerHTML = `
    <p class="${data.status.toLowerCase()}">${data.status}</p>
    <p>${data.reason}</p>
  `;
}