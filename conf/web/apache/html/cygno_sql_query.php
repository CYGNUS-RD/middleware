<?php

$username = getenv('MYSQL_USER');
$password = getenv('MYSQL_PASSWORD');

$site = array_key_exists( 'site' , $_GET ) ? $_GET['site'] : '' ;
$db = array_key_exists( 'db' , $_GET ) ? $_GET['db'] : 'Runlog' ;
$run = array_key_exists( 'run' , $_GET ) ? $_GET['run'] : '' ;
$table = array_key_exists( 'table' , $_GET ) ? $_GET['table'] : '' ;
$start = array_key_exists( 'start' , $_GET ) ? $_GET['start'] : '' ;
$end = array_key_exists( 'end' , $_GET ) ? $_GET['end'] : '' ;


#
# Update for lnf/mango 1/2/24 and run limits
# G. Mazzitelli
#

if($site=="lnf" || $site=="LNF"){
   $servername = "grafana.cygno.cloud.infn.it";
   $dbname   = getenv('MYSQL_DATABASE');
   $db_port  = '6033';
}
elseif($site=="man" || $site=="MAN"){
   $servername = "grafana.cygno.cloud.infn.it";
   $dbname   = "mango_db";
   $db_port  = '6034';

}else{
   $servername = "sql.cygno.cloud.infn.it";
   $dbname   = getenv('MYSQL_DATABASE');
   $db_port  = '6033';
}


$header = "<!DOCTYPE html>
<html>
	<head>
		<meta charset=\'utf-8\'>
		<title>Page Title</title>
		<style>
		table {
			border-collapse: collapse;
		    font-family: Tahoma, Geneva, sans-serif;
		}
		table td {
			padding: 15px;
		}
		table thead td {
			background-color: #54585d;
			color: #ffffff;
			font-weight: bold;
			font-size: 13px;
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
			background-color: #ffffff;
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
            $html .= '<th>' . htmlspecialchars($key) . '</th>';
        }
    $html .= '</tr>';

    // data rows
    foreach( $array as $key=>$value){
        $html .= '<tr>';
        foreach($value as $key2=>$value2){
            $html .= '<td>' . htmlspecialchars($value2) . '</td>';
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

// debug
// print("site: ".$site." db: ".$db." run: ".$run." table: ".$table." start: ".$start." end: ".$end."<br>");

if($run) {
	$ip = getenv ("REMOTE_ADDR");
	$sql = "SELECT * FROM `".$db."` WHERE `run_number` =  $run";
	$result = $conn->query($sql);
	$row = $result->fetch_assoc();
//	echo "<br>".$row['Run number']." ". $row['RunDescription']. "<br>";
//	print_r($row);
	print json_encode($row);
    
}else{

    if($start && $end) {
	     $sql = "SELECT * FROM `".$db."` WHERE `run_number` >=  $start AND `run_number` < $end";
	}else{
	     $sql = "SELECT * FROM `".$db."`";
	}
#	print($sql);
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
