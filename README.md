# W205 - Storing and Retrieving Data, Spring 2017
Final Project - April 30th, 2017

Jason Hunsberger, Victoria Baker, Dominic Delmolino

## Servers and Services

- Scan Server (AWS Ubuntu)
- Storm Server (AWS Amazon Linux)
- Hadoop Cluster Namenode (single-node) (AWS Amazon Linux)
- Kafka Service (from aiven.io)
- PostgreSQL Service (AWS RDS PostgreSQL)

Place servers in same AWS security group

## Kafka Cluster Configuration

Kafka version 0.10.2

http://aiven.io -  Create a Kafka service

1. Use Connection parameters from your Kafka service (host, port)
2. Download your CA certificate, access key and access certificate
3. Allowed IP addresses 0.0.0.0/0
4. Add topic "zmap_scans"

## Storm Server Configuration

### Server configuration

- m3.large
- Amazon Linux
- ec2-user

Storm topology available under /home/ec2-user/finaldag

### Create a .pgpass file

1. Navigate to /home/ec2-user
2. Create a .pgpass file with your PostgreSQL hostname:port:database:username:password
3. Database should be zmapdb
4. Username should be iro_admin

### Modify /etc/hosts file

1. Navigate to /etc
2. Use sudo to edit host file
3. Add entry for reported hostname of Hadoop Cluster namenode

### Copy Kafka certificate and key files

1. Navigate to /home/ec2-user/finalcerts
2. Copy ca.pem, service.cert and service.key files from the Aiven Kafka service to this directory

### Load PostgreSQL reference data

1. Navigate to /home/ec2-user/finalpsql
2. Edit country-load-script.sh file to point at your PostgreSQL database
3. Run the country-load-script.sh file

### View PostgreSQL analysis data

1. Navigate to /home/ec2-user/finalpsql
2. Edit analysis_queries.sh file to point at your PostgreSQL database
3. Run the analysis_queries.sh file to see summary results

### Edit the WebHDFS bolt

1. Navigate to /home/ec2-user/finaldag/src/bolts directory
2. Edit the WebHDFS.py
3. Replace the IP address in the InsecureClient call with the public address of your Hadoop namenode

### Java version

```
$ java -version
java version "1.7.0_131"
OpenJDK Runtime Environment (amzn-2.6.9.0.71.amzn1-x86_64 u131-b00)
OpenJDK 64-Bit Server VM (build 24.131-b00, mixed mode)
```

### Leiningen version

```
Leiningen 2.7.1 on Java 1.7.0_131 OpenJDK 64-Bit Server VM
```

### Storm version

```
$ storm version
0.9.3
```

### Streamparse version

```
$ sparse --version
sparse 2.1.4
```

### Python version

```
$ python --version
Python 2.7.12
```

### Python libraries installed

- hdfs (2.0.16)
- sycopg2 (2.7.1)
- kafka-python (1.3.3)
- streamparse (2.1.4)

## PostgreSQL

- AWS RDS PostgreSQL
- db.m3.xlarge
- Production instance
- PostgreSQL 9.5.4
- 1 TB Storage Provision IOPS (SSD)
- IOPS 3000
- dbname zmapdb
- Username iro_admin
- Security group includes inbound traffic from Storm server security group

## Hadoop Cluster Configuration

### Server configuration

- AMI w205_cp_hadoop_jhvbdd_final ami-def191c8
- m3.large
- Amazon Linux
- ec2-user
- 2 x 500GB (st1 volume type)
- Open ports 50070, 50075 and 8080 -- allow inbound from Storm server

### Filesystem additions

```
mkfs /dev/xvdf
mkfs /dev/xvdg
mount /dev/xvdf /data_01
mount /dev/xvdg /data_02
```

### Java version

```
$ java -version
java version "1.7.0_131"
OpenJDK Runtime Environment (amzn-2.6.9.0.71.amzn1-x86_64 u131-b00)
OpenJDK 64-Bit Server VM (build 24.131-b00, mixed mode)
```

### Hadoop version

