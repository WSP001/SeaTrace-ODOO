<?php
/**
 * Status Ping - Simple API health check
 * Returns: "Operational ✅" or "Degraded ⚠️"
 */

// Simulate 90% uptime for demo
$operational = (rand(0, 9) > 0);

header('Content-Type: text/plain');
header('Cache-Control: no-cache, no-store, must-revalidate');
header('Pragma: no-cache');
header('Expires: 0');

echo $operational ? "Operational ✅" : "Degraded ⚠️";
