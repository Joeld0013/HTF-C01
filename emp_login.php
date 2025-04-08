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
        // Updated role tables with correct ID fields
        $role_tables = [
            'carpenter' => ['table' => 'carpenter', 'id_field' => 'carp_id'],
            'craneoperator' => ['table' => 'craneoperator', 'id_field' => 'craneop_id'],
            'electrician' => ['table' => 'electrician', 'id_field' => 'electrician_id'],
            'generallaborer' => ['table' => 'generallaborer', 'id_field' => 'laborer_id'],
            'mason' => ['table' => 'mason', 'id_field' => 'mason_id'],
            'plumber' => ['table' => 'plumber', 'id_field' => 'plum_id'],
            'securityguard' => ['table' => 'securityguard', 'id_field' => 'guard_id'],
            'sitesupervisor' => ['table' => 'sitesupervisor', 'id_field' => 'supervisor_id'],
            'truckdriver' => ['table' => 'truckdriver', 'id_field' => 'driver_id'],
            'welder' => ['table' => 'welder', 'id_field' => 'welder_id']
        ];

        $authenticated = false;

        foreach ($role_tables as $role => $config) {
            $stmt = $conn->prepare("SELECT {$config['id_field']}, name, email, password, status FROM {$config['table']} WHERE email = ?");
            $stmt->bind_param("s", $email);
            $stmt->execute();
            $result = $stmt->get_result();

            if ($result->num_rows === 1) {
                $user = $result->fetch_assoc();

                if ($password === $user['password']) {
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
