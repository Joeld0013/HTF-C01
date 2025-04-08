<?php
header('Content-Type: application/json');
require 'dbconnect.php';

$response = ['success' => false, 'message' => ''];

try {
    $input = json_decode(file_get_contents('php://input'), true);
    
    $employee_id = $input['employee_id'] ?? '';
    $name = $input['name'] ?? '';
    $gender = $input['gender'] ?? '';
    $department = $input['department'] ?? '';
    $role = $input['role'] ?? '';
    $email = $input['email'] ?? '';

    // Validate inputs
    if (empty($employee_id) || empty($name) || empty($email)) {
        throw new Exception('Required fields are missing');
    }

    // Start transaction
    $conn->begin_transaction();

    // Update employee_dash
    $stmt = $conn->prepare("UPDATE employee_dash SET 
        name = ?, 
        gender = ?, 
        department = ?, 
        role = ?, 
        email = ?, 
        updated_at = NOW() 
        WHERE employee_id = ?");
    $stmt->bind_param("ssssss", $name, $gender, $department, $role, $email, $employee_id);
    $stmt->execute();

    // Update users table
    $user_stmt = $conn->prepare("UPDATE users SET 
        name = ?, 
        email = ?, 
        designation = ?, 
        updated_at = NOW() 
        WHERE email = (SELECT email FROM (SELECT email FROM employee_dash WHERE employee_id = ?) AS temp)");
    $user_stmt->bind_param("ssss", $name, $email, $role, $employee_id);
    $user_stmt->execute();

    $conn->commit();
    $response['success'] = true;
    $response['message'] = 'Employee updated successfully';
} catch (Exception $e) {
    $conn->rollback();
    $response['message'] = 'Error: ' . $e->getMessage();
    error_log('Update Error: ' . $e->getMessage());
}

$conn->close();
echo json_encode($response);
?>