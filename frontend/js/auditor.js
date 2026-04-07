async function loadFlagged() {
  const res = await fetch(`${API_BASE}/auditor/flagged`);
  const data = await res.json();

  const container = document.getElementById("claims");
  container.innerHTML = "";

  data.forEach(claim => {
    const div = document.createElement("div");

    div.innerHTML = `
      <div class="card">
        <p><b>Sequence:</b> ${claim[1]}</p>
        <p><b>Status:</b> ${claim[12]}</p>

        <button onclick="decide('${claim[1]}', 'Approved')">Approve</button>
        <button onclick="decide('${claim[1]}', 'Declined')">Decline</button>
      </div>
    `;

    container.appendChild(div);
  });
}

async function decide(seq, decision) {
  await fetch(`${API_BASE}/auditor/decision?sequence_code=${seq}&decision=${decision}&reason=Reviewed`, {
    method: "POST"
  });

  alert("Updated!");
  loadFlagged();
}