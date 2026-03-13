<?php
$conn = new mysqli("localhost","iot","123456","smart_home");

$type = $_GET['type'];
$value = $_GET['value'];

if($type == "mode"){
    $conn->query("UPDATE system SET mode='$value'");
}else{
    $conn->query("UPDATE devices SET status='$value' WHERE type='$type'");
}
