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
la logica è la seguente:

1. ti crei la tua immagine dove installi tutto il software che vuoi attraverso la creazione di un dockerfile di cui dovrebbe esserci un template/guida/dummy esempio proprio nella guida alla sezione "Make a custom image"

2. questa operazione la puoi fare ovunque anche sul tuo laptop.

3. quando l'immagine è buildata e ne hai fatto l'upload i.e. su dockerhub

4. nel form del jupytehub di cygno basta che metti quel nome al posto del default.

5. se vuoi rendere il nome:tag di quell'immagine disponibile nel menu' devi fare una operazione manuale di cui pensavo avessi già creato le istruzioni ma non è cosi' lo faccio e le aggiungo al link di cui sopra.

questo dovrebbe darti idea della logica.. e i dettagli sono nel link.
