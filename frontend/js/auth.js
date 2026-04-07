function openLoginModal() {
  document.getElementById("loginModal").classList.remove("hidden");
}

function closeLoginModal() {
  document.getElementById("loginModal").classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  const roleSelect = document.getElementById("role");
  if (roleSelect) {
    roleSelect.addEventListener("change", updateLoginLabels);
    updateLoginLabels();
  }
});

function updateLoginLabels() {
  const role = document.getElementById("role").value;
  const userLabel = document.getElementById("userLabel");
  const username = document.getElementById("username");

  if (role === "employee") {
    userLabel.textContent = "Employee ID";
    username.placeholder = "Enter employee ID";
  } else if (role === "boss") {
    userLabel.textContent = "Boss ID";
    username.placeholder = "Enter boss ID";
  } else {
    userLabel.textContent = "Auditor ID";
    username.placeholder = "Enter auditor ID";
  }
}

async function login() {
  const role = document.getElementById("role").value;
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || !password) {
    showLoginMessage("Please enter both ID and password.", true);
    return;
  }

  let url = "";

  if (role === "employee") {
    url = `${API_BASE}/login/employee?employee_id=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
  } else if (role === "boss") {
    url = `${API_BASE}/login/boss?boss_id=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
  } else {
    url = `${API_BASE}/login/auditor?auditor_id=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
  }

  try {
    const res = await fetch(url, { method: "POST" });
    const data = await res.json();

    if (!res.ok || data.error) {
      showLoginMessage(data.error || "Login failed.", true);
      return;
    }

    localStorage.setItem("role", role);

    if (role === "employee") {
      localStorage.setItem("employee_id", data.employee_id);
      localStorage.setItem("employee_name", data.name);
      localStorage.setItem("boss_id", data.boss_id);
      window.location.href = "/static/employee.html";
    } else if (role === "boss") {
      localStorage.setItem("boss_id", data.boss_id);
      localStorage.setItem("boss_name", data.name);
      window.location.href = "/static/boss.html";
    } else {
      localStorage.setItem("auditor_id", data.auditor_id);
      localStorage.setItem("auditor_name", data.name);
      window.location.href = "/static/auditor.html";
    }
  } catch (err) {
    showLoginMessage("Could not connect to backend.", true);
  }
}

function showLoginMessage(message, isError = false) {
  const msg = document.getElementById("loginMessage");
  msg.classList.remove("hidden");
  msg.textContent = message;
  msg.className = `inline-message ${isError ? "error" : "success"}`;
}