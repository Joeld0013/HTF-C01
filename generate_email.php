<?php
header('Content-Type: application/json');
require 'dbconnect.php';

try {
    $role = $_GET['role'] ?? '';
    $role_short = strtolower(str_replace([' ', '/'], '', explode('(', $role)[0]));
    
    // Find gaps in existing IDs
    $stmt = $conn->prepare("SELECT employee_id FROM employee_dash WHERE role = ? ORDER BY employee_id");
    $stmt->bind_param("s", $role);
    $stmt->execute();
    $result = $stmt->get_result();
    
    $existing_ids = [];
    while ($row = $result->fetch_assoc()) {
        $num = (int)substr($row['employee_id'], 2); // Extract numeric part after 'EM'
        $existing_ids[] = $num;
    }
    
    // Find the first available gap or next number
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