"""Country reads IP addresses and enriches them with Country information.

Country is a streamparse Bolt subclass that:
1. Takes JSON objects as input
2. Extracts the IP address field
3. Converts the IP address to an IP decimal
4. Looks up the country that the IP address is associated with.
5. Adds Country Name and Country Code attributes to the JSON object.

This class expects that the Country:IP lookup database is stored in
Postgres.
"""

import psycopg2     # Used to connect to Postgres
import json
from streamparse.bolt import Bolt


class Country(Bolt):

    def initialize(self, conf, ctx):
        self.conn = psycopg2.connect(
            database="zmapdb",
            user="iro_admin",
            password="aUgbsbIGaJ1KCXA1frN",
            host="internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com",
            port="5432"
        )
        self.conn.autocommit = False
        self.cur = self.conn.cursor()
        self.getCountry = """
                SELECT ipstart, ipend, countryabbr, countryname
                FROM country
                WHERE (%s) <= ipend AND (%s) >= ipstart
                """

    def process(self, tup):
        msg_str = tup.values[0]
        msg_json = json.loads(msg_str)

        # Get source (the responding host's) ip address from json
        ipaddr = msg_json['saddr']

        # Split the IP address numbers by '.'
        num1, num2, num3, num4 = map(int, ipaddr.split("."))

        # Calculate ip decimal and add it to the json object
        ip_decimal = (
            num1*(2**24) +
            num2*(2**16) +
            num3*(2**8) +
            num4
            )
        msg_json['ipdec'] = ip_decimal

        if ip_decimal > 0:
            # if the ip_decimal is not negative, perform a country code lookup

            self.cur.execute(self.getCountry, (ip_decimal, ip_decimal))
            row = self.cur.fetchone()

            msg_json['countryabbr'] = row[2]
            msg_json['countryname'] = row[3]

            self.conn.commit()

        # convert json object back to str
        msg_str = json.dumps(msg_json).encode("utf-8")

        # The following code is useful for debugging the spout.
        # self.log('country-bolt: %s = %d in %s' % (ipaddr
        #    , ip_decimal
        #    , msg_json['countryname']
        #    ))
        self.emit([msg_str])
