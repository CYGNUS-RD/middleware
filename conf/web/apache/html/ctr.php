<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

<head>

<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="refresh" content="60" />
<title>CTRL Station</title>
<style type="text/css">
<!--
BODY {color:#4F473D;font-family:Verdana,sans-serif;font-weight:bold;margin:2px;padding:2px;}
    .main {width:755px;margin:0 auto;}
    .hdr {float:left;width:440px;word-wrap:break-word;overflow:auto;}
    .tme {float:right;padding-top:30px;margin-right:8px;font-size:70%;text-align:right;}
    .tmb {margin-top:20px;text-align:center;font-size:80%;}
    .tmb a {text-decoration:underline;color:#4F473D;}
        .tile {height:150px;width:200px;float:left;margin-bottom:4px;margin-left:4px;padding-left:10px;color:#FFFFFF;background:#429BC3;}
        .tile:hover,.tile2:hover {background:#D0E5FA;color:#4F473D;}
            .small {width:93px;}
            .tile2 {height:304px;width:414px;float:left;margin-bottom:4px;margin-left:4px;padding-left:10px;color:#FFFFFF;background:#429BC3;}
                .high1,.low1 {background:#F08080;}
                .high1:hover,.low1:hover {background:#FAACAC;}
                    .none0,.none0:hover {background:#F2F2F2;}
                        .none1 {background:#429BC3;}
                            .t1 {font-size:95%;margin-top:10px;display:block;}
                            .t2 {font-size:160%;margin-top:25px;display:block;}
                            .t3 {font-size:110%;margin-top:-2px;display:block;}
                            .t4 {font-size:300%;margin-top:25px;margin-left:-10px;text-align:center;display:block;}
                            .t5 {font-size:80%;margin-top:-22px;margin-left:4px;margin-bottom:10px;display:block;}
                            .t6 {font-size:180%;margin-top:10px;display:block;}
                            .t7 {font-size:320%;margin-top:25px;display:block;}
                            .t8 {font-size:210%;margin-top:-2px;display:block;}
                            .t9 {font-size:130%;margin-top:25px;display:block;}
                            h1 {font-size:180%;}
                            A {text-decoration:none;}
                            .clear {clear:both;}
                        .none2 {background:#AD1836;}
                                .t1 {font-size:95%;margin-top:10px;display:block;}
                                .t2 {font-size:160%;margin-top:25px;display:block;}
                                .t3 {font-size:110%;margin-top:-2px;display:block;}
                                .t4 {font-size:300%;margin-top:25px;margin-left:-10px;text-align:center;display:block;}
                                .t5 {font-size:80%;margin-top:-22px;margin-left:4px;margin-bottom:10px;display:block;}
                                .t6 {font-size:180%;margin-top:10px;display:block;}
                                .t7 {font-size:320%;margin-top:25px;display:block;}
                                .t8 {font-size:210%;margin-top:-2px;display:block;}
                                .t9 {font-size:130%;margin-top:25px;display:block;}
                                h1 {font-size:180%;}
                            -->
                            </style>
                            
                            </head>
                            
                            <body onload="init();">
                            <div class="main">
                            <?php
                                $cmd = "uname -a | awk '{print $2}'";
                                exec( $cmd, $name);
                                $dovea=explode("-", $name[0]);
                                $dove=$dovea[0];
                            # $wwwhome="https://gmazzitelli.noip.me:6400";
                                $wwwhome=".";
                                $cmd= 'tail -1 /var/www/html/data/sensors-campaegli-pi.txt';
                                exec($cmd, $result);
                                $datatxt = explode(" ", $result[0]);
                                if ($datatxt[4] ==  $datatxt[5]){
                                   $datatxt[4] = "-- ";
                                   $datatxt[5] = "-- ";
                                }


                            ?>
                            <div class="hdr"><h1>CTRL <?php echo $dove ?></h1><div class="t5"><?php echo "data time: $datatxt[0] $datatxt[1]"; ?></div></div>
                            <div class="tme"><span id="time">Time: <?php echo gmdate("H:i:s d-m-Y", time() + 3600*(1+date("I"))); ?></span><br /><span id="user">Logged in: <?php echo getenv ("REMOTE_USER"); ?></span></div>
                            <div class="clear"></div>
                            <div style="float:left;">
                            <?php
                               # $cmd = 'python /home/pi/controls/MPL115A2/MPL115A2.py';
                               # exec( $cmd, $result);
                               # $MPL = explode(" ", $result[0]);
                               # $cmd = 'sudo /home/pi/controls/DHT22/WDHT.sh';
                               # exec( $cmd, $result2);
                               # $DHT = explode(" ", $result2[0]);
                            ?>
                            
                                <a href="<?php echo $wwwhome; ?>/plots/plots.html" class="tile none1"><span class="t1">Temperature (In)</span><span class="t2"><?php echo $datatxt[7]; ?>&deg;C</span></a>
                                <!--<div class="tile none0"></div>-->
                                <a href="<?php echo $wwwhome; ?>/plots/plots.html" class="tile none1"><span class="t1">Relative humidity</span><span class="t2"><?php echo $datatxt[9]; ?>%RH</span></a>
                                <!--<div class="tile none0"></div>-->
                            
                            
                                <div class="clear"></div>
                            
                                <a href="<?php echo $wwwhome; ?>/plots/plots.html" class="tile none1"><span class="t1">Temperature (Out)</span><span class="t2"><?php echo $datatxt[3];?>&deg;C<br><?php echo $datatxt[4]; ?>&deg;C</span></a>
                                <!--<div class="tile none0"></div>-->
                                <a href="<?php echo $wwwhome; ?>/plots/plots.html" class="tile none1"><span class="t1">Atmospheric pressure</span><span class="t2"><?php echo $datatxt[2]; ?>hPa<br><?php echo $datatxt[8]; ?>hPa</span></a>
                                <!--<div class="tile none0"></div>-->
                            
                            
                                <div class="clear"></div>
                            <?php
                                $cmd = '/home/pi/controls/monitor.sh in';
                                exec($cmd, $varin);
                                $nvar=count($varin);
                            ?>
                            <a href="./" class="tile none1"><span class="t1" >Input:</span><?php foreach ( $varin as $v ) { ?> <span class="t1"><?php echo "--> $v"; ?></span><?php }?></a>
                            <?php
                                $cmd = 'sudo /home/pi/controls/heating.sh status';
                                exec($cmd, $varat);
                                $test=explode(" ", $varat[0]);
                                if ($test[0]=="off"){ $style="none1"; }else{ $style="none2";}
                            ?>
                                <a href="./switch.php?what=heating" onclick="return confirm('Are you sure?');" class="tile <?php echo $style ?>"><span class="t1">heating</span><span class="t2"><?php echo "$varat[0]" ?></span></a>
                                <!--div class="tile none0"></div>-->
                            
                            
                            </div>
                            
                            <div>
                                <div class="tile small none0"></div>
                                <a href="<?php echo $wwwhome; ?>/plots/" class="tile small"><span class="t1">History</span><span class="t2">plots</span><span class="t3">png</span></a>
                                <a href="<?php echo $wwwhome; ?>/data/" class="tile small"><span class="t1">History</span><span class="t2">data</span><span class="t3">txt</span></a>
                                <div class="tile small none0"></div>
				<a href="ssh://pi@<?php echo $_SERVER['SERVER_ADDR']?>" class="tile small"><span class="t1">terminal</span><span class="t2">ssh<br><?php echo $datatxt[6]; ?>&deg;C</span></a>
                                <?php
                                    $cmd = 'sudo /home/pi/controls/allarm.sh status';
                                    exec($cmd, $varal);
                                    $nvar=count($varal);
                                    if ($varal[0]=="off"){ $style="none1"; }else{ $style="none2";}
                                ?>
                            <a href="./switch.php?what=allarm" onclick="return confirm('Are you sure?');" class="tile small <?php echo $style ?>"><span class="t1">Allarm</span><span class="t2"><?php echo $varal[0]; ?></span></a>
                                <!--div class="tile small none0"></div>-->
                                <a href="http://10.9.2.6:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=root&pwd=quasimodo" class="tile small"><span class="t1">view</span><span class="t2">cam1</span></a>
				<a href="http://10.9.2.7:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=root&pwd=quasimodo" class="tile small"><span class="t1">view</span><span class="t2">cam2</span></a>
                                <a href="http://10.9.2.8:88/cgi-bin/CGIProxy.fcgi?cmd=snapPicture2&usr=root&pwd=quasimodo" class="tile small"><span class="t1">view</span><span class="t2">cam3</span></a>
                            </div>
                            
                            <?php
                                $cmd = '/home/pi/controls/monitor.sh out';
                                exec($cmd, $varout);
                                $nvar=count($varout);
                            ?>
                            <?php foreach ( $varout as $v ) { $value=explode(" ", $v); if ($value[0]!="none"){ if ($value[1]=="on"){ $style="none2"; }else{ $style="none1";} ?>
                                <a href="./switch.php?what=<?php echo $value[0] ?>" onclick="return confirm('Are you sure?');" class="tile small <?php echo $style ?>" ><span class="t1" >Output:</span><span class="t9"><?php echo "$v"; ?></span></a>
                                <?php }}?>
                            <div class="clear"></div>
                            <div class="tmb">Copyright &copy; 2015, <a href="http://giovannimazzitelli.wordpress.com/" >G. Mazzitelli.</a> All rights reserved.</div>
                            
                            </body>
                            </html>
                            
