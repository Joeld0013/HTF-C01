<?php
header('Content-Type: application/json');

// Database connection
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "workforce";

try {
    $conn = new PDO("mysql:host=$servername;dbname=$dbname", $username, $password);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Get role from query parameter
    $role = isset($_GET['role']) ? $_GET['role'] : '';
    
    if (empty($role)) {
        throw new Exception("Role parameter is required");
    }
    
    // Prepare and execute query with the correct field names
    $stmt = $conn->prepare("SELECT employee_id, name, role, email, created_at FROM employee_dash WHERE role = :role");
    $stmt->bindParam(':role', $role);
    $stmt->execute();
    
    $workers = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode($workers);
    
} catch(PDOException $e) {
    echo json_encode(['error' => 'Database error: ' . $e->getMessage()]);
} catch(Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
?>