<?

$connID = mysql_connect($servername,$username,$password);
mysql_select_db($dbname);

$ip = getenv ("REMOTE_ADDR"); 

// $realuploaddir = realpath( $uploaddir );

$medium="2";
$smal="1";

$fgcolor1="#FFFFFF";
$bgcolor1="#AA0000";
$fgcolor2="#440000";
$fgcolor3="#3333FF";
$bgcolor2="#FFCC33";
$bgcolor3="#009900";
$bgcolor4="#666660";
$empty="#888888";
$tdh ="<th colspan=1 bgcolor=$bgcolor1><font color=$fgcolor1 size=$medium>";
$th2 ="<th colspan=2 bgcolor=$bgcolor1><font color=$fgcolor1 size=$medium>";
$th4 ="<th colspan=4 bgcolor=$bgcolor1><font color=$fgcolor1 size=$medium>";
$td1 ="<td bgcolor=$bgcolor3><font color=$fgcolor1 size=$medium>";
$td2 ="<td bgcolor=$bgcolor2><font color=$fgcolor2 size=$medium>";
$td3 ="<td bgcolor=$bgcolor2><font color=$fgcolor2 size=$medium>";
$td4 ="<td colspan=4 bgcolor=$bgcolor2><font color=$fgcolor2 size=$medium>";
$td ="<td bgcolor=$bgcolor2><font color=$fgcolor2 size=$medium>";

$thopen ="<th colspan=1 bgcolor=$bgcolor1><font color=$fgcolor1 size=$medium>";
$thres ="<th colspan=1 bgcolor=$bgcolor2><font color=$fgcolor1 size=$medium>";
$thclose ="<th colspan=1 bgcolor=$bgcolor3><font color=$fgcolor1 size=$medium>";
$thnews ="<th colspan=1 bgcolor=$bgcolor4><font color=$fgcolor1 size=$medium>";

$delta = 10 ;
$delta1 = 100;
$start = 0 ;
if( $_POST['start'] > 0 ) $start = $_POST['start'] ;


?>
