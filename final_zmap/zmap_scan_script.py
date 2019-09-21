#!/usr/bin/ python3

# LIBRARIES
from ZmapScan import ZmapScan
from ZmapKafkaProducer import ZmapKafkaProducer
from kafka import KafkaProducer
import asyncio
import json
import sys

# PYTHON VERSION CHECK
if sys.version_info[0] != 3 or sys.version_info[1] < 5:
    print("This script requires Python version 3.5 or greater.")
    sys.exit(1)

# SETTINGS
zmap_config_file = '/home/ubuntu/zmap-scan.conf'
zmap_output_file = '/data/http-scan-021.json'
kafka_server = 'kafka-d212393.ddelmoli-bb94.aivencloud.com:25959'
kafka_cert_path = '/home/ubuntu/kafka/certs'
kafka_scan_topic = 'zmap_scans'
kafka_scan_meta_topic = 'zmap_scans_meta'
tcp_port = 80
max_ips = 2**21

# Create the output file.
open(zmap_output_file, mode='w+t', encoding='utf-8').close()

# Create a TCP and ICMP scan object.
tcp_scan = ZmapScan(
    config_file=zmap_config_file,
    type='TCP',
    port=tcp_port,
    max=max_ips,
    output_file=zmap_output_file
)

kafka_scan_prod = ZmapKafkaProducer(
    server=kafka_server,
    cert_path=kafka_cert_path,
    topic_name=kafka_scan_topic,
    zmap_scan=tcp_scan
)

kafka_scan_meta_prod = KafkaProducer(
    bootstrap_servers=kafka_server,
    security_protocol="SSL",
    ssl_cafile=kafka_cert_path + "/ca.pem",
    ssl_certfile=kafka_cert_path + "/service.cert",
    ssl_keyfile=kafka_cert_path + "/service.key",
    )

# icmp_scan = ZmapScan(config_file='/home/ubuntu/zmap-scan.conf'
#     , type='ICMP'
#     , max=2**21
#     , output_file='/data/icmp-scan-010.json'
#     )

# Run scans asynchronously: works! but doesn't end...
loop = asyncio.get_event_loop()
tasks = [
    loop.create_task(tcp_scan.run_async_scan()),
    loop.create_task(kafka_scan_prod.run_async())
]
wait_tasks = asyncio.wait(tasks)
loop.run_until_complete(wait_tasks)
loop.close()

# Write scan
kafka_scan_meta_prod.send(
    kafka_scan_meta_topic,
    json.dumps(tcp_scan.settings()).encode("utf-8")
)
