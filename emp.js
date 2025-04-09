document.addEventListener('DOMContentLoaded', function() {
    // Toggle between sections
    const navItems = document.querySelectorAll('.nav-menu li a');
    const contentSections = document.querySelectorAll('.content-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all nav items and sections
            navItems.forEach(navItem => {
                navItem.parentElement.classList.remove('active');
            });
            
            contentSections.forEach(section => {
                section.classList.remove('active-section');
            });
            
            // Add active class to clicked nav item
            this.parentElement.classList.add('active');
            
            // Show corresponding section
            const targetSection = this.getAttribute('href').substring(1);
            document.getElementById(targetSection).classList.add('active-section');
        });
    });

    // Profile dropdown functionality
    const profileDropdown = document.querySelector('.profile-dropdown');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    
    profileDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function() {
        dropdownMenu.style.display = 'none';
    });

    // Modal functionality
    const viewFullProfileBtn = document.getElementById('viewFullProfileBtn');
    const fullProfileModal = document.getElementById('fullProfileModal');
    const closeModal = document.querySelector('.close');
    
    viewFullProfileBtn.addEventListener('click', function() {
        fullProfileModal.style.display = 'block';
    });
    
    closeModal.addEventListener('click', function() {
        fullProfileModal.style.display = 'none';
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === fullProfileModal) {
            fullProfileModal.style.display = 'none';
        }
    });

    // Edit profile button
    const editProfileBtn = document.getElementById('editProfileBtn');
    
    editProfileBtn.addEventListener('click', function() {
        const inputs = document.querySelectorAll('.profile-details input');
        inputs.forEach(input => {
            input.removeAttribute('readonly');
            input.style.backgroundColor = 'white';
            input.style.borderColor = '#ddd';
        });
        
        this.innerHTML = '<i class="fas fa-save"></i> Save Changes';
        this.removeEventListener('click', arguments.callee);
        
        this.addEventListener('click', function() {
            inputs.forEach(input => {
                input.setAttribute('readonly', 'true');
                input.style.backgroundColor = '#F5F7FA';
                input.style.borderColor = 'transparent';
            });
            
            this.innerHTML = '<i class="fas fa-edit"></i> Edit Profile';
            fullProfileModal.style.display = 'none';
            
            // Show success message
            alert('Profile updated successfully!');
        });
    });

    // Initialize charts
    initializeCharts();
    
    // Sample attendance data
    populateAttendanceTable();
    
    // Sample leave history data
    populateLeaveHistory();
});

