# middleware

* ODB INFO: [http://lmu.web.psi.ch/docu/manuals/bulk_manuals/software/midas195/html/ODB_Structure.html#ODB_System_Tree](http://lmu.web.psi.ch/docu/manuals/bulk_manuals/software/midas195/html/ODB_Structure.html#ODB_System_Tree)
* LIB INFO: [https://bitbucket.org/tmidas/midas/src/develop/python/](https://bitbucket.org/tmidas/midas/src/develop/python/)
* SSH LNGS: `ssh -p 9023 standard@172.16.10.83 `
* SSH LNF: `ssh -p 9023 standard@spaip.lnf.infn.it` (`ssh -X cygno@spaip.lnf.infn.it -p 9022`)
* CONF: ...
* JUPYTER LNF:  http://spaip.lnf.infn.it:8888/ (not in autostart: `nohup jupyter notebook --no-browser&` )
* JUPYTER LNGS: http://172.16.10.83:8888/

jupyter configuration
```
sudo chmod 777 /home/software/root_build/etc/notebook/jupyter_notebook_config.py
sudo chmod 777 /home/software/root_build/etc/notebook/
```
first config 
```
jupyter notebook --generate-config
c.NotebookApp.allow_origin = '*'
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.password = <password>
```

python setup:

```
pip install testresources
pip install root_numpy
pip install sklearn
pip install Cython
pip install notebook
pip install mysql-connector
pip install git+https://github.com/DODAS-TS/boto3sts
pip install git+https://github.com/CYGNUS-RD/cygno.git
export PYTHONPATH=$PYTHONPATH:$MIDASSYS/python (to set in bashrc/DAQsetup)
sudo pip install -e $MIDASSYS/python --user
```

in middeleware setup for cygno cytron
```
sudo apt-get install python-numpy
cython cython_cygno.pyx
cythonize -a -i cython_cygno.pyx
```

cloud token https://github.com/CYGNUS-RD/cygno; http://repo.data.kit.edu/ (if repository unreachble eg ubunto 20.04)
```
sudo apt-key adv --keyserver hkp://pgp.surfnet.nl --recv-keys ACDFB08FDC962044D87FF00B512839863D487A87
vi /etc/apt/sources.list
```
add
```
deb https://repo.data.kit.edu/ubuntu/20.04 ./
sudo apt-get install oidc-agent
```

