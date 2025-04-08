<?php
header('Content-Type: application/json');
require 'dbconnect.php';

// Map full role to roleId
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
    $input = json_decode(file_get_contents("php://input"), true);
    $name = $input['name'] ?? '';
    $role = $input['role'] ?? '';

    $roleId = generateRoleId($role);
    if (!$roleId) throw new Exception("Invalid role");

    // Generate Email and Password
    $stmt = $conn->prepare("SELECT COUNT(*) as total FROM `$roleId`");
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();
    $nextNum = str_pad($row['total'] + 1, 2, "0", STR_PAD_LEFT);

    $email = "25{$roleId}{$nextNum}@gmail.com";
    $password = "{$roleId}{$nextNum}";
    $status = "Inactive";
    $created_time = date("Y-m-d H:i:s");

    // Insert into correct role-based table
    $stmt = $conn->prepare("INSERT INTO `$roleId` (name, role, email, password, status,joined_time) VALUES (?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("ssssss", $name, $role, $email, $password, $status,$joined_time);

    if ($stmt->execute()) {
        echo json_encode(["status" => "success", "email" => $email, "password" => $password]);
    } else {
        throw new Exception("Insert failed: " . $stmt->error);
    }
} catch (Exception $e) {
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
?>
