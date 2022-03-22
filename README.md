# middleware

* ODB [http://lmu.web.psi.ch/docu/manuals/bulk_manuals/software/midas195/html/ODB_Structure.html#ODB_System_Tree](http://lmu.web.psi.ch/docu/manuals/bulk_manuals/software/midas195/html/ODB_Structure.html#ODB_System_Tree)
* LIB [https://bitbucket.org/tmidas/midas/src/develop/python/](https://bitbucket.org/tmidas/midas/src/develop/python/)
* SSH LNGS: `ssh -p 9023 standard@172.16.10.83 `
* SSH LNF: `ssh -p 9023 standard@spaip.lnf.infn.it` (`ssh -X cygno@spaip.lnf.infn.it -p 9022`)
* CONF: source /home/cygno/DAQ/middleware/dev/setup.sh
* JUPYTER:  http://spaip.lnf.infn.it:8888/ ( to start: nohup jupyter notebook --no-browser& ; first config jupyter notebook --generate-config;  c.NotebookApp.allow_origin = '*'; c.NotebookApp.ip = '0.0.0.0' and set c.NotebookApp.password)

```
pip install testresources
pip install root_numpy
pip install sklearn
pip install Cython
pip install notebook
pip install mysql-connector
pip install git+https://github.com/DODAS-TS/boto3sts
pip install git+https://github.com/CYGNUS-RD/cygno.git
export PYTHONPATH=$PYTHONPATH:$MIDASSYS/python
sudo pip install -e $MIDASSYS/python --user
sudo apt-get install python-numpy
cython cython_cygno.pyx
cythonize -a -i cython_cygno.pyx
```
