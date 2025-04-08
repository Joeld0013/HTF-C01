<?php
header('Content-Type: application/json');
require 'dbconnect.php';

try {
    $stmt = $conn->prepare("SELECT * FROM employee_dash ORDER BY created_at DESC");
    $stmt->execute();
    $result = $stmt->get_result();
    
    $employees = [];
    while ($row = $result->fetch_assoc()) {
        $employees[] = $row;
    }
    
    echo json_encode($employees);
} catch (Exception $e) {
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
?>