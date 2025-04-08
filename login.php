<?php
session_start();
header('Content-Type: application/json');
require_once 'dbconnect.php';

$response = ['success' => false, 'message' => ''];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if (empty($email) || empty($password)) {
        $response['message'] = 'Please fill in all fields';
        echo json_encode($response);
        exit();
    }

    try {
        $stmt = $conn->prepare("SELECT a_id, email, password FROM admin WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows === 1) {
            $admin = $result->fetch_assoc();
            if ($password === $admin['password']) {  // Use hashed passwords in production
                $_SESSION['admin_id'] = $admin['a_id'];
                $_SESSION['admin_email'] = $admin['email'];

                $response['success'] = true;
                $response['message'] = 'Login successful';
                $response['redirect'] = 'http://localhost:8050'; // Python dashboard URL
            } else {
                $response['message'] = 'Invalid email or password';
            }
        } else {
            $response['message'] = 'Invalid email or password';
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
