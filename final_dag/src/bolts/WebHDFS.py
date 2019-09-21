"""WriteWebHDFS writes scan data to Hadoop

Writes the analytics data to HDFS every 5 seconds.
"""

from __future__ import absolute_import, print_function, unicode_literals
from datetime import datetime
from hdfs import InsecureClient     # Used insecure client
from streamparse.bolt import BatchingBolt


class WriteWebHDFS(BatchingBolt):

    # Batch up the tuples every 5 seconds
    ticks_between_batches = 5

    def initialize(self, conf, ctx):
        self.conf = conf
        self.ctx = ctx

        # Keep track of how many tuples we have seen
        self.lines = 0

        # Open a connection via webHDFS to hadoop cluster
        # Will need to replace IP address with address of hadoop cluster
        # Also may need to update local /etc/hosts if that remote
        # address returns a hostname that does not resolve to the same
        # address in this file
        self.client = InsecureClient(
            'http://52.91.211.34:50070/',
            user='iro'
        )

        # Create an HDFS directory name based on bolt startup time
        n = datetime.now()
        self.dirname = 'scanrun-' + n.strftime("%Y%m%d%H%M%S")
        self.client.makedirs(self.dirname)

    def process_batch(self, key, tups):

        # Track number of lines and use it in filename to write
        self.lines += len(tups)
        filename = self.dirname + '/'
        filename = filename + str(self.ctx['taskid']).zfill(2)
        filename = filename + str(self.lines).zfill(10)
        filename = filename + '.txt'

        # Write to HDFS
        with self.client.write(filename, encoding='utf-8') as writer:
            for tup in tups:
                writer.write(tup.values[0]+'\n')

        self.log(self.lines)
        self.log(filename)
