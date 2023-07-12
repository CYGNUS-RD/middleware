# How to install MariaDB and Useful links

## Installation and Configuration Maria DB

Useful links:
- [Install mariadb ubuntu 22.04](https://www.digitalocean.com/community/tutorials/how-to-install-mariadb-on-ubuntu-22-04)
- [Install and Secure Phpmyadmin Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-phpmyadmin-on-ubuntu-20-04)
- [Install PhpMyAdmin with MariaDB](https://www.server-world.info/en/note?os=Ubuntu_22.04&p=mariadb&f=6)

### Configure mysql_secure_installation

> sudo mysql_secure_installation

```
NOTE: RUNNING ALL PARTS OF THIS SCRIPT IS RECOMMENDED FOR ALL MariaDB
      SERVERS IN PRODUCTION USE!  PLEASE READ EACH STEP CAREFULLY!

In order to log into MariaDB to secure it, we'll need the current
password for the root user. If you've just installed MariaDB, and
haven't set the root password yet, you should just press enter here.

Enter current password for root (enter for none): 
OK, successfully used password, moving on...

Setting the root password or using the unix_socket ensures that nobody
can log into the MariaDB root user without the proper authorisation.

You already have your root account protected, so you can safely answer 'n'.

Switch to unix_socket authentication [Y/n] Y
Enabled successfully!
Reloading privilege tables..
 ... Success!


You already have your root account protected, so you can safely answer 'n'.

Change the root password? [Y/n] n
 ... skipping.

By default, a MariaDB installation has an anonymous user, allowing anyone
to log into MariaDB without having to have a user account created for
them.  This is intended only for testing, and to make the installation
go a bit smoother.  You should remove them before moving into a
production environment.

Remove anonymous users? [Y/n] Y
 ... Success!

Normally, root should only be allowed to connect from 'localhost'.  This
ensures that someone cannot guess at the root password from the network.

Disallow root login remotely? [Y/n] Y
 ... Success!

By default, MariaDB comes with a database named 'test' that anyone can
access.  This is also intended only for testing, and should be removed
before moving into a production environment.

Remove test database and access to it? [Y/n] Y
 - Dropping test database...
 ... Success!
 - Removing privileges on test database...
 ... Success!

Reloading the privilege tables will ensure that all changes made so far
will take effect immediately.

Reload privilege tables now? [Y/n] Y
 ... Success!

Cleaning up...

All done!  If you've completed all of the above steps, your MariaDB
installation should now be secure.

Thanks for using MariaDB!
```


## Solution to replica desynchronization (stopping data acquisition)

Useful link [replication issues](https://dba.stackexchange.com/questions/214102/mysql-replication-issues-duplicate-primary-key-error-and-problems-reading-rel)

### Syncing Master and Slave for Replication.

Syncing a Master and Slave is tricky on a Master which is live, online and constantly being updated.
The MariaDB [documentation](https://mariadb.com/kb/en/library/setting-up-replication/) and other answers to this question, recommend:

#### Master side: 
1. Open the VPN to LNGS and connect to the DAQ;
2. Enter Mariadb with the DAQ password:
  ```
  sudo mysql -u root -p
  ```
3. Flush and Lock ALL tables by running the following command:
  ```
  FLUSH TABLES WITH READ LOCK;
  ```
4. Get the current position in the binary log by running SHOW MASTER STATUS:
   ```
   SHOW MASTER STATUS;
   ```
   Output example:
   ```
      MariaDB [(none)]> SHOW MASTER STATUS;
      +------------------+----------+--------------+------------------+
      | File             | Position | Binlog_Do_DB | Binlog_Ignore_DB |
      +------------------+----------+--------------+------------------+
      | mysql-bin.XXXXXX |  XXXXXXX |              |                  |
      +------------------+----------+--------------+------------------+
      1 row in set (0,000 sec)
   ```
   
6. Record the File and Position details. *If binary logging has just been enabled, these will be blank.*

7. [IMPORTANT] Keep this session running - *exiting it will release the lock*.

8. Now, with the lock still in place, open another terminal on the DAQ.
9. Copy the data from the master:
   ```
   sudo mysqldump -u root --master-data <database-name> > ./<backup-file-name>.sql
   gzip ./<backup-file-name>.sql
   ```
10. Once the data has been exported, you can go to the first terminal and release the lock on the master by running UNLOCK TABLES.
    ```
    UNLOCK TABLES;
    ```
12. You must copy the exported data to the replica VM.
13. Once the data has been transferred to the VM you should go inside the VM.
    
#### Slave side:

1. Inside the VM you have to copy the exported data to the docker container, first check the name of MariaDB container, copy the file and then enter inside the container:
    ```
    docker ps
    docker cp <backup-file-name>.sql <container-name>:/
    docker exec -it <container-name> bash
    ```
2. Inside MariaDB Container you must STOP and [RESET the Slave](https://dev.mysql.com/doc/refman/5.5/en/reset-slave.html) (using MYSQL PWD):
    ```
    mysql -u root -p 
    STOP SLAVE;
    RESET SLAVE;
    EXIT;
    ```

3. Import the SQL file into the SLAVE:
   ```
   mysql -u root -p database-name < <backup-file-name>.sql
   ```
5. After that you should return to the MariaDB command line and set the Master configuration with the File and Position got on **Step 4 of the Master Side**:
   ```
   CHANGE MASTER TO MASTER_HOST = '127.0.0.1', MASTER_PORT = <PORT>, MASTER_USER = 'replication', MASTER_PASSWORD = '<replication-password>', MASTER_LOG_FILE = '<File-Master>', MASTER_LOG_POS = <Position-Master>;
   START SLAVE;   
   ```
6. Test if the SLAVE was started in the right way with the following command:
   ```
   SHOW SLAVE STATUS \G
   ```
   Output Example:
   ```
   *************************** 1. row ***************************
      Slave_IO_State: Waiting for master to send event
      Master_Host: <IP>
      Master_User: <replication-user>
      Master_Port: <PORT>
      Connect_Retry: 60
      Master_Log_File: <File-Master>
      Read_Master_Log_Pos: <Position-Master>
      Relay_Log_File: mysql-relay-bin.000002
      Relay_Log_Pos: 2601
      Relay_Master_Log_File: <>
      **Slave_IO_Running: Yes**
      **Slave_SQL_Running: Yes**
   ```
   
8. Now you should have your replica Up-to-date and running!

