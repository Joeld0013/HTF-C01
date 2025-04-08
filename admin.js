const sectionLinks = document.querySelectorAll(".nav-link");
const sections = document.querySelectorAll(".section");

// Modal Handling
function openModal() {
  const modal = document.getElementById("employeeModal");
  if (modal) modal.style.display = "flex";

  ["name", "role", "email", "password", "status", "created_time", "facescan", "employeeId"].forEach(id => {
    const field = document.getElementById(id);
    if (field) field.value = "";
  });
  
  document.querySelector('input[name="idOption"][value="auto"]').checked = true;
  document.getElementById("employeeId").style.display = "none";
}

function closeModal() {
  const modal = document.getElementById("employeeModal");
  if (modal) modal.style.display = "none";
}

// Section Switching
function showSection(id) {
  sections.forEach(section => section.classList.remove("active"));
  const sectionToShow = document.getElementById(id);
  if (sectionToShow) sectionToShow.classList.add("active");

  sectionLinks.forEach(link => link.classList.remove("active"));
  const clickedLink = Array.from(sectionLinks).find(link =>
    link.getAttribute("onclick")?.includes(id)
  );
  if (clickedLink) clickedLink.classList.add("active");
}

// Role Map
const roleMap = {
  "Site Supervisor / Foreman": "sitesupervisor",
  "General Laborer": "generallaborer",
  "Electrician": "electrician",
  "Plumber": "plumber",
  "Carpenter": "carpenter",
  "Mason": "mason",
  "Welder": "welder",
  "Crane Operator / Heavy Equipment Operator": "craneoperator",
  "Truck Driver / Material Transporter": "truckdriver",
  "Security Guard": "securityguard"
};

// Function to set role from navbar buttons
function setRole(selectedRole) {
  const roleDropdown = document.getElementById("role");
  if (roleDropdown) {
    roleDropdown.value = selectedRole;
    roleDropdown.dispatchEvent(new Event('change'));
  }
}

// Function to toggle ID input field
function toggleIdInput() {
  const idOption = document.querySelector('input[name="idOption"]:checked').value;
  const idInput = document.getElementById("employeeId");
  
  if (idOption === 'manual') {
    idInput.style.display = "block";
    idInput.required = true;
  } else {
    idInput.style.display = "none";
    idInput.required = false;
    idInput.value = "";
    // Trigger auto-generation when switching back to auto
    document.getElementById("role").dispatchEvent(new Event('change'));
  }
}

// SINGLE confirmManualId function
function confirmManualId() {
  const manualId = document.getElementById('employeeId').value;
  const role = document.getElementById('role').value;
  
  if (!manualId || !role) {
    alert('Please enter an ID and select a role first');
    return;
  }

  fetch(`generate_email.php?role=${encodeURIComponent(role)}&manual_id=${manualId}&t=${Date.now()}`)
    .then(response => {
      if (!response.ok) throw new Error('Network error');
      return response.json();
    })
    .then(data => {
      if (data.status === "success") {
        document.getElementById('email').value = data.email;
        document.getElementById('password').value = data.password;
      } else {
        throw new Error(data.message || 'Failed to confirm ID');
      }
    })
    .catch(error => {
      alert(`Error: ${error.message}`);
      document.getElementById('role').dispatchEvent(new Event('change'));
    });
}

// SINGLE role change event listener
document.getElementById("role").addEventListener("change", function() {
  const role = this.value;
  const roleId = roleMap[role];
  
  if (!roleId) {
    document.getElementById("email").value = "";
    document.getElementById("password").value = "";
    return;
  }

  fetch(`generate_email.php?role=${encodeURIComponent(role)}&t=${Date.now()}`)
    .then(response => {
      if (!response.ok) throw new Error('Network error');
      return response.json();
    })
    .then(data => {
      if (data.status === "success") {
        document.getElementById("email").value = data.email;
        document.getElementById("password").value = data.password;
        document.getElementById("status").value = "Inactive";
        document.getElementById("created_time").value = new Date().toISOString().slice(0, 19).replace("T", " ");
      } else {
        throw new Error(data.message || 'Failed to generate credentials');
      }
    })
    .catch(error => {
      console.error("Error:", error);
      alert("❌ Failed to generate email:\n" + error.message);
    });
});

document.getElementById("employeeForm").addEventListener("submit", function(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById("name").value,
        role: document.getElementById("role").value
    };

    fetch("add_employee.php", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) throw new Error("Network error");
        return response.json();
    })
    .then(data => {
        if (data.status === "success") {
            alert(`Employee added successfully!\nEmail: ${data.email}\nPassword: ${data.password}`);
            closeModal();
            location.reload();
        } else {
            throw new Error(data.message || "Failed to add employee");
        }
    })
    .catch(error => {
        alert("Error: " + error.message);
        console.error("Error:", error);
    });
}); 
function handleResponse(response) {
  if (!response.ok) throw new Error('Network error');
  return response.json().then(data => {
    if (data.status !== "success") throw new Error(data.message);
    return data;
  });
}

function handleError(error) {
  console.error("Error:", error);
  alert(`❌ Error: ${error.message}`);
}

function resetForm() {
  document.getElementById("employeeForm").reset();
  document.getElementById("role").value = "";
  document.getElementById("email").value = "";
  document.getElementById("password").value = "";
  document.querySelector('input[name="idOption"][value="auto"]').checked = true;
  document.getElementById("employeeId").style.display = "none";
}





///////////////////////////////////////////////
