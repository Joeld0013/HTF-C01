<?php
header('Content-Type: application/json');
require 'dbconnect.php';  // Ensure this connects to 'workforce' DB

// Map full role names to table IDs
function generateRoleId($role) {
    $map = [
        "Site Supervisor / Foreman" => "sitesupervisor",
        "General Laborer" => "generallaborer",
        "Electrician" => "electrician",
        "Plumber" => "plumber",
        "Carpenter" => "carpenter",
        "Mason" => "mason",
        "Welder" => "welder",
        "Crane Operator / Heavy Equipment Operator" => "craneoperator",
        "Truck Driver / Material Transporter" => "truckdriver",
        "Security Guard" => "securityguard"
    ];
    return $map[$role] ?? null;
}

try {
    if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['role'])) {
        $role = urldecode(trim($_GET['role']));
        $roleId = generateRoleId($role);

        if (!$roleId) {
            throw new Exception("Invalid role: $role");
        }

        // Now we use `$roleId` as the table name
        $stmt = $conn->prepare("SELECT SUBSTRING(email, 3 + LENGTH(?), 2) as num 
                                FROM `$roleId` 
                                WHERE email LIKE CONCAT('25', ?, '%@gmail.com') 
                                ORDER BY num ASC");
        $stmt->bind_param("ss", $roleId, $roleId);
        $stmt->execute();
        $result = $stmt->get_result();

        $existingNumbers = [];
        while ($row = $result->fetch_assoc()) {
            $existingNumbers[] = intval($row['num']);
        }

        // Find the first missing number between 1-99
        for ($i = 1; $i <= 99; $i++) {
            if (!in_array($i, $existingNumbers)) {
                $nextNum = $i;
                break;
            }
        }

        if (!isset($nextNum)) {
            throw new Exception("No available ID slots");
        }

        $formattedNum = str_pad($nextNum, 2, "0", STR_PAD_LEFT);
        echo json_encode([
            "status" => "success",
            "email" => "25{$roleId}{$formattedNum}@gmail.com",
            "password" => "{$roleId}{$formattedNum}",
            "generated_id" => $formattedNum
        ]);
    } else {
        throw new Exception("Invalid request format");
    }
} catch (Exception $e) {
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}

$conn->close();
?>
