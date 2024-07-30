# Rsync Dockerized Backup Solution

This project provides a Dockerized solution to perform rsync operations between two servers and automate the process using cron jobs. The setup ensures secure and automated synchronization of directories across different servers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [Create backup directories](#1-create-backup-directories)
  - [Clone the repository](#2-clone-repository) 
- [Automating with Cron](#automating-with-cron)
  - [Add rsync Jobs to crontab](#add-rsync-jobs-to-crontab)
- [Notes](#notes)

## Prerequisites

- Docker installed on backup server
- SSH access between the servers with key-based authentication

## Setup

### 1. Create backup directories
1 - Create the filesystem where the backup will be placed as `/data`;
2 - Inside the `/data` create the notebooks folder and inside the notebook the daily, weekly and monthly folder:

```
cd /data
mkdir notebook00 notebook01 notebook02
mkdir notebook00/daily notebook00/weekly notebook00/monthly
mkdir notebook01/daily notebook01/weekly notebook01/monthly
mkdir notebook02/daily notebook02/weekly notebook02/monthly
cd
```

### 2. Clone repository
Go to the machine that will serve as the backup server and run the following line:

```
git clone https://github.com/CYGNUS-RD/middleware.git
```

## Automating with Cron
### Add rsync Jobs to crontab
Move the files inside the cron_scripts directory to the /etc/cron.d/ on the backup server:

```
mv /middleware/conf/cygnoui/cron_scripts/* /etc/cron.d/
systemctl restart crond
```
## Notes

- Ensure the user setting up the cron jobs has the necessary permissions.
- Test the rsync scripts manually to verify their functionality:
  - Go to the cygnoui folder and run docker:
      ```
      cd middleware/conf/cygnoui
      docker compose up -d
      ```
  - Verify the docker logs for each notebook (00, 01 and 02):
      ```
      docker logs bkp_note00 # 01 or 02
      ```
