* check value of HV in the page GEM HV
![GEM](https://github.com/CYGNUS-RD/middleware/blob/master/daq/gem.png)
* set the right value (deafult set in the picture)
* check in program that everything is runing
![PROGRAM](https://github.com/CYGNUS-RD/middleware/blob/master/daq/program.png)
* check ODB --> Configuration the exposure and freRunning flag
![GEM](https://github.com/CYGNUS-RD/middleware/blob/master/daq/config.png)
* controll Status of the run and stop it
![RUN](https://github.com/CYGNUS-RD/middleware/blob/master/daq/run.png)
* check/switch in ODB --> Logger [write date] y by clinking on the value e switcing between [y/n]
![RUN](https://github.com/CYGNUS-RD/middleware/blob/master/daq/logger.png)
* start the run and acquire data until reache the numebr of event you need
* open a terminal (or use one already open) and copy data on cloud
```
cygno_repo put cygno-data runXXXXX.mid.gz -t STD -s infncloud-wlcg
example
cygno_repo put cygno-data run00030.mid.gz -t STD -s infncloud-wlcg
```
