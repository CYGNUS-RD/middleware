<?php
 
require_once('/var/simplesamlphp/lib/_autoload.php');
$as = new SimpleSAML_Auth_Simple('default-sp');
if ( $as->isAuthenticated() && $_REQUEST['logout'] ) {
  $as->logout();
}
 
if ( !$as->isAuthenticated() && $_REQUEST['login'] ) {
  $as->requireAuth();
}
 
 
echo "Hello World!\n";
 
if ( $as->isAuthenticated() ) { 
  echo "You are authenticated<br>\n";
 
  $attr = $as->getAttributes();
 
  echo "<pre>";
  print_r( $attr );
  echo "</pre>";
 
}
 
 
?>
<br>
<a href="?login=yes">LOGIN</a><br>
<a href="?logout=yes">LOGOUT</a><br>
