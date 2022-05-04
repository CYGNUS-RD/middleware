# info

### MIDAS ODB
* https://midas.triumf.ca/MidasWiki/index.php/Python
* http://lmu.web.psi.ch/docu/manuals/bulk_manuals/software/midas195/html/ODB_Structure.html#ODB_System_Tree


## Tools

### start notebook

    nohup jupyter notebook --no-browser --port=8888 > jupyter.log 2>&1 &

### config jupyter

    nano /usr/local/root_install/etc/notebook/jupyter_notebook_config.py

### cloud jupyter container
* https://confluence.infn.it/pages/viewpage.action?spaceKey=INFNCLOUD&title=Estenzione+e+Customizzazione+immagini+docker+CYGNO
* fare un frok del progetto sul proprio github e poi un clone in locale
* creata una directory sotto CYGNO detta custom
* in questa dierectory fatto il un Docker che parte dall'utlima realse (ESEMPIO DI Dockerfile CHE aggiunra solo le cygno lib)
```
#FROM dodasts/cygno-lab:<latest release> -> for example:
FROM dodasts/cygno-lab:v1.0.13-cygno

RUN pip3 install --no-cache-dir -U git+https://github.com/CYGNUS-RD/cygno.git
```
* quando l'immagine è buildata e ne hai fatto l'upload i.e. su dockerhub (modificare la tag)
```
docker build -t gmazzitelli/cygno-lab:v1.0.13-cygno /Users/mazzitel/cygno_dev/dodas-docker-images/docker/CYGNO/custom/
docker push gmazzitelli/cygno-hub:v1.0.13-cygno
```
* andare sulla VM e 
``` 
cd /usr/local/share/dodasts/jupyterhub
sudo docker-compose down
sudo vim docker-compose.yaml (mettere la nuova tag)
sudo  docker-compose up -d --build
``` 
