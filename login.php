<?php
session_start();
require_once 'dbconnect.php';

// Get form data
$email = $_POST['email'] ?? '';
$password = $_POST['password'] ?? '';

// Basic validation
if (empty($email) || empty($password)) {
    header("Location: index.html?error=empty_fields");
    exit();
}

try {
    // Check admin credentials
    $stmt = $conn->prepare("SELECT a_id, email, password FROM admin WHERE email = ?");
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows === 1) {
        $admin = $result->fetch_assoc();
        
        // Compare plain text passwords
        if ($password === $admin['password']) {
            // Set session variables
            $_SESSION['admin_id'] = $admin['a_id'];
            $_SESSION['admin_email'] = $admin['email'];
            
            // Redirect to admin page
            header("Location: templates/admin.html");
            exit();
        }
    }
    
    // If we get here, credentials were invalid
    header("Location: index.html?error=invalid_credentials");
    exit();
    
} catch (Exception $e) {
    header("Location: index.html?error=database_error");
    exit();
}
?>