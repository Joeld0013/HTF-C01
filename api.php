<?php
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");


// Database connection
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "workforce";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die(json_encode(['error' => "Connection failed: " . $conn->connect_error]));
}

$action = $_GET['action'] ?? '';

try {
    switch ($action) {
        case 'get_workers':
            $role = $_GET['role'] ?? '';
            if (empty($role)) {
                throw new Exception("Role parameter is required");
            }
            getWorkersByRole($conn, $role);
            break;
            
        case 'save_schedule':
            saveSchedule($conn);
            break;
            
        case 'load_schedule':
            $weekStart = $_GET['weekStart'] ?? '';
            if (empty($weekStart)) {
                throw new Exception("weekStart parameter is required");
            }
            loadSchedule($conn, $weekStart);
            break;
            
        default:
            throw new Exception("Invalid action");
    }
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}

$conn->close();

function getWorkersByRole($conn, $role) {
    $stmt = $conn->prepare("
        SELECT employee_id, name, role, email, photo, gender, age 
        FROM employee_dash 
        WHERE role = ?
    ");
    if (!$stmt) {
        throw new Exception("Prepare failed: " . $conn->error);
    }
    
    $stmt->bind_param("s", $role);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $workers = [];
    while ($row = $result->fetch_assoc()) {
        $workers[] = [
            'id' => $row['employee_id'],
            'name' => $row['name'],
            'role' => $row['role'],
            'email' => $row['email'],
            'photo' => $row['photo'] ? base64_encode($row['photo']) : null,
            'gender' => $row['gender'],
            'age' => $row['age']
        ];
    }
    
    echo json_encode($workers);
}

function saveSchedule($conn) {
    $json = file_get_contents('php://input');
    $data = json_decode($json, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception("Invalid JSON data");
    }
    
    $weekStart = $data['weekStart'] ?? '';
    $assignments = $data['assignments'] ?? [];
    
    if (empty($weekStart)) {
        throw new Exception("weekStart is required");
    }
    
    // Begin transaction
    $conn->begin_transaction();
    
    try {
        // Delete existing assignments for this week
        $stmt = $conn->prepare("DELETE FROM schedule_assignments WHERE week_start = ?");
        if (!$stmt) {
            throw new Exception("Prepare failed: " . $conn->error);
        }
        $stmt->bind_param("s", $weekStart);
        $stmt->execute();
        
        // Insert new assignments
        $stmt = $conn->prepare("
            INSERT INTO schedule_assignments 
            (week_start, day, shift, role, employee_id) 
            VALUES (?, ?, ?, ?, ?)
        ");
        if (!$stmt) {
            throw new Exception("Prepare failed: " . $conn->error);
        }
        
        foreach ($assignments as $assignment) {
            $day = $assignment['day'] ?? '';
            $shift = $assignment['shift'] ?? '';
            $role = $assignment['role'] ?? '';
            $employeeId = $assignment['employeeId'] ?? '';
            
            if (empty($day) || empty($shift) || empty($role)) {
                continue; // Skip invalid assignments
            }
            
            $stmt->bind_param("ssiss", $weekStart, $day, $shift, $role, $employeeId);
            if (!$stmt->execute()) {
                throw new Exception("Execute failed: " . $stmt->error);
            }
        }
        
        $conn->commit();
        echo json_encode(['success' => true, 'message' => 'Schedule saved successfully']);
    } catch (Exception $e) {
        $conn->rollback();
        throw $e;
    }
}

function loadSchedule($conn, $weekStart) {
    $stmt = $conn->prepare("
        SELECT day, shift, role, employee_id 
        FROM schedule_assignments 
        WHERE week_start = ?
        ORDER BY day, shift
    ");
    if (!$stmt) {
        throw new Exception("Prepare failed: " . $conn->error);
    }
    
    $stmt->bind_param("s", $weekStart);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $assignments = [];
    while ($row = $result->fetch_assoc()) {
        $assignments[] = [
            'day' => $row['day'],
            'shift' => $row['shift'],
            'role' => $row['role'],
            'employeeId' => $row['employee_id']
        ];
    }
    
    // Get worker names for the assignments
    $workerInfo = [];
    if (!empty($assignments)) {
        $employeeIds = array_filter(array_unique(array_column($assignments, 'employeeId')));
        if (!empty($employeeIds)) {
            $placeholders = implode(',', array_fill(0, count($employeeIds), '?'));
            $types = str_repeat('s', count($employeeIds));
            
            $stmt = $conn->prepare("
                SELECT employee_id, name 
                FROM employee_dash 
                WHERE employee_id IN ($placeholders)
            ");
            if (!$stmt) {
                throw new Exception("Prepare failed: " . $conn->error);
            }
            
            $stmt->bind_param($types, ...$employeeIds);
            $stmt->execute();
            $workerResult = $stmt->get_result();
            
            while ($row = $workerResult->fetch_assoc()) {
                $workerInfo[$row['employee_id']] = $row['name'];
            }
        }
    }
    
    // Add worker names to assignments
    foreach ($assignments as &$assignment) {
        if ($assignment['employeeId'] && isset($workerInfo[$assignment['employeeId']])) {
            $assignment['employeeName'] = $workerInfo[$assignment['employeeId']];
        }
    }
    
    echo json_encode($assignments);
}
?>