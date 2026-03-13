<?php
$conn = new mysqli("localhost","iot","123456","smart_home");
$conn->query("UPDATE system SET mode='MANUAL'");
