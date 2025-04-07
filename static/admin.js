const sectionLinks = document.querySelectorAll(".nav-link");
const sections = document.querySelectorAll(".section");

// Modal Handling
function openModal() {
  document.getElementById("employeeModal").style.display = "flex";
}
function closeModal() {
  document.getElementById("employeeModal").style.display = "none";
}

window.onload = function () {
  document.getElementById("employeeModal").style.display = "none"; // Always hide modal on reload
};

// Section Switching
function showSection(id) {
  sections.forEach((section) => {
    section.classList.remove("active");
  });
  document.getElementById(id).classList.add("active");

  sectionLinks.forEach((link) => {
    link.classList.remove("active");
  });
  const clickedLink = Array.from(sectionLinks).find((link) =>
    link.getAttribute("onclick").includes(id)
  );
  if (clickedLink) clickedLink.classList.add("active");
}

// Role-based Email/Password Generator
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
  "Security Guard": "securityguard",
};

document.getElementById("role").addEventListener("change", function () {
  const selectedRole = this.value;
  const roleId = roleMap[selectedRole];

  if (roleId) {
    // Simulating count from DB using localStorage
    let currentCount = localStorage.getItem(roleId);
    currentCount = currentCount ? parseInt(currentCount) + 1 : 1;
    localStorage.setItem(roleId, currentCount);

    const formattedNumber = currentCount.toString().padStart(2, "0");
    const email = `25${roleId}${formattedNumber}@gmail.com`;
    const password = `${roleId}${formattedNumber}`;

    document.getElementById("email").value = email;
    document.getElementById("password").value = password;
  } else {
    document.getElementById("email").value = "";
    document.getElementById("password").value = "";
  }
});