```
$ hadoop version
Hadoop 2.7.1
Subversion https://git-wip-us.apache.org/repos/asf/hadoop.git -r 15ecc87ccf4a0228f35af08fc56de536e6ce657a
Compiled by jenkins on 2015-06-29T06:04Z
Compiled with protoc 2.5.0
From source with checksum fc0a1a23fc1868e4d5ee7fa2b28a58a
This command was run using /usr/local/hadoop/share/hadoop/common/hadoop-common-2.7.1.jar
```

### hadoop-env.sh lines to change

```
export JAVA_HOME=/usr
export HADOOP_LOG_DIR=/data_01/logs
```

### core-site.xml details

```
<configuration>

   <property>
      <name>fs.defaultFS</name>
      <value>hdfs://localhost:9000</value>
   </property>

   <property>
      <name>hadoop.temp.dir</name>
      <value>/data_01/temp</value>
   </property>

</configuration>
```

### hdfs-site.xml details

```
<configuration>

   <property>
      <name>dfs.name.dir</name>
      <value>/data_01/name</value>
   </property>

   <property>
      <name>dfs.data.dir</name>
      <value>/data_01/data,/data_02/data</value>
   </property>

   <property>
      <name>dfs.replication</name>
      <value>1</value>
   </property>

   <property>
      <name>dfs.webhdfs.enabled</name>
      <value>true</value>
   </property>

   <property>
      <name>mapred.job.tracker</name>
      <value>localhost:9001</value>
   </property>

</configuration>
```

### Hadoop user iro

```
$ hadoop fs -mkdir /user/iro
$ hadoop fs -chown iro:hadoop /user/iro
```

## Scan Server configuration

- AWS c3.large instance

### Zmap scanner build with Ubuntu 16.04 LTS - Xenial (HVM)

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade
sudo apt-get install python3-pip
sudo ln -s /usr/bin/python3 python
sudo ln -s /usr/bin/pip3 pip
sudo apt-get install unzip
sudo apt-get install nginx
pip install kafka-python
sudo apt-get install git gcc make libpcap-dev
```

### ZMAP Build from source

```
git clone git://github.com/zmap/zmap.git
cd zmap/
sudo apt-get install build-essential cmake libgmp3-dev libpcap-dev gengetopt byacc flex
sudo apt-get install git pkg-config libjson0-dev
git clone https://github.com/json-c/json-c.git
cd json-c/
sudo apt-get install autoconf
sudo apt-get install automake
sudo apt-get install libtool
sh autogen.sh
./configure
make -j 4
make install
sudo make install
make check

sudo apt-get install libunistring-dev

cmake -DWITH_JSON=ON -DENABLE_DEVELOPMENT=OFF
make
sudo make install
```

### nginx configuration

```
sudo vim /etc/nginx/nginx.conf
enabled: server_tokens off;

sudo service nginx reload
```

### Let's Encrypt! SSL Cert Installation

```
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot
sudo certbot certonly --webroot -w /var/www/html -d internet-observatory.io
sudo certbot certonly --webroot -w /var/www/html -d internet-observatory.io
sudo certbot renew --dry-run
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
sudo vim default
sudo nginx -t
```

# Running the project

## Start the scan server, Kafka service, PostgreSQL service, Storm Server and Hadoop cluster

## To Run a Scan

**NOTE**: The default configuration will scan approximately 8 million IP addresses on port 80 (HTTP).
1. Login into Storm Server as "ec2-user" user
2. Navigate to /home/ec2-user/finaldag directory
3. At the unix prompt, type "sparse run --option "supervisor.worker.timeout.secs=3600"
4. Login to Scan server as "ubuntu" user
5. Confirm /data is mounted with `mount -t ext4 /dev/xvdc /data`
6. Run `python3 zmap_scan_script.py`
7. After scan completes on scan server (confirmed with a message to stdout), use ctrl-c to cancel the scanner script.

Validate data by running SQL queries agains the PostgreSQL database

Check the Hadoop filesystem for the stream files

