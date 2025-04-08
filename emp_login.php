<?php
session_start();
header('Content-Type: application/json');

require_once 'dbconnect.php';

$response = ['success' => false, 'message' => '', 'role' => ''];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if (empty($email) || empty($password)) {
        $response['message'] = 'Please fill in all fields';
        echo json_encode($response);
        exit();
    }

    try {
        // Check employee_dash table (hashed password verification)
        $stmt = $conn->prepare("SELECT employee_id, name, email, password, role FROM employee_dash WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            $user = $result->fetch_assoc();

            // Verify hashed password
            if (password_verify($password, $user['password'])) {
                $_SESSION['employee_id'] = $user['employee_id'];
                $_SESSION['employee_email'] = $user['email'];
                $_SESSION['employee_name'] = $user['name'];
                $_SESSION['employee_role'] = strtolower(str_replace(' ', '', $user['role']));

                $response['success'] = true;
                $response['message'] = 'Login successful';
                $response['role'] = $_SESSION['employee_role'];
            } else {
                $response['message'] = 'Invalid password';
            }
        } else {
            $response['message'] = 'Employee not found';
        }

        $stmt->close();
    } catch (Exception $e) {
        $response['message'] = 'Database error occurred';
        error_log('Login error: ' . $e->getMessage());
    }

    $conn->close();
} else {
    $response['message'] = 'Invalid request method';
}

echo json_encode($response);
?>