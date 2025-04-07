<?php
header('Content-Type: application/json');
ini_set('display_errors', 0);
require 'dbconnect.php';

function getRoleTable($role) {
    return strtolower(str_replace([' ', '/'], '', $role));
}

try {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $data = json_decode(file_get_contents('php://input'), true);
        
        // Validate input
        if (empty($data['name']) || empty($data['role'])) {
            throw new Exception("Name and role are required");
        }

        $name = $data['name'];
        $role = $data['role'];
        $tableName = getRoleTable($role);

        // Find first available ID
        $result = $conn->query("SELECT slno FROM `$tableName` ORDER BY slno");
        $existingIds = [];
        while ($row = $result->fetch_assoc()) {
            $existingIds[] = $row['slno'];
        }

        // Find first gap or next number
        $newId = 1;
        foreach ($existingIds as $id) {
            if ($id > $newId) break; // Found a gap
            $newId = $id + 1;
        }

        // Generate email/password
        $rolePrefix = strtolower(str_replace([' ', '/'], '', $role));
        $formattedId = str_pad($newId, 2, '0', STR_PAD_LEFT);
        $email = "25{$rolePrefix}{$formattedId}@gmail.com";
        $password = "{$rolePrefix}{$formattedId}";

        // Insert into database
        $stmt = $conn->prepare("INSERT INTO `$tableName` 
                              (slno, name, role, email, password, status, joined_time, facescan) 
                              VALUES (?, ?, ?, ?, ?, 'Inactive', NOW(), '')");
        
        $stmt->bind_param("issss", $newId, $name, $role, $email, $password);
        
        if (!$stmt->execute()) {
            throw new Exception("Failed to add employee: " . $conn->error);
        }

        echo json_encode([
            'status' => 'success',
            'email' => $email,
            'password' => $password,
            'id' => $newId
        ]);

    } else {
        throw new Exception("Invalid request method");
    }
} catch (Exception $e) {
    echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);
}
?>