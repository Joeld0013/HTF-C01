<?php
session_start();
header('Content-Type: application/json');

require_once 'dbconnect.php';

$response = ['success' => false, 'message' => '', 'role' => ''];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = trim($_POST['email'] ?? '');
    $password = trim($_POST['password'] ?? '');

    // Basic validation
    if (empty($email) || empty($password)) {
        $response['message'] = 'Please fill in all fields';
        echo json_encode($response);
        exit();
    }

    try {
        // Define all role tables (excluding admin)
        $role_tables = [
            'carpenter' => ['table' => 'carpenter', 'id_field' => 'slno'],
            'craneoperator' => ['table' => 'craneoperator', 'id_field' => 'slno'],
            'electrician' => ['table' => 'electrician', 'id_field' => 'slno'],
            'generallaborer' => ['table' => 'generallaborer', 'id_field' => 'slno'],
            'mason' => ['table' => 'mason', 'id_field' => 'slno'],
            'plumber' => ['table' => 'plumber', 'id_field' => 'slno'],
            'securityguard' => ['table' => 'securityguard', 'id_field' => 'slno'],
            'sitesupervisor' => ['table' => 'sitesupervisor', 'id_field' => 'slno'],
            'truckdriver' => ['table' => 'truckdriver', 'id_field' => 'slno'],
            'welder' => ['table' => 'welder', 'id_field' => 'slno']
        ];

        $authenticated = false;

        // Check each role table until we find a match
        foreach ($role_tables as $role => $config) {
            $stmt = $conn->prepare("SELECT {$config['id_field']}, name, email, password, status FROM {$config['table']} WHERE email = ?");
            $stmt->bind_param("s", $email);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows === 1) {
                $user = $result->fetch_assoc();
                
                // Compare passwords (plain text comparison)
                if ($password === $user['password']) {
                    // Check if account is active
                 //   if ($user['status'] === 'Inactive') {
                     //   $response['message'] = 'Your account is inactive';
                       // echo json_encode($response);
                        //exit();
                    //}
                    
                    // Set session variables
                    $_SESSION['user_id'] = $user[$config['id_field']];
                    $_SESSION['user_email'] = $user['email'];
                    $_SESSION['user_name'] = $user['name'];
                    $_SESSION['user_role'] = $role;
                    
                    $response['success'] = true;
                    $response['message'] = 'Login successful';
                    $response['role'] = $role;
                    $authenticated = true;
                    break;
                }
            }
            $stmt->close();
        }
    
        if (!$authenticated) {
            $response['message'] = 'Invalid email or password';
        }

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