document.addEventListener("DOMContentLoaded", () => {
    // Calendar and Schedule Functionality
    const roles = document.querySelectorAll(".role");
    const dropZones = document.querySelectorAll(".drop-zone");
    const calendar = document.getElementById("calendar");
    const prevWeekBtn = document.getElementById("prev-week");
    const nextWeekBtn = document.getElementById("next-week");
    const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const dateHeaders = document.querySelectorAll("thead th:nth-child(n+2)");
    let scheduleData = JSON.parse(localStorage.getItem("schedule")) || {};
    let selectedDate = "";

    // Initialize calendar
    function getMonday(d) {
        d = new Date(d);
        let day = d.getDay();
        let diff = d.getDate() - day + (day === 0 ? -6 : 1);
        return new Date(d.setDate(diff));
    }

    function updateWeek(startDate) {
        let currentDate = getMonday(startDate);
        dateHeaders.forEach((th, index) => {
            let newDate = new Date(currentDate);
            newDate.setDate(newDate.getDate() + index);
            if (newDate.getDay() === 0) {
                newDate.setDate(newDate.getDate() + 1);
            }
            th.innerHTML = `${days[index]}<br><span class="date">${newDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>`;
        });
        calendar.valueAsDate = getMonday(startDate);
        selectedDate = calendar.value;
        loadSchedule(selectedDate);
    }

    calendar.addEventListener("change", (e) => {
        updateWeek(new Date(e.target.value));
    });

    nextWeekBtn.addEventListener("click", () => {
        let currentDisplayedDate = new Date(dateHeaders[0].querySelector(".date").textContent.trim().replace(/,/g, ""));
        currentDisplayedDate.setDate(currentDisplayedDate.getDate() + 7);
        updateWeek(currentDisplayedDate);
    });

    prevWeekBtn.addEventListener("click", () => {
        let currentDisplayedDate = new Date(dateHeaders[0].querySelector(".date").textContent.trim().replace(/,/g, ""));
        currentDisplayedDate.setDate(currentDisplayedDate.getDate() - 7);
        updateWeek(currentDisplayedDate);
    });

    // Drag and drop functionality
    document.addEventListener("dragstart", (e) => {
        if (e.target.classList.contains("role")) {
            e.dataTransfer.setData("text/plain", e.target.id);
            e.target.classList.add("dragging");
            document.body.classList.add("dragging-active");
        }
    });

    document.addEventListener("dragend", (e) => {
        if (e.target.classList.contains("role")) {
            e.target.classList.remove("dragging");
            document.body.classList.remove("dragging-active");
        }
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
            zone.classList.remove("drop-hover");
            
            const roleId = e.dataTransfer.getData("text/plain");
            const role = document.getElementById(roleId);
            if (!role) return;
            
            // Clear existing content
            while (zone.firstChild) {
                zone.removeChild(zone.firstChild);
            }
            
            // Create and append clone
            const clone = role.cloneNode(true);
            clone.classList.remove("dragging");
            zone.appendChild(clone);
            
            storeAssignment(selectedDate, zone.id, roleId);
        });
    });

    function storeAssignment(date, shiftId, roleId) {
        if (!date) return;
        if (!scheduleData[date]) scheduleData[date] = {};
        scheduleData[date][shiftId] = roleId;
        localStorage.setItem("schedule", JSON.stringify(scheduleData));
    }

    function loadSchedule(date) {
        if (!date) return;
        
        dropZones.forEach(zone => {
            // Reset to default text
            if (zone.children.length === 0) {
                zone.textContent = zone.id.includes("session1") ? "Shift 1: 9:00 AM - 12:00 PM" :
                                  zone.id.includes("session2") ? "Shift 2: 1:00 PM - 6:00 PM" :
                                  "Shift 3: 6:00 PM - 11:30 PM";
            }
        });
        
        if (scheduleData[date]) {
            for (const [shiftId, roleId] of Object.entries(scheduleData[date])) {
                const dropZone = document.getElementById(shiftId);
                const roleElement = document.getElementById(roleId);
                
                if (dropZone && roleElement) {
                    dropZone.innerHTML = "";
                    const clone = roleElement.cloneNode(true);
                    clone.classList.remove("dragging");
                    dropZone.appendChild(clone);
                }
            }
        }
    }

    // Save/Load functionality
    document.getElementById("save-schedule").addEventListener("click", () => {
        localStorage.setItem("schedule", JSON.stringify(scheduleData));
        alert("Schedule saved successfully!");
    });

    document.getElementById("load-schedule").addEventListener("click", () => {
        const loadedData = localStorage.getItem("schedule");
        if (loadedData) {
            scheduleData = JSON.parse(loadedData);
            loadSchedule(selectedDate);
            alert("Schedule loaded successfully!");
        } else {
            alert("No saved schedule found!");
        }
    });

    // Add Role functionality
    const addRoleBtn = document.getElementById("add-role-btn");
    const newRoleInput = document.getElementById("new-role-input");
    const rolesContainer = document.querySelector(".roles-container");

    addRoleBtn.addEventListener("click", addNewRole);
    newRoleInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") addNewRole();
    });

    function addNewRole() {
        const roleName = newRoleInput.value.trim();
        if (!roleName) return;
        
        const roleCount = document.querySelectorAll(".role").length;
        const newRole = document.createElement("div");
        newRole.className = "role";
        newRole.draggable = true;
        newRole.id = `role${roleCount + 1}`;
        newRole.textContent = roleName.toUpperCase();
        
        newRole.addEventListener("dragstart", function(e) {
            e.dataTransfer.setData("text/plain", e.target.id);
            e.target.classList.add("dragging");
            document.body.classList.add("dragging-active");
        });
        
        newRole.addEventListener("dragend", function() {
            this.classList.remove("dragging");
            document.body.classList.remove("dragging-active");
        });
        
        rolesContainer.appendChild(newRole);
        newRoleInput.value = "";
    }

    // Worker Management Section
    const roleDropdown = document.getElementById("role-dropdown");
    const fetchBtn = document.getElementById("fetch-workers");

    fetchBtn.addEventListener("click", fetchWorkersByRole);

    async function fetchWorkersByRole() {
        const role = roleDropdown.value;
        if (!role) {
            alert("Please select a role first");
            return;
        }
    
        const workerList = document.getElementById("worker-data-list");
        workerList.innerHTML = '<div class="loading-workers">Loading workers...</div>';
    
        try {
            const response = await fetch(`get_workers.php?role=${encodeURIComponent(role)}`);
            if (!response.ok) throw new Error('Network response was not ok');
            
            const workers = await response.json();
            displayWorkers(workers);
        } catch (error) {
            console.error('Error:', error);
            workerList.innerHTML = '<div class="error">Failed to load workers. Please try again.</div>';
        }
    }
    
    function displayWorkers(workers) {
        const workerList = document.getElementById("worker-data-list");
        workerList.innerHTML = '';
    
        if (!workers || workers.length === 0) {
            workerList.innerHTML = '<div class="no-workers">No workers found for this role</div>';
            return;
        }
    
        workers.forEach(worker => {
            const workerDiv = document.createElement("div");
            workerDiv.className = "worker-bar";
            workerDiv.setAttribute("draggable", "true");
            workerDiv.setAttribute("data-worker-id", worker.employee_id);
            
            const joinDate = new Date(worker.created_at);
            const formattedDate = joinDate.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
            
            workerDiv.innerHTML = `
                <div class="worker-id">${worker.employee_id || 'N/A'}</div>
                <div class="worker-name">${worker.name || 'N/A'}</div>
                <div class="worker-role">${worker.role || 'N/A'}</div>
                <div class="worker-email">${worker.email || 'N/A'}</div>
                <div class="worker-join-date">${formattedDate}</div>
            `;
    
            workerDiv.addEventListener("dragstart", handleWorkerDragStart);
            workerDiv.addEventListener("dragend", handleWorkerDragEnd);
            
            workerList.appendChild(workerDiv);
        });
    }

    function handleWorkerDragStart(e) {
        this.classList.add("worker-dragging");
        e.dataTransfer.setData("text/plain", this.getAttribute("data-worker-id"));
    }

    function handleWorkerDragEnd() {
        this.classList.remove("worker-dragging");
    }

    // Initialize with current week
    updateWeek(new Date());
});
