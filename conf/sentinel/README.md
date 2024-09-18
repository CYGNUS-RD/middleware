# SENTINEL
HTCondor client with python env for data recostruction and file tranfer on S3 storage. 
it need a valid token in /tmp/token
```
      IAM_CLIENT_SECRET: ${IAM_CLIENT_SECRET}
      IAM_CLIENT_ID: ${IAM_CLIENT_ID}
      ENDPOINT_URL: ${ENDPOINT_URL}
      HTC_IP: XXX.XXX.XXX.XXX
```



```
docker run -e HTC_IP=XXX.XXX.XXX.XXX --env-file <( env| cut -f1 -d= ) -v /tmp:/tmp gmazzitelli/sentinel:v0.1
```


# Rebuild image

cd docker
vi Dockerfile #Change what you need
docker build -t gmazzitelli/cygno-st:v2.0.x-cygno . # x is the latest version
docker push gmazzitelli/cygno-st:v2.0.x-cygno

## Change the version on the docker-compose file and then:
docker compose up -d



# How to handle errors/crashes on the Sentinel:

Based on the conversation, here’s a step-by-step guide for managing and troubleshooting the Sentinel Docker containers.

#### **1. Accessing the Sentinel Folder**
   - Use SSH to access the Sentinel server:
     ```bash
     ssh <server_name>
     ```
   - Switch to the superuser:
     ```bash
     sudo su
     ```
   - Navigate to the Sentinel folder:
     ```bash
     cd middleware/conf/sentinel
     ```

#### **2. Checking Docker Logs**
   - To check the logs of a specific container (e.g., `sentinel1`):
     ```bash
     docker logs sentinel1
     ```
   - Alternatively, if the container has a different name:
     ```bash
     docker logs <container_name>
     ```

#### **3. Checking Active Docker Containers**
   - To see all Docker containers that are currently running:
     ```bash
     docker ps
     ```

#### **4. Viewing Log Files**
   - For detailed log monitoring, you can use the `tail` command to view the real-time logs of the algorithm (e.g., `recodf_condor_coda1.log`):
     ```bash
     tail -f -n 1000 dev/log/recodf_condor_coda1.log
     ```

#### **5. Common Problems and Solutions**

   **Problem 1: Docker Service/Process is Not Running**
   - If Docker as a service has stopped, you can check its status by running:
     ```bash
     docker ps
     ```
   - If it’s not running, restart the containers within the current folder:
     ```bash
     docker compose up -d
     ```
   - This command will start all Docker containers that are down in that directory.

   **Problem 2: Sentinel Algorithm is Stuck**
   - If the Docker service is running but the Sentinel algorithm has crashed, you will need to restart the specific container. First, check the logs for errors:
     ```bash
     tail -f dev/log/recodf_condor_coda1.log
     ```
   - If there’s an issue (often related to a token error), restart the Sentinel container:
     ```bash
     docker compose stop sentinel1
     docker compose rm sentinel1
     docker compose up -d
     ```
   - This process restarts only the `sentinel1` container.

#### **6. Restarting All Containers (Optional)**
   - If you want to bring down and restart all containers, you can do:
     ```bash
     docker compose down
     docker compose up -d
     ```
   - However, be aware that this will stop and restart **all** containers in the folder, not just Sentinel.
