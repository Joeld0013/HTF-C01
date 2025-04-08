<?php
header('Content-Type: application/json');
require 'dbconnect.php';

try {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (!isset($input['next_num'])) {
        throw new Exception("Missing next_num in request");
    }

    // Hash the password before storing
    $hashed_password = password_hash($input['password'], PASSWORD_DEFAULT);
    
    // Generate employee ID with proper padding
    $employee_id = 'EM' . str_pad($input['next_num'], 4, '0', STR_PAD_LEFT);
    
    // Start transaction
    $conn->begin_transaction();
    
    try {
        // Insert into employee_dash
        $stmt = $conn->prepare("INSERT INTO employee_dash (
            employee_id, name, gender, department, role, 
            email, password, join_date, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, CURDATE(), NOW(), NOW())");
        
        $stmt->bind_param("sssssss", 
            $employee_id,
            $input['name'],
            $input['gender'],
            $input['department'],
            $input['role'],
            $input['email'],
            $hashed_password
        );
        
        if (!$stmt->execute()) {
            throw new Exception("Failed to add to employee_dash: " . $stmt->error);
        }
        
        // Also insert into users table
        $user_stmt = $conn->prepare("INSERT INTO users (
            name, email, password, designation, join_date, gender, created_at, updated_at
        ) VALUES (?, ?, ?, ?, CURDATE(), ?, NOW(), NOW())");
        
        $user_stmt->bind_param("sssss", 
            $input['name'],
            $input['email'],
            $hashed_password,
            $input['role'],
            $input['gender']
        );
        
        if (!$user_stmt->execute()) {
            throw new Exception("Failed to add to users: " . $user_stmt->error);
        }
        
        $conn->commit();
        
        echo json_encode([
            "status" => "success",
            "employee_id" => $employee_id,
            "email" => $input['email'],
            "password" => $input['password'] // Return plain password only once
        ]);
    } catch (Exception $e) {
        $conn->rollback();
        throw $e;
    }
} catch (Exception $e) {
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
?>