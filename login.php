<?php
session_start();
include 'dbconnect.php';

$email = $_POST['email'];
$password = $_POST['password'];

// Direct check against database (no hashing)
$query = "SELECT a_id FROM admin WHERE email='$email' AND password='$password'";
$result = $conn->query($query);

if ($result->num_rows === 1) {
    $_SESSION['admin_id'] = $result->fetch_assoc()['a_id'];
    header("Location: templates/admin.html");
    exit();
} else {
    header("Location: index.php?error=Invalid email or password");
    exit();
}
?>