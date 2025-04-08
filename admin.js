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
    const response = await fetch('get_employees.php');
    const data = await response.json();
    
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
          <button onclick="editEmployee('${employee.employee_id}')">Edit</button>
          <button onclick="deleteEmployee('${employee.employee_id}')">Delete</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
    
    document.getElementById('total-employees').textContent = data.length;
  } catch (error) {
    console.error('Error loading employees:', error);
  }
}

// Email Generation
document.getElementById('role').addEventListener('change', async function() {
  const role = this.value;
  if (!role) return;
  
  try {
    const response = await fetch(`generate_email.php?role=${encodeURIComponent(role)}`);
    const data = await response.json();
    
    if (data.status === 'success') {
      document.getElementById('email').value = data.email;
      document.getElementById('password').value = data.password;
    } else {
      throw new Error(data.message || 'Failed to generate credentials');
    }
  } catch (error) {
    console.error('Error generating email:', error);
    alert('Error generating credentials: ' + error.message);
  }
});

// Form Submission
document.getElementById('employeeForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const formData = {
    name: document.getElementById('name').value,
    gender: document.getElementById('gender').value,
    department: document.getElementById('department').value,
    role: document.getElementById('role').value,
    email: document.getElementById('email').value,
    password: document.getElementById('password').value
  };
  
  try {
    const response = await fetch('add_employee.php', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    const data = await response.json();
    
    if (data.status === 'success') {
      alert('Employee added successfully!');
      closeModal();
      loadEmployees();
    } else {
      throw new Error(data.message || 'Failed to add employee');
    }
  } catch (error) {
    console.error('Error adding employee:', error);
    alert('Error: ' + error.message);
  }
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
  loadEmployees();
});