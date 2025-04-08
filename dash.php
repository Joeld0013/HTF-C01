<?php
// Sample data
$df_employees = [
    [
        'employee_id' => 'E001',
        'name' => 'Anna Jensen',
        'department' => 'Finance',
        'join_date' => '2021-04-15',
        'months_employed' => 36,
        'base_salary' => 42000,
        'holiday_allowance' => 5250,
        'annual_leave_balance' => 15,
        'annual_leave_total' => 25,
        'parental_leave_balance' => 10,
        'parental_leave_total' => 32,
        'paternity_leave_balance' => 2,
        'paternity_leave_total' => 2,
        'bereavement_leave_balance' => 3,
        'bereavement_leave_total' => 3,
        'sick_leave_taken' => 2
    ]
];

$df_attendance = [
    ['employee_id' => 'E001', 'date' => '2024-04-05', 'check_in' => '08:00', 'check_out' => '16:30', 'overtime_hours' => 0.5, 'status' => 'Present'],
    ['employee_id' => 'E001', 'date' => '2024-04-04', 'check_in' => '08:10', 'check_out' => '17:00', 'overtime_hours' => 1.0, 'status' => 'Present'],
    ['employee_id' => 'E001', 'date' => '2024-04-03', 'check_in' => '08:05', 'check_out' => '16:40', 'overtime_hours' => 0.7, 'status' => 'Present'],
    ['employee_id' => 'E001', 'date' => '2024-04-02', 'check_in' => '08:15', 'check_out' => '16:30', 'overtime_hours' => 0.0, 'status' => 'Present'],
    ['employee_id' => 'E001', 'date' => '2024-04-01', 'check_in' => '08:00', 'check_out' => '16:45', 'overtime_hours' => 0.8, 'status' => 'Present']
];

$df_leaves = [
    ['employee_id' => 'E001', 'leave_type' => 'Annual Leave', 'start_date' => '2024-03-15', 'end_date' => '2024-03-18', 'duration' => 3, 'status' => 'Approved'],
    ['employee_id' => 'E001', 'leave_type' => 'Sick Leave', 'start_date' => '2024-02-10', 'end_date' => '2024-02-11', 'duration' => 2, 'status' => 'Approved']
];

// Weather data - using sample data for this example
$weather_data = [
    'current' => [
        'temp' => 18,
        'condition' => 'Partly Cloudy',
        'humidity' => 65,
        'wind_speed' => 12,
        'icon' => '⛅'
    ],
    'forecast' => [
        ['day' => 'Today', 'temp_high' => 18, 'temp_low' => 10, 'condition' => 'Partly Cloudy', 'icon' => '⛅'],
        ['day' => 'Tomorrow', 'temp_high' => 22, 'temp_low' => 12, 'condition' => 'Sunny', 'icon' => '☀️'],
        ['day' => 'Wednesday', 'temp_high' => 17, 'temp_low' => 9, 'condition' => 'Rain', 'icon' => '🌧️', 'warning' => 'Heavy Rain Warning']
    ]
];

// AI task recommendations
$ai_tasks = [
    ['priority' => 'High', 'task' => 'Complete Q2 financial report', 'deadline' => '2024-04-15', 'status' => 'Pending'],
    ['priority' => 'Medium', 'task' => 'Review department budget allocations', 'deadline' => '2024-04-20', 'status' => 'Pending'],
    ['priority' => 'Low', 'task' => 'Update expense tracking spreadsheet', 'deadline' => '2024-04-25', 'status' => 'Pending']
];

// Chart data
$months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
$performance_data = [84, 78, 82, 91, 85, 89];
$attendance_data = [95, 92, 98, 100, 96, 98];
$overtime_monthly = [12, 8, 10, 15, 16, 14];

// Leave balance data
$leave_types = ['Annual Leave', 'Parental Leave', 'Paternity Leave', 'Bereavement Leave'];
$leave_used = [10, 22, 0, 0];
$leave_remaining = [15, 10, 2, 3];

