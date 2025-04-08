<?php
header('Content-Type: application/json');
require 'dbconnect.php';

try {
    $role = $_GET['role'] ?? '';
    
    // Convert role to lowercase and remove spaces/special chars
    $role_short = strtolower(preg_replace('/[^a-z]/i', '', $role));
    
    // Get all existing employee IDs sorted numerically
    $stmt = $conn->prepare("SELECT employee_id FROM employee_dash ORDER BY CAST(SUBSTRING(employee_id, 3) AS UNSIGNED)");
    $stmt->execute();
    $result = $stmt->get_result();
    
    $existing_ids = [];
    while ($row = $result->fetch_assoc()) {
        $num = (int)substr($row['employee_id'], 2); // Extract numeric part after 'EM'
        $existing_ids[] = $num;
    }
    
    // Find the first available gap
    $next_num = 1;
    foreach ($existing_ids as $id) {
        if ($id > $next_num) {
            break; // Found a gap
        }
        $next_num = $id + 1;
    }
    
    $email = "25{$role_short}{$next_num}@gmail.com";
    $password = "{$role_short}{$next_num}";
    
    echo json_encode([
        "status" => "success",
        "email" => $email,
        "password" => $password,
        "next_num" => $next_num
    ]);
} catch (Exception $e) {
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
?>