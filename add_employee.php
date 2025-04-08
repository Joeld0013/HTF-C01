<?php
header('Content-Type: application/json');
require 'dbconnect.php';

try {
    $input = json_decode(file_get_contents('php://input'), true);
    
    // Generate employee ID with gap filling
    $stmt = $conn->prepare("SELECT employee_id FROM employee_dash ORDER BY employee_id");
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
    
    $employee_id = 'EM' . str_pad($next_num, 4, '0', STR_PAD_LEFT);
    
    // Insert into employee_dash
    $stmt = $conn->prepare("INSERT INTO employee_dash (
        employee_id, name, gender, department, role, 
        email, join_date, created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, CURDATE(), NOW(), NOW())");
    
    $stmt->bind_param("ssssss", 
        $employee_id,
        $input['name'],
        $input['gender'],
        $input['department'],
        $input['role'],
        $input['email']
    );
    
    if ($stmt->execute()) {
        // Insert into users table
        $user_stmt = $conn->prepare("INSERT INTO users (
            name, email, password, designation, join_date, gender, created_at, updated_at
        ) VALUES (?, ?, ?, ?, CURDATE(), ?, NOW(), NOW())");
        
        $hashed_password = password_hash($input['password'], PASSWORD_DEFAULT);
        $user_stmt->bind_param("sssss", 
            $input['name'],
            $input['email'],
            $hashed_password,
            $input['role'],
            $input['gender']
        );
        $user_stmt->execute();
        
        echo json_encode(["status" => "success", "employee_id" => $employee_id]);
    } else {
        throw new Exception("Failed to add employee: " . $stmt->error);
    }
} catch (Exception $e) {
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
?>