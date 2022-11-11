### develop/test folder

* example stand alone sensor reading/plot [readEnvTsensor.ipynb](./readEnvTsensor.ipynb)
* example and test of MIDAS ODB access form Jupyter [readMidasODB.ipynb](./readMidasODB.ipynb)

command line 

    ~/DAQ/middleware/dev$ source setup.sh
    

### da ricordare

    run=03397; cp daq_stored.log bck/ ; grep -v $run bck/daq_stored.log  > daq_stored.log

vedi file copyupload.sh che copia da una nummero all'altro ed eventualmnte elimina dai log
