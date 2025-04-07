<?php
require_once 'dbconnect.php';

header('Content-Type: application/json');

$response = ['success' => false, 'message' => ''];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if (empty($email) || empty($password)) {
        $response['message'] = 'All fields are required';
        echo json_encode($response);
        exit;
    }

    try {
        // Update password for the given email
        $stmt = $conn->prepare("UPDATE admin SET password = ? WHERE email = ?");
        $stmt->bind_param("ss", $password, $email);
        if ($stmt->execute()) {
            $response['success'] = true;
            $response['message'] = 'Password updated successfully!';
        } else {
            $response['message'] = 'Failed to update password.';
        }

        $stmt->close();
        $conn->close();
    } catch (Exception $e) {
        $response['message'] = 'Error: ' . $e->getMessage();
    }
} else {
    $response['message'] = 'Invalid request method';
}

echo json_encode($response);
?>
