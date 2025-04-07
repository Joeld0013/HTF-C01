document.addEventListener('DOMContentLoaded', function() {
    // Navigation functionality
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = {
      dashboard: document.getElementById('dashboard-section'),
      employees: document.getElementById('employees-section'),
      profile: document.getElementById('profile-section')
    };
  
    // Set dashboard as default active section
    navLinks[0].classList.add('active');
    sections.dashboard.style.display = 'block';
  
    navLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Remove active class from all links
        navLinks.forEach(navLink => navLink.classList.remove('active'));
        
        // Add active class to clicked link
        this.classList.add('active');
        
        // Hide all sections
        Object.values(sections).forEach(section => {
          section.style.display = 'none';
        });
        
        // Show the selected section
        const sectionToShow = this.dataset.section;
        if (sections[sectionToShow]) {
          sections[sectionToShow].style.display = 'block';
        }
      });
    });
  
    // Employee Modal functionality
    const addEmployeeBtn = document.getElementById('addEmployeeBtn');
    const employeeModal = document.getElementById('employeeModal');
    const cancelEmployeeBtn = document.getElementById('cancelEmployee');
    const employeeForm = document.getElementById('employeeForm');
    const employeeRole = document.getElementById('employeeRole');
  
    // Initialize employee counter (in real app, fetch this from backend)
    let employeeCounter = localStorage.getItem('employeeCounter') || 1;
  
    // Generate employee email and password in 24mcabXX format
    function generateEmployeeDetails() {
      const counterStr = employeeCounter.toString().padStart(2, '0');
      const email = `24mcab${counterStr}@kristujayanti.com`;
      const password = `24mcab${counterStr}`;
      
      document.getElementById('employeeEmail').value = email;
      document.getElementById('employeePassword').value = password;
    }
  
    // Generate details when modal opens
    if (addEmployeeBtn) {
      addEmployeeBtn.addEventListener('click', function() {
        generateEmployeeDetails();
        employeeModal.classList.add('active');
      });
    }
  
    // Close modal
    function closeEmployeeModal() {
      employeeModal.classList.remove('active');
      employeeForm.reset();
    }
  
    if (cancelEmployeeBtn) {
      cancelEmployeeBtn.addEventListener('click', closeEmployeeModal);
    }
  
    document.querySelector('#employeeModal .close-modal').addEventListener('click', closeEmployeeModal);
  
    employeeModal.addEventListener('click', function(e) {
      if (e.target === this) {
        closeEmployeeModal();
      }
    });
  
    // Form submission
    if (employeeForm) {
      employeeForm.addEventListener('submit', function(e) {
        e.preventDefault();
    
        const employeeData = {
          email: document.getElementById('employeeEmail').value,
          password: document.getElementById('employeePassword').value,
          role: employeeRole.value
        };
    
        fetch('http://localhost:5000/api/employees', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(employeeData)
        })
        .then(response => response.json())
        .then(data => {
          alert(`✅ ${data.message}\n\nEmail: ${data.employee.email}\nPassword: ${data.employee.password}`);
          closeEmployeeModal();
          loadEmployees(); // refresh the table
        })
        .catch(error => {
          console.error('Error:', error);
          alert("❌ Failed to add employee. See console.");
        });
      });
    }
    
  
  function loadEmployees() {
    fetch('http://localhost:5000/api/employees')
      .then(response => response.json())
      .then(data => {
        const tableBody = document.querySelector('#employees-section tbody');
        tableBody.innerHTML = ''; // Clear old rows
  
        data.forEach((employee, index) => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${index + 1}</td>
            <td>${employee.email}</td>
            <td>${employee.role}</td>
            <td>${employee.status}</td>
            <td>${employee.joinDate}</td>
          `;
          tableBody.appendChild(row);
        });
      })
      .catch(error => console.error('Failed to load employees:', error));
  }
  
  
  
  // Inside navLinks.forEach(...)
  if (sectionToShow === 'employees') {
    loadEmployees(); // 🟦 Load employees only when that section is shown
  }
  
  
  
    // Role change event - now just validates selection
    employeeRole.addEventListener('change', function() {
      if (!this.value) {
        document.getElementById('employeeEmail').value = '';
        document.getElementById('employeePassword').value = '';
      }
    });
  });