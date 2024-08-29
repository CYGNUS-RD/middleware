```
docker build -t gmazzitelli/myubuntu .
docker push gmazzitelli/myubuntu
docker run -d -v ${PWD}/dev/:/root/dev/ --name myubuntu --net="host" gmazzitelli/myubuntu sleep infinity
```
