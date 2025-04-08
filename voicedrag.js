document.addEventListener("DOMContentLoaded", () => {
    const roles = document.querySelectorAll(".role");
    const dropZones = document.querySelectorAll(".drop-zone");
    const calendar = document.getElementById("calendar");
    const prevWeekBtn = document.getElementById("prev-week"); // Select existing buttons
    const nextWeekBtn = document.getElementById("next-week");
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const dateHeaders = document.querySelectorAll("thead th:nth-child(n+2)");

    // Function to get Monday of a given week
    function getMonday(d) {
        d = new Date(d);
        let day = d.getDay();
        let diff = d.getDate() - day + (day === 0 ? -6 : 1);
        return new Date(d.setDate(diff));
    }

    // Function to update week display
    function updateWeek(startDate) {
        let currentDate = getMonday(startDate);

        dateHeaders.forEach((th, index) => {
            let newDate = new Date(currentDate);
            newDate.setDate(newDate.getDate() + index);

            // Ensure Sunday is skipped
            if (newDate.getDay() === 0) {
                newDate.setDate(newDate.getDate() + 1);
            }

            th.innerHTML = `<div class='day-header'>${days[index]}<br><span class='date'>${newDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span></div>`;
        });

        // Update calendar input to match the first date
        calendar.valueAsDate = getMonday(startDate);
    }

    // Calendar date change event
    calendar.addEventListener("change", (e) => {
        updateWeek(new Date(e.target.value));
    });

    // Next week button event
    nextWeekBtn.addEventListener("click", () => {
        let currentDisplayedDate = new Date(dateHeaders[0].querySelector(".date").textContent.trim().replace(/,/g, ""));
        currentDisplayedDate.setDate(currentDisplayedDate.getDate() + 7);

        // Skip Sunday
        if (currentDisplayedDate.getDay() === 0) {
            currentDisplayedDate.setDate(currentDisplayedDate.getDate() + 1);
        }

        updateWeek(currentDisplayedDate);
    });

    // Previous week button event
    prevWeekBtn.addEventListener("click", () => {
        let currentDisplayedDate = new Date(dateHeaders[0].querySelector(".date").textContent.trim().replace(/,/g, ""));
        currentDisplayedDate.setDate(currentDisplayedDate.getDate() - 7);

        // Skip Sunday
        if (currentDisplayedDate.getDay() === 0) {
            currentDisplayedDate.setDate(currentDisplayedDate.getDate() - 1);
        }

        updateWeek(currentDisplayedDate);
    });

    // Drag and drop functionality
    roles.forEach(role => {
        role.addEventListener("dragstart", (e) => {
            e.dataTransfer.setData("text", e.target.id);
            e.target.classList.add("dragging");
        });

        role.addEventListener("dragend", (e) => {
            e.target.classList.remove("dragging");
        });
    });

    dropZones.forEach(zone => {
        zone.addEventListener("dragover", (e) => {
            e.preventDefault();
            zone.classList.add("drop-hover");
        });

        zone.addEventListener("dragleave", () => {
            zone.classList.remove("drop-hover");
        });

        zone.addEventListener("drop", (e) => {
            e.preventDefault();
            const roleId = e.dataTransfer.getData("text");
            const role = document.getElementById(roleId);

            // Prevent adding multiple roles to the same drop zone
            if (zone.children.length === 0) {
                zone.appendChild(role);
            }

            zone.classList.remove("drop-hover");
        });
    });

    // Initialize with current week's dates
    updateWeek(new Date());
});



