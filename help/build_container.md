go to test notebook (192.135.24.159)
  - sudo su
  - cd dodas-docker-images/docker/CYGNO/
  - edit and update the Dockerfile in the imege folder (lab, wn, tape)
  - cd dodas-docker-images/docker/CYGNO/
  - docker build -t gmazzitelli/cygno-XXX:vX.Y.Z-cygno -f XXX/Dockerfile .

example:
```
docker build -t gmazzitelli/cygno-wn:v1.0.20-cygno -f wn/Dockerfile .
docker push gmazzitelli/cygno-wn:v1.0.20-cygno
```
