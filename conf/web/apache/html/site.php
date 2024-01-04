<?

# Configure this to access different site DB and Facility
$site = "LNGS";
$debug = True;

# MySQL connection info  

$username = "cygno_producer";
$password = getenv('MYSQL_PASSWORD');

$dbname   = "cygno_db";
$db_port  = '6033';

# Home web page
$web = "https://web.infn.it/cygnus/";

if($site=="lnf"){
   $servername = "131.154.96.196";
}else{
   $servername = "131.154.96.221";
}

$baseurl = "https://131.154.97.187/";

// echo ">".$servername." ".$username." ".$password." ".$dbname." ".$db_port;
// // Create connection
// $connID = new mysqli($servername, $username, $password, $dbname, $db_port);
// // Check connection
// if ($conn->connect_error) {
//   die("Connection failed: " . $conn->connect_error);
// }

###########################################################################
# DON'T TOUCH BELOW THIS LINE !!! #########################################
###########################################################################
# ERRORS HANDLING #########################################################
###########################################################################

ini_set ( 'error_reporting',  E_ALL );
ini_set ( 'log_errors',         1 );

function userErrorHandler( $errno, $errmsg, $filename, $linenum, $vars ) {

   if ( $errno === E_NOTICE ) {
#     echo "$filename:$linenum: $errmsg<br>\n";
     return;
   }

   $errortype = array (
               E_ERROR          => "Error",
               E_WARNING        => "Warning",
               E_PARSE          => "Parsing Error",
               E_CORE_ERROR      => "Core Error",
               E_CORE_WARNING    => "Core Warning",
               E_COMPILE_ERROR  => "Compile Error",
               E_COMPILE_WARNING => "Compile Warning",
               E_USER_ERROR      => "User Error",
               E_USER_WARNING    => "User Warning",
               E_USER_NOTICE    => "User Notice",
               E_STRICT          => "Runtime Notice"
               );

   $err = "<b>An error has occurred\n";
   $err .= "Please contact your system Administrator sending this report:</b>\n";
   $err .= "------------------------------------------------------------------\n";
   $err .= "Datetime:       ".date("Y-m-d H:i:s (T)")."$dt\n";
   $err .= "Errornum:       $errno\n";
   $err .= "Errortype:      $errortype[$errno]\n";
   $err .= "Errormsg:       $errmsg\n";
   $err .= "Scriptname:     $filename\n";
   $err .= "Scriptlinenum:  $linenum\n";
   $err .= "------------------------------------------------------------------\n";

   echo "<pre style='font-family: courier; font-size: 14; color: #DD0000; text-align: left;'>$err</pre>\n";
   flush(); ob_flush();
   flush(); ob_flush();
   flush(); ob_flush();

   exit;

}
set_error_handler("userErrorHandler");

//###########################################################################


?>
