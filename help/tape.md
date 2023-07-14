connect to tape:
  - ssh sql (131.154.96.221)
  - docker attach tape 
  - source oicd-setup.sh
  - gfal-ls davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/LNGS/
  - gfal-ls davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/LNGS/ | grep run1051
  - TO EXIT CRT-P CTR-Q

esempio:
```
  gfal-ls davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/LNGS/ > files_bck.txt
  cygno_repo put cygno-data files_bck.txt -t BCK -s infncloud-wlcg
```
