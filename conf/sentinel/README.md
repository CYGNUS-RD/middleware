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
    

# How to update the reconstruction folder with new repository on the Sentinel:

#### **1. Initial Setup for Sentinel**

1. Switch to superuser:
   ```bash
   sudo su
   ```

2. Navigate to the Sentinel directory:
   ```bash
   cd /middleware/conf/sentinel/
   ```

3. Drain the Sentinel 1 in the `docker-compose.yaml` file as per instructions.

4. Start the container:
   ```bash
   docker compose up -d
   ```

#### **2. Modifying the Reconstruction Directory**

5. Navigate to the `/dev` directory:
   ```bash
   cd /dev
   ```

6. Rename the existing reconstruction directory:
   ```bash
   mv reconstruction reconstruction_toberemoved
   ```

7. Clone the reconstruction repository (specific repository URL not mentioned, but use this command with the repository link):
   ```bash
   git clone https://github.com/CYGNUS-RD/reconstruction.git
   ```

#### **3. Cythonize Setup within the Docker Container**

8. Enter the Sentinel Docker container:
   ```bash
   docker exec -it sentinel1 bash
   ```

9. Navigate to the reconstruction directory:
   ```bash
   cd dev/reconstruction
   ```

10. Run the `cythonize.sh` script:
   ```bash
   source cythonize.sh
   ```

11. Exit the Docker bash shell:
   ```bash
   exit
   ```

12. Change the permissions for the reconstruction directory:
   ```bash
   chmod -R 777 reconstruction
   ```

#### **4. Final Steps for Reconstruction Setup**

13. Navigate back to the `/dev` directory:
   ```bash
   cd /dev
   ```

14. Copy the `exec_reco.sh` script from the old directory to the new one:
   ```bash
   cp reconstruction_toberemoved/exec_reco.sh reconstruction/
   ```

15. Ensure the parameters are correct by comparing them (e.g., using `diff`):
   ```bash
   diff -r reconstruction_toberemoved/ reconstruction/
   ```

#### **5. Completing the Process**

16. After verifying the parameters, remove the drain from Sentinel 1 in the `docker-compose.yaml` file.

17. Start the container again:
   ```bash
   docker compose up -d
   ```

This guide walks through the full process, from setting up Sentinel, modifying reconstruction files, to handling Cythonization and executing the final steps.
