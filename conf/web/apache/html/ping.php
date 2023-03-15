<?php
 $endpoints = array('notebook01.cygno.cloud.infn.it','notebook02.cygno.cloud.infn.it','131.154.96.221','131.154.96.196','10.0.0.5');
 foreach ($endpoints as $endpoint) {
      $session = snmp2_get($endpoint, 'pubblic', "system.SysContact.0");
      var_dump($session->getError());
      // do something with the $session->getError() if it exists else, endpoint is up
 }
 ?>
