// Employee data storage
let employees = [];

// Section Management
function showSection(id) {
  document.querySelectorAll('.section').forEach(section => {
    section.classList.remove('active');
  });
  document.getElementById(id).classList.add('active');
  
  if (id === 'employees') {
    loadEmployees();
  }
}

// Modal Handling
function openModal() {
  document.getElementById('employeeModal').style.display = 'flex';
  document.getElementById('employeeForm').reset();
  document.getElementById('department').value = 'Construction';
  document.getElementById('email').value = '';
  document.getElementById('password').value = '';
}

function closeModal() {
  document.getElementById('employeeModal').style.display = 'none';
}

// Load Employees
async function loadEmployees() {
  try {
    const response = await fetch('get_employee.php');
    employees = await response.json();
    renderEmployeeTable(employees);
    document.getElementById('total-employees').textContent = employees.length;
    
    // Initialize filter button only once
    if (!document.querySelector('.filter-container')) {
      addFilterButton();
    }
  } catch (error) {
    console.error('Error loading employees:', error);
    alert('Failed to load employees');
  }
}

// Render Employee Table
function renderEmployeeTable(data) {
  const tableBody = document.getElementById('employee-table-body');
  tableBody.innerHTML = '';
  
  data.forEach(employee => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${employee.employee_id}</td>
      <td>${employee.name}</td>
      <td>${employee.department}</td>
      <td>${employee.role}</td>
      <td>${employee.email}</td>
      <td>${employee.join_date}</td>
      <td>
        <button onclick="editEmployee('${employee.employee_id}')" class="action-btn edit-btn">
          <i class="fas fa-edit"></i>
        </button>
        <button onclick="deleteEmployee('${employee.employee_id}')" class="action-btn delete-btn">
          <i class="fas fa-trash"></i>
        </button>
      </td>
    `;
    tableBody.appendChild(row);
  });
}

// Add Filter Button
function addFilterButton() {
  const sectionHeader = document.querySelector('#employees .section-header');
  
  const filterContainer = document.createElement('div');
  filterContainer.className = 'filter-container';
  
  const filterBtn = document.createElement('button');
  filterBtn.className = 'btn filter-btn';
  filterBtn.innerHTML = '<i class="fas fa-filter"></i> Filter by Role';
  
  const filterDropdown = document.createElement('div');
  filterDropdown.className = 'filter-dropdown';
  filterDropdown.style.display = 'none';
  
  // Add "All Roles" option
  const allRolesOption = document.createElement('a');
  allRolesOption.href = '#';
  allRolesOption.textContent = 'All Roles';
  allRolesOption.onclick = (e) => {
    e.preventDefault();
    renderEmployeeTable(employees);
    filterDropdown.style.display = 'none';
  };
  filterDropdown.appendChild(allRolesOption);
  
  // Get unique roles
  const uniqueRoles = [...new Set(employees.map(emp => emp.role))].sort();
  
  uniqueRoles.forEach(role => {
    const roleOption = document.createElement('a');
    roleOption.href = '#';
    roleOption.textContent = role;
    roleOption.onclick = (e) => {
      e.preventDefault();
      const filtered = employees.filter(emp => emp.role === role);
      renderEmployeeTable(filtered);
      filterDropdown.style.display = 'none';
    };
    filterDropdown.appendChild(roleOption);
  });
  
  filterBtn.onclick = (e) => {
    e.stopPropagation();
    filterDropdown.style.display = filterDropdown.style.display === 'none' ? 'block' : 'none';
  };
  
  filterContainer.appendChild(filterBtn);
  filterContainer.appendChild(filterDropdown);
  sectionHeader.appendChild(filterContainer);
}

// Email Generation
document.getElementById('role').addEventListener('change', async function() {
  const role = this.value;
  if (!role) return;
  
  try {
    const response = await fetch(`generate_email.php?role=${encodeURIComponent(role)}`);
    const data = await response.json();
    
    if (data.status === "success") {
      document.getElementById("email").value = data.email;
      document.getElementById("password").value = data.password;
      document.getElementById("employeeForm").dataset.nextNum = data.next_num;
    } else {
      throw new Error(data.message || 'Failed to generate credentials');
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Error generating credentials: " + error.message);
  }
});

// Form Submission
document.getElementById("employeeForm").addEventListener("submit", async function(e) {
  e.preventDefault();
  
  const formData = {
    name: document.getElementById("name").value,
    gender: document.getElementById("gender").value,
    department: document.getElementById("department").value,
    role: document.getElementById("role").value,
    email: document.getElementById("email").value,
    password: document.getElementById("password").value,
    next_num: this.dataset.nextNum
  };

  try {
    const response = await fetch("add_employee.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    
    const data = await response.json();
    
    if (data.status === "success") {
      alert(`Employee added successfully!\nID: ${data.employee_id}\nEmail: ${data.email}`);
      closeModal();
      loadEmployees();
    } else {
      throw new Error(data.message || "Failed to add employee");
    }
  } catch (error) {
    alert("Error: " + error.message);
    console.error("Error:", error);
  }
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.filter-container')) {
      document.querySelectorAll('.filter-dropdown').forEach(dd => {
        dd.style.display = 'none';
      });
    }
  });
  
  loadEmployees();
});
// View Employee Function
function viewEmployee(id) {
  const employee = employees.find(emp => emp.employee_id === id);
  if (employee) {
      // Create modal HTML for viewing
      const modalContent = `
          <div class="view-modal">
              <h3>Employee Details</h3>
              <div class="employee-details">
                  <p><strong>ID:</strong> ${employee.employee_id}</p>
                  <p><strong>Name:</strong> ${employee.name}</p>
                  <p><strong>Role:</strong> ${employee.role}</p>
                  <p><strong>Department:</strong> ${employee.department}</p>
                  <p><strong>Email:</strong> ${employee.email}</p>
                  <p><strong>Join Date:</strong> ${employee.join_date}</p>
              </div>
              <button onclick="closeViewModal()" class="btn">Close</button>
          </div>
      `;
      
      // Show modal
      document.getElementById('viewModal').innerHTML = modalContent;
      document.getElementById('viewModal').style.display = 'flex';
  }
}

// Edit Employee Function
function editEmployee(id) {
  const employee = employees.find(emp => emp.employee_id === id);
  if (employee) {
      // Populate the edit form (you can reuse your add employee modal)
      document.getElementById('editEmployeeId').value = employee.employee_id;
      document.getElementById('editName').value = employee.name;
      document.getElementById('editGender').value = employee.gender;
      document.getElementById('editDepartment').value = employee.department;
      document.getElementById('editRole').value = employee.role;
      document.getElementById('editEmail').value = employee.email;
      
      // Show edit modal
      document.getElementById('editModal').style.display = 'flex';
  }
}

// Delete Employee Function
async function deleteEmployee(id) {
  if (confirm('Are you sure you want to delete this employee?')) {
      try {
          const response = await fetch('delete_employee.php', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/x-www-form-urlencoded',
              },
              body: `employee_id=${id}`
          });
          
          const data = await response.json();
          
          if (data.success) {
              alert('Employee deleted successfully');
              loadEmployees(); // Refresh the table
          } else {
              throw new Error(data.message || 'Failed to delete employee');
          }
      } catch (error) {
          console.error('Error:', error);
          alert('Error deleting employee: ' + error.message);
      }
  }
}

// Update your renderEmployeeTable function to include View button
function renderEmployeeTable(data) {
  const tableBody = document.getElementById('employee-table-body');
  tableBody.innerHTML = '';

  data.forEach(employee => {
      const row = document.createElement('tr');
      row.innerHTML = `
          <td>${employee.employee_id}</td>
          <td>${employee.name}</td>
          <td>${employee.department}</td>
          <td>${employee.role}</td>
          <td>${employee.email}</td>
          <td>${employee.join_date}</td>
          <td>
              <button onclick="viewEmployee('${employee.employee_id}')" class="action-btn view-btn">
                  <i class="fas fa-eye"></i>
              </button>
              <button onclick="editEmployee('${employee.employee_id}')" class="action-btn edit-btn">
                  <i class="fas fa-edit"></i>
              </button>
              <button onclick="deleteEmployee('${employee.employee_id}')" class="action-btn delete-btn">
                  <i class="fas fa-trash"></i>
              </button>
          </td>
      `;
      tableBody.appendChild(row);
  });
}

// Close modals functions
function closeViewModal() {
  document.getElementById('viewModal').style.display = 'none';
}

function closeEditModal() {
  document.getElementById('editModal').style.display = 'none';
}
// Edit Form Submission
document.getElementById("editEmployeeForm").addEventListener("submit", async function(e) {
  e.preventDefault();
  
  const formData = {
      employee_id: document.getElementById("editEmployeeId").value,
      name: document.getElementById("editName").value,
      gender: document.getElementById("editGender").value,
      department: document.getElementById("editDepartment").value,
      role: document.getElementById("editRole").value,
      email: document.getElementById("editEmail").value
  };

  try {
      const response = await fetch("update_employee.php", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      
      if (data.success) {
          alert(data.message);
          closeEditModal();
          loadEmployees(); // Refresh the table
      } else {
          throw new Error(data.message || "Failed to update employee");
      }
  } catch (error) {
      alert("Error: " + error.message);
      console.error("Error:", error);
  }
});