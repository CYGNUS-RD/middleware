### develop/test folder

* example stand alone sensor reading/plot [readEnvTsensor.ipynb](./readEnvTsensor.ipynb)
* example and test of MIDAS ODB access form Jupyter [readMidasODB.ipynb](./readMidasODB.ipynb)

command line 

    ~/DAQ/middleware/dev$ source setup.sh
    

### da ricordare

    run=05790; grep $run daq_converted_HIS.log; grep $run daq_stored_HIS.log
    run=05790; cp *.log bck/ ; grep -v $run bck/daq_converted_HIS.log > daq_converted_HIS.log; grep -v $run bck/daq_stored_HIS.log > daq_stored_HIS.log

vedi file copyupload.sh che copia da una nummero all'altro ed eventualmnte elimina dai log
