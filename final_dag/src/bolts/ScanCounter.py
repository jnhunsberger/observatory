"""ScanCounter counts the number of IP addresses

ScanCounter counts the number of IPs that responded to our scan and the
number of IPs that responded by country.
"""

from __future__ import absolute_import, print_function, unicode_literals
import psycopg2     # Used to connect to Postgres
import json
from collections import Counter
from streamparse.bolt import Bolt


class ScanCounter(Bolt):

    def initialize(self, conf, ctx):
        self.scan_count = Counter()
        self.ctry_count = Counter()
        # Create the connection string to the DB with the country code
        # lookup.
        # NOTE: need to fill in correct host and port here
        self.conn = psycopg2.connect(
            database="zmapdb",
            user="iro_admin",
            password="aUgbsbIGaJ1KCXA1frN",
            host="internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com",
            port="5432"
        )
        self.conn.autocommit = False
        self.cur = self.conn.cursor()
        # insert ip count and scan id
        # scan_id, ip count
        self.checkipsql = """
            SELECT count(*)
            FROM ipcount
            WHERE scan_id = (%s);
            """
        self.insertipsql = """
            INSERT INTO ipcount (scan_id, count)
            VALUES (%s, %s);
            """
        self.updateipsql = """
            UPDATE ipcount
            SET count = (COUNT+1)
            WHERE scan_id = (%s);
            """
        # scan_id, country, count
        self.checkcountrysql = """
            SELECT count(*)
            FROM countrycount
            WHERE scan_id = (%s) AND countryabbr = (%s);
            """
        self.insertcountrysql = """
            INSERT INTO countrycount (scan_id, countryabbr, count)
            VALUES (%s, %s, %s);
            """
        self.updatecountrysql = """
            UPDATE countrycount
            SET count = (count+1)
            WHERE scan_id = (%s) AND countryabbr = (%s);
            """

    def process(self, tup):
        self.log("scan-counter-bolt has been entered.")

        msg_str = tup.values[0]
        msg_json = json.loads(msg_str)
        scan_id = msg_json['scan_id']
        ctry_code = msg_json['countryabbr']

        # Update scan-level analytics
        self.cur.execute(self.checkipsql, (scan_id,))
        rc = self.cur.fetchone()[0]     # return the results
        if rc > 0:
            self.cur.execute(self.updateipsql, (scan_id,))
        else:
            self.cur.execute(self.insertipsql, (scan_id, 1))
        self.conn.commit()

        # Update country-level analytics
        self.cur.execute(self.checkcountrysql, (scan_id, ctry_code))
        rc = self.cur.fetchone()[0]     # return the results.
        if rc > 0:
            self.cur.execute(self.updatecountrysql, (scan_id, ctry_code))
        else:
            self.cur.execute(self.insertcountrysql, (scan_id, ctry_code, 1))
        self.conn.commit()

        # emit the scan metadata
        self.scan_count[scan_id] += 1
        self.ctry_count[ctry_code] += 1
        # Log the count - just to see the topology running
        self.log('scan_id %s: %d' % (scan_id, self.scan_count[scan_id]))
        self.emit([msg_str])