function initializeCharts() {
    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart').getContext('2d');
    const performanceChart = new Chart(performanceCtx, {
        type: 'bar',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
                label: 'Performance Score',
                data: [3.8, 4.2, 4.5, 4.1],
                backgroundColor: '#2E4E7E',
                borderColor: '#1E3E6E',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 3,
                    max: 5,
                    ticks: {
                        stepSize: 0.5
                    }
                }
            }
        }
    });

    // Attendance Chart
    const attendanceCtx = document.getElementById('attendanceChart').getContext('2d');
    const attendanceChart = new Chart(attendanceCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Present Days',
                data: [22, 20, 23, 21, 22, 22],
                backgroundColor: 'rgba(0, 180, 166, 0.1)',
                borderColor: '#00B4A6',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    min: 15,
                    max: 25
                }
            }
        }
    });

    // Quarterly Performance Chart
    const quarterlyCtx = document.getElementById('quarterlyPerformanceChart').getContext('2d');
    const quarterlyChart = new Chart(quarterlyCtx, {
        type: 'radar',
        data: {
            labels: ['Quality', 'Productivity', 'Teamwork', 'Initiative', 'Safety', 'Punctuality'],
            datasets: [{
                label: 'Current Quarter',
                data: [4.5, 4.3, 4.0, 4.1, 4.7, 4.2],
                backgroundColor: 'rgba(46, 78, 126, 0.2)',
                borderColor: '#2E4E7E',
                borderWidth: 2,
                pointBackgroundColor: '#2E4E7E'
            }, {
                label: 'Previous Quarter',
                data: [4.2, 4.0, 3.8, 3.9, 4.5, 4.0],
                backgroundColor: 'rgba(0, 180, 166, 0.2)',
                borderColor: '#00B4A6',
                borderWidth: 2,
                pointBackgroundColor: '#00B4A6'
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    angleLines: {
                        display: true
                    },
                    suggestedMin: 3,
                    suggestedMax: 5
                }
            }
        }
    });

    // Goals Chart
    const goalsCtx = document.getElementById('goalsChart').getContext('2d');
    const goalsChart = new Chart(goalsCtx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'In Progress', 'Not Started'],
            datasets: [{
                data: [65, 25, 10],
                backgroundColor: [
                    '#00B4A6',
                    '#2E4E7E',
                    '#F5F7FA'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function populateAttendanceTable() {
    const tableBody = document.querySelector('.attendance-table tbody');
    const attendanceData = [
        { date: 'Mon, Jun 5', checkIn: '06:58 AM', checkOut: '04:02 PM', hours: '9.1', overtime: '1.1', late: '0', status: 'present' },
        { date: 'Tue, Jun 6', checkIn: '07:15 AM', checkOut: '03:45 PM', hours: '8.5', overtime: '0.5', late: '15', status: 'present' },
        { date: 'Wed, Jun 7', checkIn: '06:45 AM', checkOut: '04:15 PM', hours: '9.5', overtime: '1.5', late: '0', status: 'present' },
        { date: 'Thu, Jun 8', checkIn: '-', checkOut: '-', hours: '-', overtime: '-', late: '-', status: 'absent' },
        { date: 'Fri, Jun 9', checkIn: '07:05 AM', checkOut: '03:55 PM', hours: '8.8', overtime: '0.8', late: '5', status: 'present' },
        { date: 'Sat, Jun 10', checkIn: '07:00 AM', checkOut: '12:00 PM', hours: '5.0', overtime: '0', late: '0', status: 'present' },
        { date: 'Mon, Jun 12', checkIn: '06:50 AM', checkOut: '04:10 PM', hours: '9.3', overtime: '1.3', late: '0', status: 'present' },
        { date: 'Tue, Jun 13', checkIn: '07:20 AM', checkOut: '03:40 PM', hours: '8.3', overtime: '0.3', late: '20', status: 'present' },
        { date: 'Wed, Jun 14', checkIn: '06:55 AM', checkOut: '04:05 PM', hours: '9.2', overtime: '1.2', late: '0', status: 'present' }
    ];

    attendanceData.forEach(record => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${record.date}</td>
            <td>${record.checkIn}</td>
            <td>${record.checkOut}</td>
            <td>${record.hours} hrs</td>
            <td>${record.overtime} hrs</td>
            <td>${record.late}</td>
            <td><span class="status ${record.status}">${record.status.charAt(0).toUpperCase() + record.status.slice(1)}</span></td>
        `;
        
        tableBody.appendChild(row);
    });
}

function populateLeaveHistory() {
    const tableBody = document.querySelector('.leave-history-table tbody');
    const leaveData = [
        { type: 'Annual', dates: 'Jun 1-5, 2023', duration: '5 days', status: 'approved' },
        { type: 'Sick', dates: 'Apr 15, 2023', duration: '1 day', status: 'approved' },
        { type: 'Personal', dates: 'Mar 10, 2023', duration: '1 day', status: 'approved' },
        { type: 'Annual', dates: 'Jul 20-25, 2023', duration: '5 days', status: 'pending' },
        { type: 'Parental', dates: 'Sep 1-30, 2023', duration: '30 days', status: 'planned' }
    ];

    leaveData.forEach(leave => {
        const row = document.createElement('tr');
        
        let statusClass = '';
        let statusText = '';
        
        switch(leave.status) {
            case 'approved':
                statusClass = 'success';
                statusText = 'Approved';
                break;
            case 'pending':
                statusClass = 'warning';
                statusText = 'Pending';
                break;
            case 'planned':
                statusClass = 'info';
                statusText = 'Planned';
                break;
            case 'rejected':
                statusClass = 'danger';
                statusText = 'Rejected';
                break;
        }
        
        row.innerHTML = `
            <td>${leave.type} Leave</td>
            <td>${leave.dates}</td>
            <td>${leave.duration}</td>
            <td><span class="status ${statusClass}">${statusText}</span></td>
            <td>
                <button class="btn small"><i class="fas fa-eye"></i></button>
                ${leave.status === 'pending' ? '<button class="btn small danger"><i class="fas fa-times"></i></button>' : ''}
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}
document.addEventListener("DOMContentLoaded", function () {
    // Fetch user ID from session or hidden input
    fetch("check_first_login.php")
      .then(response => response.json())
      .then(data => {
        if (data.first_login === true) {
          document.getElementById("firstLoginModal").style.display = "block";
          document.getElementById("emp_id").value = data.emp_id;
        }
      });
  
    document.getElementById("firstLoginForm").addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);
  
      fetch("update_profile.php", {
        method: "POST",
        body: formData
      })
        .then(res => res.text())
        .then(response => {
          alert(response);
          document.getElementById("firstLoginModal").style.display = "none";
        });
    });
  });
  