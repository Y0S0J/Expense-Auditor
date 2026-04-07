function openLogin() {
  document.getElementById("loginModal").style.display = "flex";
}

function closeLogin() {
  document.getElementById("loginModal").style.display = "none";
}

async function login() {
  const role = document.getElementById("role").value;
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    let url = "";

    if (role === "employee") {
      url = `${API_BASE}/login/employee?employee_id=${username}`;
    } else {
      url = `${API_BASE}/login/auditor?username=${username}&password=${password}`;
    }

    const res = await fetch(url, { method: "POST" });
    const data = await res.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    localStorage.setItem("user", username);
    localStorage.setItem("role", role);

    if (role === "employee") {
      window.location.href = "employee.html";
    } else {
      window.location.href = "auditor.html";
    }

  } catch (err) {
    alert("Login failed");
  }
}