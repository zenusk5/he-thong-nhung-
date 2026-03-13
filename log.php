<?php
$conn = new mysqli("localhost","iot","123456","smart_home");

$q = $conn->query("SELECT * FROM rfid_logs ORDER BY id DESC LIMIT 20");

echo "<table>";
echo "<tr><th>ID</th><th>UID</th><th>KET QUA</th><th>THOI GIAN</th></tr>";

while($row = $q->fetch_assoc()){
    echo "<tr>";
    echo "<td>".$row['id']."</td>";
    echo "<td>".$row['rfid_uid']."</td>";
    echo "<td>".$row['result']."</td>";
    echo "<td>".$row['time']."</td>";
    echo "</tr>";
}

echo "</table>";