// Color palette
$colors = [
    'primary' => '#1f77b4',
    'secondary' => '#2ca02c',
    'accent' => '#ff7f0e',
    'background' => '#f9fafb',
    'card' => '#ffffff',
    'text' => '#2c3e50',
    'border' => '#e1e4e8',
    'warning' => '#e74c3c',
    'high' => '#e74c3c',
    'medium' => '#f39c12',
    'low' => '#3498db'
];

// Determine active tab
$active_tab = isset($_GET['tab']) ? $_GET['tab'] : 'overview';

// Handle generate tasks action
if (isset($_GET['action']) && $_GET['action'] == 'generate_tasks') {
    $new_priorities = ['High', 'Medium', 'Low'];
    $new_tasks = [
        'Prepare monthly expense report',
        'Schedule team meeting for budget review',
        'Update quarterly forecasts',
        'Create presentation for management meeting',
        'Review invoices for payment processing'
    ];
    
    $new_task = [
        'priority' => $new_priorities[array_rand($new_priorities)],
        'task' => $new_tasks[array_rand($new_tasks)],
        'deadline' => '2024-04-' . rand(15, 30),
        'status' => 'New'
    ];
    
    array_unshift($ai_tasks, $new_task);
    if (count($ai_tasks) > 5) {
        array_pop($ai_tasks);
    }
    
    // Redirect back to prevent form resubmission
    header("Location: ?tab=overview");
    exit;
}

