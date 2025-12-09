### cvmfs client per siti CERN e INFN

- per far patire il docker a mano:
- per produzione WP1
- ```docker run -it --rm -d --privileged=True --device /dev/fuse  --cap-add SYS_ADMIN --volume /data/jupyter-mounts/cvmfs/:/cvmfs:shared --restart=unless-stopped --log-driver local -e REPO_LIST='sft.cern.ch datacloud.infn.it sft-cygno.infn.it' --log-opt max-size=100m --log-opt max-file=5 --name cvmfs gmazzitelli/cvmfs-client:wp1-0.1```
- per WP6 R&D
- ```docker run -it --rm -d --privileged=True --device /dev/fuse  --cap-add SYS_ADMIN --volume /data/jupyter-mounts/cvmfs/:/cvmfs:shared --restart=unless-stopped --log-driver local -e REPO_LIST='sft.cern.ch datacloud.infn.it sft-cygno.infn.it' --log-opt max-size=100m --log-opt max-file=5 --name cvmfs gmazzitelli/cvmfs-client:wp6-0.1```
- e poi ```docker attach -it cvmfs```
- user help: [https://github.com/CYGNUS-RD/middleware/blob/master/help/cvmfs_config.md](https://github.com/CYGNUS-RD/middleware/blob/master/help/cvmfs_config.md)