document.addEventListener("DOMContentLoaded", function () {
    let scheduleData = JSON.parse(localStorage.getItem("schedule")) || {}; // Load saved schedule

    const roles = document.querySelectorAll(".role");
    const dropZones = document.querySelectorAll(".drop-zone");
    const calendar = document.getElementById("calendar");
    const saveButton = document.getElementById("save-schedule"); // Use existing button

    let selectedDate = ""; 

    // Update selected date
    calendar.addEventListener("change", function () {
        selectedDate = this.value;
        loadSchedule(selectedDate);
    });

    // Drag events
    roles.forEach(role => {
        role.addEventListener("dragstart", function (event) {
            event.dataTransfer.setData("text/plain", event.target.id);
        });
    });

    dropZones.forEach(zone => {
        zone.addEventListener("dragover", function (event) {
            event.preventDefault();
        });

        zone.addEventListener("drop", function (event) {
            event.preventDefault();
            const roleId = event.dataTransfer.getData("text/plain");
            const roleElement = document.getElementById(roleId);
            this.innerHTML = ""; // Clear previous content
            this.appendChild(roleElement.cloneNode(true)); // Move role
            storeAssignment(selectedDate, this.id, roleId);
        });
    });

    // Store assignment dynamically
    function storeAssignment(date, shiftId, role) {
        if (!date) {
            alert("Please select a date first!");
            return;
        }
        if (!scheduleData[date]) {
            scheduleData[date] = {};
        }
        scheduleData[date][shiftId] = role;
    }

    // Save schedule to localStorage
    document.getElementById("load-schedule").addEventListener("click", function () {
        const selectedDate = document.getElementById("calendar").value; // Get the selected date
    
        if (!selectedDate) {
            alert("Please select a date first!");
            return;
        }
    
        fetch(`http://127.0.0.1:5000/get_schedule/${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                console.log("📤 Fetched Schedule:", data); // Debugging: Show received data in the console
    
                // Update the UI (Example: Display data in drop zones)
                Object.keys(data).forEach(shiftId => {
                    const dropZone = document.getElementById(shiftId);
                    if (dropZone) {
                        dropZone.innerHTML = `<div class="role">${data[shiftId]}</div>`; // Assign role
                    }
                });
            })
            .catch(error => console.error("❌ Error Fetching Schedule:", error));
    });
    
    // Load saved schedule
    function loadSchedule(date) {
        dropZones.forEach(zone => {
            zone.innerHTML = "Drag & Drop";
        });

        if (scheduleData[date]) {
            for (const [shiftId, roleId] of Object.entries(scheduleData[date])) {
                const dropZone = document.getElementById(shiftId);
                if (dropZone) {
                    const roleElement = document.getElementById(roleId);
                    if (roleElement) {
                        dropZone.innerHTML = "";
                        dropZone.appendChild(roleElement.cloneNode(true));
                    }
                }
            }
        }
    }


});









//////////////////////////////////////////////
/// Worker Assignment Functionality
document.querySelectorAll('.worker-role-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
        const role = this.getAttribute('data-worker-role');
        await fetchWorkersByRole(role);
    });
});

async function fetchWorkersByRole(role) {
    try {
        // Show loading state
        const workerList = document.getElementById('worker-data-list');
        workerList.innerHTML = '<tr><td colspan="4" class="loading-workers">Loading workers...</td></tr>';
        
        // Replace with your actual API endpoint
        const response = await fetch(`/api/workers?role=${encodeURIComponent(role)}`);
        const workers = await response.json();
        
        displayWorkers(workers);
    } catch (error) {
        console.error('Error fetching workers:', error);
        // Fallback to mock data
        displayWorkers(generateMockWorkers(role));
    }
}

function displayWorkers(workers) {
    const tbody = document.getElementById('worker-data-list');
    tbody.innerHTML = '';
    
    if (workers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="no-workers">No workers found for this role</td></tr>';
        return;
    }
    
    workers.forEach(worker => {
        const tr = document.createElement('tr');
        tr.setAttribute('draggable', 'true');
        tr.setAttribute('data-worker-id', worker.id);
        tr.classList.add('worker-row');
        
        tr.innerHTML = `
            <td class="worker-id">${worker.id}</td>
            <td class="worker-name">${worker.name}</td>
            <td class="worker-role">${worker.role}</td>
            <td class="worker-contact">${worker.contact}</td>
        `;
        
        // Add drag events
        tr.addEventListener('dragstart', handleWorkerDragStart);
        tr.addEventListener('dragend', handleWorkerDragEnd);
        
        tbody.appendChild(tr);
    });
}

// Worker Drag and Drop Handlers
function handleWorkerDragStart(e) {
    this.classList.add('worker-dragging');
    e.dataTransfer.setData('text/plain', this.getAttribute('data-worker-id'));
    e.dataTransfer.effectAllowed = 'move';
}

function handleWorkerDragEnd() {
    this.classList.remove('worker-dragging');
}

// Update existing drop zones to accept workers
document.querySelectorAll('.drop-zone').forEach(zone => {
    zone.addEventListener('dragover', function(e) {
        if (e.dataTransfer.types.includes('text/plain')) {
            e.preventDefault();
            this.classList.add('worker-drop-active');
            e.dataTransfer.dropEffect = 'move';
        }
    });
    
    zone.addEventListener('dragleave', function() {
        this.classList.remove('worker-drop-active');
    });
    
    zone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('worker-drop-active');
        
        const workerId = e.dataTransfer.getData('text/plain');
        const workerRow = document.querySelector(`tr[data-worker-id="${workerId}"]`);
        
        if (workerRow) {
            const workerName = workerRow.querySelector('.worker-name').textContent;
            const workerRole = workerRow.querySelector('.worker-role').textContent;
            
            // Check if worker is already assigned
            if (this.querySelector(`.assigned-worker[data-worker-id="${workerId}"]`)) {
                return;
            }
            
            // Create assigned worker element
            const assignedWorker = document.createElement('div');
            assignedWorker.className = 'assigned-worker';
            assignedWorker.setAttribute('data-worker-id', workerId);
            assignedWorker.innerHTML = `
                ${workerName} (${workerRole})
                <span class="remove-worker" title="Remove">×</span>
            `;
            
            // Add remove functionality
            assignedWorker.querySelector('.remove-worker').addEventListener('click', function() {
                this.parentElement.remove();
            });
            
            this.appendChild(assignedWorker);
        }
    });
});

// Mock data generator
function generateMockWorkers(role) {
    const roleWorkers = {
        'Site Supervisor / Foreman': [
            { id: 'WF1001', name: 'John Smith', contact: '555-7890' },
            { id: 'WF1002', name: 'Robert Johnson', contact: '555-7891' }
        ],
        'General Laborer': [
            { id: 'WL2001', name: 'Mike Brown', contact: '555-1234' },
            { id: 'WL2002', name: 'David Wilson', contact: '555-1235' },
            { id: 'WL2003', name: 'James Davis', contact: '555-1236' }
        ],
        // Add mock data for other roles...
    };

    return roleWorkers[role] || [
        {
            id: `W${Math.floor(1000 + Math.random() * 9000)}`,
            name: 'Sample Worker',
            contact: `555-${Math.floor(1000 + Math.random() * 9000)}`,
            role: role
        }
    ];
}