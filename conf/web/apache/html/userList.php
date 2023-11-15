<?
require('site.php');  
require('top.php');

// require('auth.php');

echo "ciao";

if ($connID){
  $data_table = $_POST['data_table'];
  if(!$data_table){
    $data_table = 'Runlog';
  }

  if($debug){
    print ("DEBUG ----->>>>> <br>");
    foreach($_POST as $variable => $value) {
      echo "Variable Name: " . $variable . " Value: $value<br>";
    }   
    print ("<<<<<----- DEBUG <br>");
  }
  print ("<P>"); 
  

  $cerca = 0 ;
  if( $_POST['invia'] != "" ) $cerca = 1 ;
  
  if( $_POST['data_a']!="" && $_POST['data_m']!="" && $_POST['data_g']!="" )
    $data = $_POST['data_a']."-".$_POST['data_m']."-".$_POST['data_g'] ;	
  
  if( $_POST['data_a']!="" && $_POST['data_m']=="" && $_POST['data_g']=="" )
    $data = $_POST['data_a'].$_POST['data_m'].$_POST['data_g'] ;
  
  if( $_POST['data_a']!="" && $_POST['data_m']!="" && $_POST['data_g']=="" )
    $data = $_POST['data_a']."-".$_POST['data_m'].$_POST['data_g'] ;	
  
  
  if( $_POST['service'] != "" )
    $service = trim( $_POST['service'] ) ;
  
  $all = "SELECT * FROM $data_table WHERE 1 " ;
  if( $cerca && $data ) $all .= " AND OPEN_TIME LIKE '".$data."%' " ;
  if( $cerca && $service ) $all .= " AND OPEN_DESCRIPTION LIKE '%".$service."%'" ;
  if( $_POST['scom'] ) $all .= " OR OPEN_COMMENT LIKE '%".$service."%'";
  $all .= " ORDER BY IDELEMENT DESC ";
  ($query=mysql_query($all,$connID)
   or die("Non riesco ad eseguire la richiesta $all"));
  $tot_rows=mysql_num_rows($query);
  
  $all .= " LIMIT ".$start.",".$delta." " ;
  // echo "$all";
  $thequery = $all ;
  ($query=mysql_query($all,$connID)
   or die("Non riesco ad eseguire la richiesta $all"));
  
  $result = mysql_query($thequery,$connID);
  
  
?>
    <META HTTP-EQUIV="refresh" CONTENT="60;URL=userList.php">
<?
       $to = $start+$delta ;
  if( $to > $tot_rows ) $to = $tot_rows ;
  echo "<p></p><div align='center'> $tot_rows Record Found. List from $start to ".($to)."<p>";
  print ("<table border=1>");
  print ("<th>Ticket ID</th>");
  print ("<th>Open Time</th>");
  print ("<th>Description</th>");
  print ("<th>Opening Comment</th>");
  print ("<th>Close Time</th>");
  print ("<th>Elapsed Time</th>");
  print ("<th>Responsable Acknowledge</th>");
  print ("</th></tr>\n");
  while ($row = mysql_fetch_object($result)) {
    $att="";
    if ($row->NUMBER_OF_UPDATES>0) $att="<img src='/icons/small/text.gif'>";
    if ($row->RESP_CLOSE_TIME<=$row->OPEN_TIME){
      $tcolor = $thres;
      $tresprint = "--";
      if ($row->OP_CLOSE_TIME<=$row->OPEN_TIME){	
	$tcolor = $thopen;
	$tprint = "--";
      }else{
	$tprint = $row->OP_CLOSE_TIME;
      }
      $descr = preg_replace("/FAULT/", "<blink>FAULT</blink>", $row->OPEN_DESCRIPTION);
      $descr = "<a href='updateList.php?id=$row->IDELEMENT'> $descr</a>";
    }else{
      $descr = "<a href='updateList.php?id=$row->IDELEMENT'> $row->OPEN_DESCRIPTION</a>";
      $tcolor = $thclose;
      $tresprint = $row->RESP_CLOSE_TIME;
    }	
    if(preg_match("/NEWS/",  $row->OPEN_DESCRIPTION)) $tcolor = $thnews;
    print ("$tcolor $row->IDELEMENT</th>");
    print ("$tcolor $row->OPEN_TIME</th>");
    print ("$tcolor $descr $att</th>");
    print ("$tcolor $row->OPEN_COMMENT</th>");
    print ("$tcolor $tprint</th>");
    $opening = strtotime($row->OPEN_TIME);
    $closing = strtotime($row->OP_CLOSE_TIME);
    $elapsedTime=$closing - $opening;
    if($elapsedTime==0)$elapsedTime=(time() - $opening);
    $dt= t_elap($elapsedTime);
    print ("$tcolor $dt</th>");
    print ("$tcolor $tresprint</th>");
    print ("</th></tr>\n");
    
  }
} else {
  print ("Connection failed for user: $user<br>"); 
  print ("on: $host<br>\n");
} 



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
<? require('bottom.php'); ?>