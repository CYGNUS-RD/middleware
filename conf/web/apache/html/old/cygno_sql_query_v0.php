<?php

$username = "cygno_producer";
$password = getenv('MYSQL_PASSWORD');

$dbname   = "cygno_db";
$db_port  = '6033';
$site = array_key_exists( 'site' , $_GET ) ? $_GET['site'] : '' ;
$db = array_key_exists( 'db' , $_GET ) ? $_GET['db'] : '' ;
$run = array_key_exists( 'run' , $_GET ) ? $_GET['run'] : '' ;
$table = array_key_exists( 'table' , $_GET ) ? $_GET['table'] : '' ;
#$offset = array_key_exists( 'offset' , $_POST ) ? $_POST['offset'] : '1' ;
#$limit = array_key_exists( 'limit' , $_POST ) ? $_POST['limit'] : '10' ;
if($site=="lnf"){
   $servername = "131.154.96.196";
}else{
   $servername = "131.154.96.221";
}


$header = "<!DOCTYPE html>
            <html>
                <head>
                    <meta charset=\'utf-8\'>
                    <title>CYGNO DB</title>
                    <style>
                    table {
                        border-collapse: collapse;
                        font-family: Tahoma, Geneva, sans-serif;
                    }
                    table td {
                        padding: 9px;
                    }
                    table thead td {
                        background-color: #54585d;
                        color: #FFFFFF;
                        font-weight: bold;
                        font-size: 9px;
                        border: 1px solid #54585d;
                    }
                    table tbody td {
                        color: #636363;
                        border: 1px solid #dddfe1;
                    }
                    table tbody tr {
                        background-color: #f9fafb;
                    }
                    table tbody tr:nth-child(odd) {
                        background-color: #FFFFFF;
                    }
                    </style>
                </head>
                <body>";
    
$footer = "</body></html>";

function build_table($array){
    // start table
    $html = '<table>';
    // header row
    $html .= '<tr>';
    foreach($array[0] as $key=>$value){
        
            $html .= '<th colspan=1 bgcolor=#AA0000><font color=#FFFFFF size=> ' . str_replace("_", " ", htmlspecialchars($key ?? '')) . '</th>';
        }
    $html .= '</tr>';

    // data rows
    foreach( $array as $key=>$value){
        $html .= '<tr>';
        foreach($value as $key2=>$value2){
            $html .= '<td>' . htmlspecialchars($value2 ?? '') . '</td>';
        }
        $html .= '</tr>';
    }

    // finish table and return it

    $html .= '</table>';
    return $html;
}


/**
 * Workaround for PHP < 5.1.6
 */
if (!function_exists('json_encode')) {
    function json_encode($data) {
        switch ($type = gettype($data)) {
            case 'NULL':
                return 'null';
            case 'boolean':
                return ($data ? 'true' : 'false');
            case 'integer':
            case 'double':
            case 'float':
                return $data;
            case 'string':
                return '"' . addslashes($data) . '"';
            case 'object':
                $data = get_object_vars($data);
            case 'array':
                $output_index_count = 0;
                $output_indexed = array();
                $output_associative = array();
                foreach ($data as $key => $value) {
                    $output_indexed[] = json_encode($value);
                    $output_associative[] = json_encode($key) . ':' . json_encode($value);
                    if ($output_index_count !== NULL && $output_index_count++ !== $key) {
                        $output_index_count = NULL;
                    }
                }
                if ($output_index_count !== NULL) {
                    return '[' . implode(',', $output_indexed) . ']';
                } else {
                    return '{' . implode(',', $output_associative) . '}';
                }
            default:
                return ''; // Not supported
        }
    }
}


