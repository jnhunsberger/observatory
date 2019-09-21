"""ZmapKafkaProducer reads a json file and streams it to a Kakfa cluster.

Will continuously read a JSON file filled with Zmap data and send it to
a Kafka cluster for processing.

This class requires that the Kafka-Python package is installed.

"""

# LIBRARIES
from kafka import KafkaProducer
import asyncio
import json


class ZmapKafkaProducer():

    """"""
    POLL_INTERVAL = 0.01     # seconds to wait before checking file

    def __init__(self, server, cert_path, topic_name, zmap_scan):
        """Initialize a ZmapKafkaProducer

        More to come.

        """
        self.server = server
        self.cert_path = cert_path
        self.file_path = zmap_scan.scanner.output_file
        self.scan_id = zmap_scan.scan_id
        self.scan_type = zmap_scan.type
        self.topic_name = topic_name
        self.producer = KafkaProducer(
            bootstrap_servers=self.server,
            security_protocol="SSL",
            ssl_cafile=self.cert_path + "/ca.pem",
            ssl_certfile=self.cert_path + "/service.cert",
            ssl_keyfile=self.cert_path + "/service.key",
        )

    async def __readline(self, f):
        """Hidden method to read a file asyncronously.

        """
        while True:
            data = f.readline()
            if data:
                return data
#             else:
#                 print("[INFO] ZmapKafkaProducer has no data to read.")
#                 break
            await asyncio.sleep(ZmapKafkaProducer.POLL_INTERVAL)

    async def run_async(self):

        if self.topic_name == '':
            print("[ERROR]: Kafka topic has not been set for this object.")
            quit()

        if self.file_path == '':
            print(
                "[ERROR]: The file to read has not been set for this object."
                )
            quit()

        if self.scan_id == '':
            print("[ERROR]: The scan_id has not been set for this object.")
            quit()

        if self.scan_type == '':
            print("[ERROR]: The scan_id has not been set for this object.")
            quit()

        msg_count = 0
        with open(
            self.file_path,
            mode='r+t',
            encoding='utf-8'
        ) as f:

            while True:
                line = await self.__readline(f)
                if line:
                    msg = json.loads(line)
                    msg['scan_id'] = self.scan_id
                    msg['scan_type'] = self.scan_type

                    # print a status message every 1000 cycles
                    if msg_count % 1000 == 0:
                        print("Sending message #: {:>10} | {}".format(
                            msg_count,
                            line.strip()
                            )
                            )
                    # send message to Kafka topic
                    self.producer.send(
                        self.topic_name,
                        json.dumps(msg).encode("utf-8")
                        )
                    msg_count += 1
                else:
                    print("[INFO] ZmapKafkaProducer has no more data to send.")
                    break
        # Wait for all messages to be sent
        self.producer.flush()

    def settings(self):
        """Displays all the settings for this Kafka Producer"""
        return {
                'kafka_settings': {
                    'server': self.server,
                    'cert_path': self.cert_path,
                    'topic_name': self.topic_name,
                },
                'file_path': self.file_path,
                'scan_id': self.scan_id,
                'poll_interval': str(self.POLL_INTERVAL)
                }
