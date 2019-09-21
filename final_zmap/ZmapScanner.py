"""ZmapScanner - Vavious classes for running Zmap scans.

ZmapScanner is an abstract class that defines an interface for various types
of Zmap scans. Two subclasses that are defined are TcpScanner and
IcmpScanner. Each subclass provides default settings and custom calls to the
OS to run a Zmap scan.

These classes are wrapper classes for executing a Zmap scan on a host. Each
class is able to run a scan synchronously or asynchronously (recommended).
Since Zmap scans can run for hours it is important to plan scan executions
accordingly.

"""
# LIBRARIES
import asyncio
from asyncio.subprocess import PIPE, STDOUT
import subprocess
from math import ceil
from shlex import quote


class ZmapScanner():

    """The abstract class which will define a Zmap scan.

    Interface:

    __init__:   creates the object with all the required settings
    settings:   returns list of settings used
    run:        runs a scan
    run_async:  runs a scan asyncronously
    zmap_cmd:   returns the raw zmap string

    """
    IPV4_ADDRESSES = 2**32
    MAX_SCAN_PCT = 80.0         # Blacklist is around 86%
    MAX_COOLDOWN = 300          # 300s = 5 minutes
    MIN_COOLDOWN = 8            # Zmap default is 8s

    def __init__(self, config_file, max=0):
        """Initialize a ZmapScanner.

        A ZmapScanner contains properties that may be used to scan the Internet
        with the Zmap scanner.

        config_file:    file path to a valid Zmap configuration file.

                        Presumes that a Zmap config file exists with the
                        following items already defined:

                        interface "ens3"
                        source-port '40000-60000'
                        output-module json
                        output-filter 'repeat = 0'  # get rid of duplicates
                        blacklist-file /etc/zmap/blacklist.conf
                        log-directory /data/logs
                        verbosity 4

        max:            integer between 0 and 2**32 specifying how many IPs to
                        scan.

        """
        self.running = False                # Is a Zmap scan running?

        self.config_file = config_file

        self.probe_module = 'tcp_synscan'   # default mode is a tcp_synscan

        self.target_port = 0                # Must be supplied by subclass

        max = int(max)
        if (max > int(ZmapScanner.IPV4_ADDRESSES *
                      (ZmapScanner.MAX_SCAN_PCT/100.0))) or (max < 0):
            # if scanning more than 80% of the Internet, scan the whole
            # Internet.
            # if max is less than 0, scan the whole Internet.
            max = 0

        self.max_targets = max

        if max == 0:
            self.cooldown_time = ZmapScanner.MAX_COOLDOWN
        else:
            # 300s for max cooldown time
            # 8s for min cooldown time
            # 2**32 = max number of IP addresses in IPv4
            # This formula scales the cooldown time based upon the number of
            # targets.
            self.cooldown_time = ceil(
                ((ZmapScanner.MAX_COOLDOWN - ZmapScanner.MIN_COOLDOWN) /
                 ZmapScanner.IPV4_ADDRESSES)*self.max_targets) + \
                 ZmapScanner.MIN_COOLDOWN

        self.output_fields = []             # Must be supplied by subclass
        self.output_file = ""               # Must be supplied by subclass

    def settings(self):
        """Returns a dict with all of the settings for the Zmap object."""
        return {
                'config_file': self.config_file,
                'probe_module': self.probe_module,
                'target_port': self.target_port,
                'max_targets': self.max_targets,
                'cooldown_time': self.cooldown_time,
                'output_fields': self.output_fields,
                'output_file': self.output_file
                }

    def run(self):
        """Runs a Zmap scan with the object's parameters.

        Uses the settings in the object and in self.config_file to run the Zmap
        scan.

        Each subclass must implement logic to use each of the settings in this
        class to run a Zmap scan.

        """

        pass

    def run_async(self):
        """Runs a Zmap scan with the object's parameters asyncronously.

        Uses the settings in the object and in self.config_file to run the Zmap
        scan.

        Each subclass must implement logic to use each of the settings in this
        class to run a Zmap scan.

        """

        pass

    def send_to_kafka(self):
        pass

    def zmap_cmd(self, dryrun=False, as_string=False):
        """Returns the string that will be send to the host OS shell.

        Assembles a Zmap shell string.

        dry_run:        True = run Zmap with the --dryrun option.
        as_string:      By default (False) return a list of each setting. Set
                        to True to concatenate each setting together into a
                        string.

        """

        cmd = [
            'sudo',
            'zmap',
            '--config={}'.format(quote(self.config_file)),
            '--probe-module={}'.format(quote(self.probe_module)),
            '--cooldown-time={}'.format(str(self.cooldown_time)),
            '--output-fields={}'.format(
                quote(','.join(self.output_fields))
            ),
            '--output-file={}'.format(quote(self.output_file))
        ]

        if self.probe_module == 'tcp_synscan':
            cmd.append('--target-port={}'.format(str(self.target_port)))

        if self.max_targets > 0:
            cmd.append('--max-targets={}'.format(str(self.max_targets)))

        if dryrun:
            cmd.append('--dryrun')

        if as_string:
            return ' '.join(cmd)

        return cmd


