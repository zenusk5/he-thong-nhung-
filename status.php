<?php
header('Content-Type: application/json');

$conn = new mysqli("localhost","iot","123456","smart_home");

$data = [
    "mode" => "AUTO",
    "door" => "CLOSE",
    "light" => "OFF",
    "rain" => "KHO"
];

$q = $conn->query("SELECT type,status FROM devices");

while($row = $q->fetch_assoc()){
    if($row['type']=="servo") $data['door']=$row['status'];
    if($row['type']=="light") $data['light']=$row['status'];
    if($row['type']=="rain")  $data['rain']=$row['status'];
}

$q2 = $conn->query("SELECT mode FROM system LIMIT 1");
if($row2 = $q2->fetch_assoc()){
    $data['mode']=$row2['mode'];
}

echo json_encode($data);
