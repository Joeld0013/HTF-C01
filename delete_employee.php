<?php
include 'dbconnect.php';

$slno = $_POST['slno'];
$roleId = $_POST['role'];  // roleId like electrician, plumber etc.

$sql = "DELETE FROM `$roleId` WHERE slno = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("i", $slno);
$stmt->execute();

if ($stmt->affected_rows > 0) {
    echo "Deleted successfully";
} else {
    echo "Failed to delete";
}

$stmt->close();
$conn->close();
?>
