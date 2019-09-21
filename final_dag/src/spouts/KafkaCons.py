"""KafkaMessages reads JSON objects from a Kafka cluster.

KafkaMessages is a Streamparse Spout subclass that reads JSON objects
from a Kafka cluster and emits them to the streamparse directed acyclic
graph (DAG).

"""
from __future__ import absolute_import, print_function, unicode_literals
from streamparse.spout import Spout
from kafka import KafkaConsumer


class KafkaMessages(Spout):
    def initialize(self, stormconf, context):
        self.conf = stormconf,
        self.context = context
        self.consumer = KafkaConsumer(
            "zmap_scans",
            bootstrap_servers="kafka-d212393.ddelmoli-bb94.aivencloud.com:25959",
            client_id="zmap_scans_reader_01",
            group_id="zmap_scans_readers",
            security_protocol="SSL",
            ssl_cafile="/home/ec2-user/finalcerts/ca.pem",
            ssl_certfile="/home/ec2-user/finalcerts/service.cert",
            ssl_keyfile="/home/ec2-user/finalcerts/service.key"
            )

    def next_tuple(self):
        for msg in self.consumer:
            # The following commented code is useful for debugging the
            # spout. Uncomment if needed.
            # self.log('kafka-spout: {}'.format(msg.value))
            self.emit([msg.value])

    def ack(self, tup_id):
        pass    # if a tuple is processed properly, do nothing

    def fail(self, tup_id):
        pass    # if a tuple fails to process, do nothing