// Create connection
$conn = new mysqli($servername, $username, $password, $dbname, $db_port);
// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
if ($db=="old") {
   $db_table = "RunCatalogLNF";
}else{
   $db_table = "Runlog";
}
# print($db_table);
if($run) {
    $ip = getenv ("REMOTE_ADDR");
//	$sql = "SELECT * FROM `RunCatalogLNF` WHERE `Run number` = $run";
//	$sql = "SELECT * FROM `Runlog` WHERE `run_number` =  $run";
    $sql = "SELECT * FROM `".$db_table."` WHERE `run_number` =  $run";
    $result = $conn->query($sql);
    $row = $result->fetch_assoc();
//	echo "<br>".$row['Run number']." ". $row['RunDescription']. "<br>";
//	print_r($row);
    print json_encode($row);
    
}else{

    $sql = "SELECT * FROM `".$db_table."`";
    $oderby = "run_number";
    // $limit = 10;
    // $offset = 1;
    $sql .= " ORDER BY `".$oderby."` DESC LIMIT ".$limit." OFFSET ".$offset." ";
    print($sql);
    $result = $conn->query($sql);
    $mytable = array();
    $out = "";
    if ($result->num_rows > 0) {
          // print("[ ");
        $out .= "[ ";
              // output data of each row
        while($row = $result->fetch_assoc()) {
           if ($table) {
                $mytable[] = $row;
            }
            // print(json_encode($row));
            $out .= json_encode($row);
            $out .= ",";
            // print(",");
        }
        $out = mb_substr($out ,0, -1);
        $out .= " ]";
        // print(" ]");
        if ($table) {
            echo $header;
            echo build_table($mytable);
            echo $footer;
        }else{
            print($out);
        }
    }

}
$conn->close();
?>

<table border="0" cellspacing="3" cellpadding="3">
<tr>
<td>
<form action="" method="post">
<?
foreach( $_POST as $k => $v )
{ ?>
  <input type="hidden" name="<?=$k?>" value="<?=$v?>">	
  <? }
?>
<input type="hidden" name="start" value="0">
<input type="submit" name="page" value="<<">
</form>
</td>
<td><form action="" method="post">
<?
foreach( $_POST as $k => $v )
{ ?>
  <input type="hidden" name="<?=$k?>" value="<?=$v?>">
  <? }
?>
<input type="hidden" name="start" value="<?=($start-$delta)?>">
<input type="submit" name="page" value="prev">
</form></td>
<td><form action="" method="post">
<?
foreach( $_POST as $k => $v )
{ ?>
  <input type="hidden" name="<?=$k?>" value="<?=$v?>">
  <? }

$next = $start+$delta ;
if( $next > $tot_rows ) $next = $tot_rows-($tot_rows%$delta) ;
?>
<input type="hidden" name="start" value="<?=($next)?>">
<input type="submit" name="page" value="next">
</form></td>
<td><form action="" method="post">
<?
foreach( $_POST as $k => $v )
{ ?>
  <input type="hidden" name="<?=$k?>" value="<?=$v?>">
  <? }
?>
<input type="hidden" name="start" value="<?=($tot_rows-($tot_rows%$delta))?>">
<input type="submit" name="page" value=">>">
</form></td>

</tr></table>

<form method="post">
<table border="0" cellspacing="1" cellpadding="1">
<tr>
<td><b>Find by date</b></td>
<td>
<?
if( $_POST['data_g'] == "" ) $_POST['data_g'] = date("d") ;
if( $_POST['data_m'] == "" ) $_POST['data_m'] = date("m") ;
if( $_POST['data_a'] == "" ) $_POST['data_a'] = date("Y") ;
?>
<select name="data_a" id="data_a">
<option value="" selected="selected"></option>
<?
for( $i=2005 ; $i<=date("Y") ; ++$i )
{
  ?><option value="<?=$i?>" <?=($i==$_POST['data_a'])?"selected=\"selected\"":""?>><?=$i?></option><?
}
?>
</select>
<select name="data_m" id="data_m">
<option value="" selected="selected"></option>
<?
for( $i=1 ; $i<=12 ; ++$i )
{
  ?><option value="<?="0$i"?>" <?=($i==$_POST['data_m'])?"selected=\"selected\"":""?>><?=$i?></option><?
}
?>
</select>
<select name="data_g" id="data_g">
<option value="" selected="selected"></option>
<?
for( $i=1 ; $i<=31 ; ++$i )
{
  ?><option value="<?="0$i"?>" <?=($i==$_POST['data_g'])?"selected=\"selected\"":""?>><?=$i?></option><?
}
?>
</select>
</td>
<td><input name="invia" type="submit" id="invia" value="Go"></td>
<!-- </tr>
</table> -->
</form>
<form method="post">
<!-- <table border="0" cellspacing="3" cellpadding="3"> 
<tr> -->
<td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
<td><b>Find by description</b></td>
<td><input name="service" type="text" id="service" value="<?=$_POST['service']?>"></td>
</tr><tr><td>&nbsp</td><td>&nbsp</td><td>&nbsp</td><td>&nbsp</td>
<td>Include Open Comment <input type="checkbox" name="scom" checked></td>
<td><input name="invia" type="submit" id="invia" value="Go"></td>

</tr>
</table>
</form>
<form>
<table><tr>&nbsp;</tr><td><input type=submit value='Reset List'></td></table>
</form>