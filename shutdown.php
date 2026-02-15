<?php
// Trigger system shutdown
// Apache user (www-data) needs sudo permission for shutdown:
// Add to /etc/sudoers.d/blackbox:
//   www-data ALL=(ALL) NOPASSWD: /sbin/shutdown
header('Content-Type: application/json');
exec('sudo /sbin/shutdown -h now 2>&1', $output, $retval);
echo json_encode(['status' => $retval === 0 ? 'ok' : 'error', 'output' => implode("\n", $output)]);
?>
