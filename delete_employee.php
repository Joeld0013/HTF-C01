<?php
header('Content-Type: application/json');
require 'dbconnect.php';

$response = ['success' => false, 'message' => ''];

try {
    $employee_id = $_POST['employee_id'] ?? '';
    
    if (empty($employee_id)) {
        throw new Exception('Employee ID is required');
    }

    // Start transaction
    $conn->begin_transaction();

    // First delete from users table (based on email)
    $stmt = $conn->prepare("DELETE FROM users WHERE email = (SELECT email FROM employee_dash WHERE employee_id = ?)");
    $stmt->bind_param("s", $employee_id);
    $stmt->execute();

    // Then delete from employee_dash
    $stmt = $conn->prepare("DELETE FROM employee_dash WHERE employee_id = ?");
    $stmt->bind_param("s", $employee_id);
    $stmt->execute();

    if ($stmt->affected_rows > 0) {
        $conn->commit();
        $response['success'] = true;
        $response['message'] = 'Employee deleted successfully';
    } else {
        $conn->rollback();
        $response['message'] = 'No employee found with that ID';
    }
} catch (Exception $e) {
    $conn->rollback();
    $response['message'] = 'Error: ' . $e->getMessage();
    error_log('Delete Error: ' . $e->getMessage());
}

$conn->close();
echo json_encode($response);
?>