class TcpScanner(ZmapScanner):

    """Performs a scan of a TCP port across the Internet.

    TcpScanner implements ZmapScanner for all TCP scans using the 'tcp_synscan'
    probe module for Zmap. All settings are managed in this class and the scan
    may be invoked by running <instance>.run().

    config_file:    path to a zmap config file. See ZmapScanner for details.
    port:           the tcp port to scan. Port 80 (HTTP) is the default.
    max:            the maximum number of IP addresses to scan. Default = all.
    output_file:    path to where the output is going to be written. Scans
                    can generate a LOT of output. A full scan can run into the
                    hundreds of GBs.

    """
    def __init__(
        self,
        config_file,
        port=80,
        max=0,
        output_file='tcp_scan.json'
    ):
        """Initializes a ZmapScanner that will scan a TCP port.

        Default scan is of TCP port 80 (HTTP).

        Optional parameter {max} should be an int that defines the maximum
        number of hosts to scan. The default of 0 means that all hosts on the
        Internet not in the blacklist will be scanned.

        """
        super().__init__(config_file, max)

        self.probe_module = "tcp_synscan"
        self.target_port = port

        self.output_fields = [
            "saddr",
            "daddr",
            "ttl",
            "classification",
            "success",
            "cooldown",
            "timestamp_str",
        ]
        self.output_file = output_file

    def run(self, dryrun=False):
        """Executes a Zmap scan syncronously.

        Takes all the settings stored in the class object, forms a valid Zmap
        shell string and passes it to the OS for execution.

        dryrun:     True = runs Zmap in dryrun mode and will not actually send
                    packets to the Internet.

        """

        if self.running:
            print(
                "[WARN] The run() function was called during a running scan. This request was ignored."
            )
            pass

        self.running = True
        subprocess.run(self.zmap_cmd())
        self.running = False

    async def run_async(self, scan_id=''):
        """Executes a Zmap TCP scan asynchronously.

        Takes all the settings stored in the class object, forms a valid Zmap
        shell string and passes it to the OS for execution.

        scan_id:    this parameter may be provided to display system messages
                    with a clear designation as to which scan it belongs to.
        """

        self.running = True
        process = await asyncio.create_subprocess_shell(
            self.zmap_cmd(as_string=True),
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
        )
        if scan_id == '':
            print("[INFO] The Zmap scan is running on process {}.".format(
                str(process.pid))
                )
        else:
            print(
                "[INFO] The Zmap scan '{}' is running on process {}.".format(
                    scan_id,
                    str(process.pid)
                    )
                )
        await process.wait()
        self.running = False
        if scan_id == '':
            print(
                "[INFO] The Zmap scan on process {} has completed.".format(
                    str(process.pid)
                    )
                )
        else:
            print(
                "[INFO] The Zmap scan '{}' on process {} has completed."
                .format(
                    scan_id,
                    str(process.pid)
                    )
                )


