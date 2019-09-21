# Zmap Scanning Library

Zmap is an Internet-scale scanning utility that can perform an internet-wide scan in under an hour. Zmap was invented at the University of Michigan and currently is used by the censys organization to provide census data about the public Internet.

The Zmap Scanning Library was built to ease the deployment of a Zmap scan across a server infrastruture and to feed the data it produces into a Kafka cluster for further processing.

To execute a Zmap scan, some configuration is needed.

This library assumes that Zmap is installed on the system that is running these scripts. It also assumes the following:

* Python 3.5+
* Kafka-Python library is installed
* You have full authorization to scan from the network you are running these tools.
* A kafka cluster is available to send the Zmap data into
* Zmap is compiled with the JSON extensions

Running a Zmap scan requires modifying the settings stored in zmap_scan_script.py to match your environment's configuration. It will also require a custom zmap_config_file. A sample config file should be in this repository.

## TODO LIST

The following aspects of the library still need refinement:
* Implement other scan types in ZmapScanner
* Be able to send a signal to ZmapKafkaProducer to shutdown once ZmapScan has completed.
