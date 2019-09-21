"""ZmapScan class manages the settings for a Zmap scan.

ZmapScan is a wrapper class used to manage the settings and configuration of
a Zmap scan. This includes any configuration parameters necessary to execute a
scan plus meta data about a scan such as a unique ScanID, the start and end
time for a scan, and the type of scan.
"""

# LIBRARIES
import uuid
from datetime import datetime
from ZmapScanner import TcpScanner, IcmpScanner


class ZmapScan():

    """A class to manage the metadata for a Zmap scan.

    More to come.
    Interface:
    __init__:   initializes all Zmap scan settings, creates ZmapScanner object
    run_async_scan:     runs a scan asyncronously
    settings:   returns all settings for the scan
    """

    def __init__(
        self,
        config_file,
        type='TCP',
        port=80,
        max=2**22,    # scan approx. 4.1m IP addresses
        output_file = 'tcp-scan_000.json'
    ):

        """Initialize a ZmapScan object.

        Defaults to a TCP scan. If type is unrecognized, then this will be an
        ICMP scan.
        """
        self.scan_id = str(uuid.uuid4())
        self.start_time = ''
        self.end_time = ''
        self.type = type
        if type.upper() == 'TCP':
            self.scanner = TcpScanner(
                config_file=config_file,
                port=port,
                max=max,
                output_file=output_file
            )
        elif type.upper() == 'ICMP':
            self.scanner = IcmpScanner(
                config_file=config_file,
                max=max,
                output_file=output_file
            )
        else:
            print(
                "[WARN] No scan type chosen. Valid choices are 'TCP' or 'ICMP'. This scan is configured for 'ICMP'."
            )
            self.scanner = IcmpScanner(
                config_file=config_file,
                max=max,
                output_file=output_file
            )

    async def run_async_scan(self):
        """Runs the scan asynchronously.

        More to come.
        """

        self.start_time = str(datetime.utcnow())
        await self.scanner.run_async(self.scan_id)
        self.end_time = str(datetime.utcnow())

    def settings(self):
        return {
            'scan_id': self.scan_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'type': self.type,
            'scan_settings': self.scanner.settings()
        }