class IcmpScanner(ZmapScanner):

    """Performs an ICMP echo scan of the Internet.

    IcmpScanner implements ZmapScanner for all TCP scans using the
    'icmp_echoscan' probe module for Zmap. All settings are managed in this
    class and the scan may be invoked by running <instance>.run().

    config_file:    path to a zmap config file. See ZmapScanner for details.
    max:            the maximum number of IP addresses to scan. Default = all.
    output_file:    path to where the output is going to be written. Scans
                    can generate a LOT of output. A full scan can run into the
                    hundreds of GBs.

    """
    def __init__(
        self,
        config_file,
        max=0,
        output_file='icmp_scan.json'
    ):
        """Initializes a ZmapScanner that will perform an ICMP echo scan.

        Optional parameter {max} should be an int that defines the maximum
        number of hosts to scan. The default of 0 means that all hosts on the
        Internet not in the blacklist will be scanned.

        """
        super().__init__(config_file, max)

        self.probe_module = "icmp_echoscan"
        self.target_port = 0

        self.output_fields = [
            "saddr",
            "daddr",
            "ttl",
            "classification",
            "success",
            "cooldown",
            "timestamp_str"
        ]
        self.output_file = quote(output_file)

    def run(self, dryrun=False):
        """Executes a Zmap scan asyncronously.

        Takes all the settings stored in the class object, forms a valid Zmap
        shell string and passes it to the OS for execution.

        dryrun:     True = runs Zmap in dryrun mode and will not actually send
                    packets to the Internet.

        """

        self.running = True
        subprocess.run(self.zmap_cmd())

        self.running = False

    async def run_async(self, scan_id=''):
        """Executes a Zmap ICMP scan asynchronously.

        Takes all the settings stored in the class object, forms a valid Zmap
        shell string and passes it to the OS for execution.

        scan_id:    this parameter may be provided to display system messages
                    with a clear designation as to which scan it belongs to.
        """

        self.running = True
        process = await asyncio.create_subprocess_shell(
            self.zmap_cmd(as_string=True),
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT
        )
        if scan_id == '':
            print("[INFO] The Zmap scan is running on process {}.".format(
                str(process.pid))
                )
        else:
            print(
                "[INFO] The Zmap scan '{}' is running on process {}.".format(
                    scan_id,
                    str(process.pid)
                )
            )
        await process.wait()
        self.running = False
        if scan_id == '':
            print("[INFO] The Zmap scan on process {} has completed.".format(
                str(process.pid))
                )
        else:
            print(
                "[INFO] The Zmap scan '{}' on process {} has completed.".format(
                    scan_id,
                    str(process.pid)
                )
            )

# TESTING
# TEST 1: BOUNDARIES
# from ZmapScanner import ZmapScanner
# from ZmapScanner import TcpScanner
# myscanner = ZmapScanner('zmap-scan.conf')
# myscanner.settings()
# from pprint import pprint
# pprint(myscanner.settings())
# myscanner.run()
# myscanner = ZmapScanner('zmap-scan.conf', 2**20)
# pprint(myscanner.settings())
# myscanner = ZmapScanner('zmap-scan.conf', 2**31)
# pprint(myscanner.settings())
# myscanner = ZmapScanner('zmap-scan.conf', 2**31+2**30)
# pprint(myscanner.settings())
# myscanner = ZmapScanner('zmap-scan.conf', 2**31+2**30+2**29)
# pprint(myscanner.settings())
# myscanner = ZmapScanner('zmap-scan.conf', 2**32-1)
# pprint(myscanner.settings())
# myscanner = ZmapScanner('zmap-scan.conf', 2**32)
# pprint(myscanner.settings())
# myscanner = ZmapScanner('zmap-scan.conf', -1)
# pprint(myscanner.settings())
#
# TEST 2: DRY RUN
# from ZmapScanner import TcpScanner
# from pprint import pprint
# myscanner = TcpScanner('zmap-scan.conf', port=443, max=4e6, output_file='/data/https-scan_001.json')
# pprint(myscanner.settings())
# myscanner.run(dryrun=True)