// Function to render the current tab content
function renderTabContent($tab, $data) {
    extract($data); // Make all variables available
    
    if ($tab == 'overview') {
        return '
        <div class="card-row">
            <!-- Weather Widget -->
            <div class="card flex-1">
                <h4 class="card-title">Weather Report</h4>
                <div class="weather-main">
                    <div class="current-weather">
                        <span class="weather-icon">' . $weather_data['current']['icon'] . '</span>
                        <div>
                            <h3 class="temp">' . $weather_data['current']['temp'] . '°C</h3>
                            <p class="condition">' . $weather_data['current']['condition'] . '</p>
                        </div>
                    </div>
                    <div class="weather-details">
                        <p>Humidity: ' . $weather_data['current']['humidity'] . '%</p>
                        <p>Wind: ' . $weather_data['current']['wind_speed'] . ' km/h</p>
                    </div>
                </div>
                <div class="weather-forecast">';
                
                foreach ($weather_data['forecast'] as $day) {
                    echo '<div class="forecast-day">
                        <h5>' . $day['day'] . '</h5>
                        <span class="forecast-icon">' . $day['icon'] . '</span>
                        <p>' . $day['temp_high'] . '°/' . $day['temp_low'] . '°</p>';
                    
                    if (isset($day['warning'])) {
                        echo '<div><p class="weather-warning">' . $day['warning'] . '</p></div>';
                    }
                    
                    echo '</div>';
                }
                
                echo '
                </div>
            </div>
            
            <!-- AI Task Recommendations -->
            <div class="card flex-1">
                <h4 class="card-title">AI Task Recommendations</h4>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Priority</th>
                                <th>Task</th>
                                <th>Deadline</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>';
                        
                        foreach ($ai_tasks as $task) {
                            echo '<tr>
                                <td><span class="priority-badge ' . strtolower($task['priority']) . '">' . $task['priority'] . '</span></td>
                                <td>' . $task['task'] . '</td>
                                <td>' . $task['deadline'] . '</td>
                                <td><span class="status-badge pending">' . $task['status'] . '</span></td>
                            </tr>';
                        }
                        
                        echo '
                        </tbody>
                    </table>
                </div>
                <div class="action-container" style="margin-top: 15px;">
                    <a href="?tab=overview&action=generate_tasks" class="action-button">Generate More Tasks</a>
                </div>
            </div>
        </div>
        
        <!-- Personal info & AI insights row -->
        <div class="card-row">
            <div class="card flex-1">
                <h4 class="card-title">Personal Information</h4>
                <div class="info-grid">
                    <div class="info-item">
                        <p>Department</p>
                        <h5>' . $df_employees[0]['department'] . '</h5>
                    </div>
                    <div class="info-item">
                        <p>Join Date</p>
                        <h5>' . $df_employees[0]['join_date'] . '</h5>
                    </div>
                    <div class="info-item">
                        <p>Months Employed</p>
                        <h5>' . $df_employees[0]['months_employed'] . '</h5>
                    </div>
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <p>Base Salary</p>
                        <h5>' . $df_employees[0]['base_salary'] . ' DKK</h5>
                    </div>
                    <div class="info-item">
                        <p>Holiday Allowance</p>
                        <h5>' . $df_employees[0]['holiday_allowance'] . ' DKK</h5>
                    </div>
                </div>
            </div>
            
            <div class="card flex-1" style="background-color: #f8f9fa;">
                <h4 class="card-title">AI Insights</h4>
                <div class="insight-grid">
                    <div class="insight-item">
                        <p>Performance</p>
                        <h5 style="color: #27ae60;">High</h5>
                    </div>
                    <div class="insight-item">
                        <p>Attendance</p>
                        <h5 style="color: #27ae60;">98%</h5>
                    </div>
                    <div class="insight-item">
                        <p>Late Arrivals</p>
                        <h5 style="color: #27ae60;">Low</h5>
                    </div>
                    <div class="insight-item">
                        <p>Overtime</p>
                        <h5 style="color: #f39c12;">Moderate</h5>
                    </div>
                </div>
                <div class="recommendation-container">
                    <p class="recommendation-label">Recommendation</p>
                    <p class="recommendation">Keep up the good work!</p>
                </div>
            </div>
        </div>
        
        <!-- Performance graph - using Chart.js -->
        <div class="card">
            <h4 class="card-title">Performance & Attendance Trends</h4>
            <canvas id="performanceChart" height="300"></canvas>
            <script>
                var ctx = document.getElementById("performanceChart").getContext("2d");
                var performanceChart = new Chart(ctx, {
                    type: "line",
                    data: {
                        labels: ' . json_encode($months) . ',
                        datasets: [
                            {
                                label: "Performance",
                                data: ' . json_encode($performance_data) . ',
                                borderColor: "' . $colors['primary'] . '",
                                backgroundColor: "transparent",
                                borderWidth: 3,
                                pointRadius: 5
                            },
                            {
                                label: "Attendance",
                                data: ' . json_encode($attendance_data) . ',
                                borderColor: "' . $colors['secondary'] . '",
                                backgroundColor: "transparent",
                                borderWidth: 3,
                                pointRadius: 5
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: false,
                                min: 60,
                                max: 100
                            }
                        }
                    }
                });
            </script>
        </div>';
    } 
    elseif ($tab == 'attendance') {
        return '
        <div class="card-row">
            <div class="card">
                <h4 class="card-title">Recent Attendance</h4>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Check In</th>
                                <th>Check Out</th>
                                <th>Overtime</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>';
                        
                        foreach ($df_attendance as $row) {
                            echo '<tr>
                                <td>' . $row['date'] . '</td>
                                <td>' . $row['check_in'] . '</td>
                                <td>' . $row['check_out'] . '</td>
                                <td>' . ($row['overtime_hours'] ? $row['overtime_hours'] . ' hrs' : '-') . '</td>
                                <td><span class="status-badge present">' . $row['status'] . '</span></td>
                            </tr>';
                        }
                        
                        echo '
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <h4 class="card-title">Monthly Overtime Hours</h4>
                <canvas id="overtimeChart" height="300"></canvas>
                <script>
                    var ctx = document.getElementById("overtimeChart").getContext("2d");
                    var overtimeChart = new Chart(ctx, {
                        type: "bar",
                        data: {
                            labels: ' . json_encode($months) . ',
                            datasets: [{
                                label: "Overtime Hours",
                                data: ' . json_encode($overtime_monthly) . ',
                                backgroundColor: "' . $colors['accent'] . '"
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                </script>
            </div>
        </div>';
    } 
    elseif ($tab == 'leave') {
        return '
        <div class="card-row">
            <div class="card flex-1">
                <h4 class="card-title">Leave Balance</h4>
                <canvas id="leaveBalanceChart" height="300"></canvas>
                <script>
                    var ctx = document.getElementById("leaveBalanceChart").getContext("2d");
                    var leaveBalanceChart = new Chart(ctx, {
                        type: "bar",
                        data: {
                            labels: ' . json_encode($leave_types) . ',
                            datasets: [
                                {
                                    label: "Remaining",
                                    data: ' . json_encode($leave_remaining) . ',
                                    backgroundColor: "' . $colors['primary'] . '"
                                },
                                {
                                    label: "Used",
                                    data: ' . json_encode($leave_used) . ',
                                    backgroundColor: "' . $colors['accent'] . '"
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                x: {
                                    stacked: true,
                                },
                                y: {
                                    stacked: true,
                                    beginAtZero: true
                                }
                            }
                        }
                    });
                </script>
            </div>
            
            <div class="card flex-1">
                <h4 class="card-title">Leave History</h4>
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Start Date</th>
                                <th>End Date</th>
                                <th>Duration</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>';
                        
                        foreach ($df_leaves as $row) {
                            echo '<tr>
                                <td>' . $row['leave_type'] . '</td>
                                <td>' . $row['start_date'] . '</td>
                                <td>' . $row['end_date'] . '</td>
                                <td>' . $row['duration'] . ' days</td>
                                <td><span class="status-badge approved">' . $row['status'] . '</span></td>
                            </tr>';
                        }
                        
                        echo '
                        </tbody>
                    </table>
                </div>
                <div class="action-container">
                    <button class="action-button">Request Leave</button>
                </div>
            </div>
        </div>';
    } 
    elseif ($tab == 'performance') {
        return '
        <div class="card">
            <h4 class="card-title">Performance Overview</h4>
            <canvas id="radarChart" height="400"></canvas>
            <script>
                var ctx = document.getElementById("radarChart").getContext("2d");
                var radarChart = new Chart(ctx, {
                    type: "radar",
                    data: {
                        labels: ["Productivity", "Attendance", "Communication", "Collaboration", "Quality"],
                        datasets: [
                            {
                                label: "Current",
                                data: [89, 95, 82, 78, 90],
                                backgroundColor: "rgba(31, 119, 180, 0.2)",
                                borderColor: "' . $colors['primary'] . '",
                                pointBackgroundColor: "' . $colors['primary'] . '",
                                pointBorderColor: "#fff",
                                pointHoverBackgroundColor: "#fff",
                                pointHoverBorderColor: "' . $colors['primary'] . '"
                            },
                            {
                                label: "Target",
                                data: [75, 75, 75, 75, 75],
                                backgroundColor: "rgba(255, 127, 14, 0.2)",
                                borderColor: "' . $colors['accent'] . '",
                                pointBackgroundColor: "' . $colors['accent'] . '",
                                pointBorderColor: "#fff",
                                pointHoverBackgroundColor: "#fff",
                                pointHoverBorderColor: "' . $colors['accent'] . '"
                            }
                        ]
                    },
                    options: {
                        scale: {
                            angleLines: {
                                display: true
                            },
                            ticks: {
                                suggestedMin: 0,
                                suggestedMax: 100
                            }
                        }
                    }
                });
            </script>
        </div>';
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Employee Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #f9fafb;
            color: #2c3e50;
        }
        .dashboard-container {
            max-width: 1200px;
            margin: auto;
            padding: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        .card:hover {
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .card-title {
            color: #2c3e50;
            margin-top: 0;
            margin-bottom: 20px;
            font-weight: 600;
            border-bottom: 1px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .card-row {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .flex-1 {
            flex: 1;
            min-width: 300px;
        }
        .info-grid, .insight-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 15px;
        }
        .info-item, .insight-item {
            padding: 10px;
        }
        .info-item p, .insight-item p {
            margin: 0;
            font-size: 0.85rem;
            color: #7f8c8d;
        }
        .info-item h5, .insight-item h5 {
            margin: 5px 0 0 0;
            font-size: 1.1rem;
            font-weight: 600;
        }
        .recommendation-container {
            margin-top: 15px;
            padding: 10px;
        }
        .recommendation-label {
            margin: 0;
            font-size: 0.85rem;
            color: #7f8c8d;
        }
        .recommendation {
            margin: 5px 0 0 0;
            font-size: 1rem;
            font-weight: 500;
        }
        table.data-table {
            width: 100%;
            border-collapse: collapse;
        }
        .data-table th, .data-table td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        .data-table th {
            background: #f6f8fa;
            font-weight: 600;
            color: #2c3e50;
        }
        .data-table tr:hover {
            background-color: #f9fafb;
        }
        .status-badge, .priority-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .present, .approved {
            background-color: #e3f8e5;
            color: #27ae60;
        }
        .pending, .new {
            background-color: #eaecee;
            color: #7f8c8d;
        }
        .high {
            background-color: #fce5e5;
            color: #e74c3c;
        }
        .medium {
            background-color: #fef5e7;
            color: #f39c12;
        }
        .low {
            background-color: #e8f4f8;
            color: #3498db;
        }
        .action-container {
            margin-top: 20px;
            display: flex;
            justify-content: flex-end;
        }
        .action-button {
            background-color: #1f77b4;
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
            transition: background-color 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        .action-button:hover {
            background-color: #166aaa;
        }
        .tab-content {
            margin-top: 20px;
        }
        /* Weather Widget Styles */
        .weather-icon, .forecast-icon {
            font-size: 2.5rem;
            margin-right: 15px;
        }
        .forecast-icon {
            font-size: 1.5rem;
        }
        .current-weather {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .temp {
            font-size: 1.8rem;
            margin: 0;
            font-weight: 600;
        }
        .condition {
            margin: 0;
            color: #7f8c8d;
        }
        .weather-details {
            margin-left: 20px;
        }
        .weather-details p {
            margin: 5px 0;
            color: #7f8c8d;
        }
        .weather-forecast {
            display: flex;
            justify-content: space-between;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }
        .forecast-day {
            text-align: center;
            flex: 1;
        }
        .forecast-day h5 {
            margin: 0 0 10px;
            font-weight: 600;
        }
        .forecast-day p {
            margin: 5px 0;
        }
        .weather-warning {
            color: #e74c3c;
            font-weight: 600;
            font-size: 0.8rem;
            margin-top: 8px;
        }
        .weather-main {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        /* Tabs */
        .tabs {
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-top: 20px;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
        }
        .tab.active {
            border-bottom: 3px solid #1f77b4;
            font-weight: 600;
        }
        .tab:hover {
            background-color: #f5f5f5;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="dashboard-container">
        <div style="display: flex; flex-direction: column; align-items: center;">
            <h2 style="margin-bottom: 10px;">Employee Dashboard</h2>
            <h3 style="color: <?= $colors['text'] ?>; font-weight: normal;">
                Welcome, <?= $df_employees[0]['name'] ?> (<?= $df_employees[0]['employee_id'] ?>)
            </h3>
        </div>
        
        <div class="tabs">
            <a href="?tab=overview" class="tab <?= $active_tab == 'overview' ? 'active' : '' ?>">Overview</a>
            <a href="?tab=attendance" class="tab <?= $active_tab == 'attendance' ? 'active' : '' ?>">Attendance</a>
            <a href="?tab=leave" class="tab <?= $active_tab == 'leave' ? 'active' : '' ?>">Leave Management</a>
            <a href="?tab=performance" class="tab <?= $active_tab == 'performance' ? 'active' : '' ?>">Performance</a>
        </div>
        
        <div class="tab-content">
            <?= renderTabContent($active_tab, get_defined_vars()) ?>
        </div>
    </div>
</body>
</html>