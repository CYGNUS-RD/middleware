<?php
//
// script per la gestione di variabili e allarmi
// http://www.lnf.infn.it/~mazzitel/php/vardb.php restituisce una tabella html dei dati salvati
// http://www.lnf.infn.it/~mazzitel/php/vardb.php?name=&value=&style= etc.. imposta i paramteri
// sms parametro speciale perche invia anche un sms a me
// 0 ok, 1 errore
//

$update_time = date("Y-m-d H:i:s");   
$ip = getenv ("REMOTE_ADDR");
$to = "giovanni.mazzitelli@lnf.infn.it";	
$headers = "From: giovanni.mazzitelli@lnf.infn.it";
$subject = "message:";
$value="$value, ip: $ip ##";
mail($to, $subject, $value, $headers);

?>

