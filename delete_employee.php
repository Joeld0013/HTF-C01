<?php
include 'dbconnect.php';

header('Content-Type: application/json'); // Always return JSON

$response = ['success' => false, 'message' => ''];

try {
    // Validate input
    if (!isset($_POST['employee_id'])) {
        throw new Exception('Employee ID is required');
    }

    $employee_id = $_POST['employee_id'];

    // Prepare and execute deletion from employee_dash table
    $stmt = $conn->prepare("DELETE FROM employee_dash WHERE employee_id = ?");
    $stmt->bind_param("s", $employee_id);
    $stmt->execute();

    // Also delete from users table to maintain consistency
    $user_stmt = $conn->prepare("DELETE FROM users WHERE email = (SELECT email FROM employee_dash WHERE employee_id = ?)");
    $user_stmt->bind_param("s", $employee_id);
    $user_stmt->execute();

    if ($stmt->affected_rows > 0) {
        $response['success'] = true;
        $response['message'] = 'Employee deleted successfully';
    } else {
        $response['message'] = 'No employee found with that ID';
    }

    $stmt->close();
    $user_stmt->close();
} catch (Exception $e) {
    $response['message'] = 'Error: ' . $e->getMessage();
    error_log('Delete Error: ' . $e->getMessage());
}

$conn->close();
echo json_encode($response);
?>