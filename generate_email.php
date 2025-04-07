<?php
header('Content-Type: application/json');
ini_set('display_errors', 0);
require 'dbconnect.php';

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
        $role = urldecode($_GET['role']);
        $roleId = generateRoleId($role);

        if (!$roleId) {
            throw new Exception("Invalid role");
        }

        $tableName = $roleId;
        
        // Get all existing numbers
        $stmt = $conn->prepare("SELECT SUBSTRING(email, 3 + LENGTH(?), 2) as num FROM `$tableName` 
                               WHERE email LIKE CONCAT('25', ?, '%@gmail.com') ORDER BY num");
        $stmt->bind_param("ss", $roleId, $roleId);
        $stmt->execute();
        $result = $stmt->get_result();
        
        $existingNumbers = [];
        while ($row = $result->fetch_assoc()) {
            $existingNumbers[] = intval($row['num']);
        }
        
        // Find first missing number (1-99)
        $count = 1;
        while ($count <= 99) {
            if (!in_array($count, $existingNumbers)) {
                break;
            }
            $count++;
        }

        $formattedCount = str_pad($count, 2, "0", STR_PAD_LEFT);
        echo json_encode([
            "status" => "success",
            "email" => "25{$roleId}{$formattedCount}@gmail.com",
            "password" => "{$roleId}{$formattedCount}",
            "generated_id" => $count
        ]);
    } else {
        throw new Exception("Invalid request");
    }
} catch (Exception $e) {
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}

$conn->close();
?>