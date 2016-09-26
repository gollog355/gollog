#!/usr/bin/env python
__author__ = 'TahirRauf'

import sys
from pprint import pprint, pformat  # NOQA
from optparse import OptionParser
import logging
from hydra.lib import util
from hydra.lib.runtestbase import RunTestBase
from testbase import TestBase
import time

try:
    # Python 2.x
    from ConfigParser import ConfigParser
except ImportError:
    # Python 3.x
    from configparser import ConfigParser

l = util.createlogger('ep', logging.INFO)
# l.setLevel(logging.DEBUG)


class GL(RunTestBase):
    def __init__(self, options, runtest=True, mock=False):
        self.options = options
        self.config = ConfigParser()
        RunTestBase.__init__(self, 'ep', self.options, self.config,
                             startappserver=runtest, mock=mock, app_dirs=['livefiles'])

class RunTest(object):
    def __init__(self, argv):
        usage = ('python %prog --test_duration=<time to run test>')
        parser = OptionParser(description='KRAKEN !!!',
                              version="0.1", usage=usage)
        parser.add_option("--config_file", dest='config_file', type='string', default="hydra.ini")
        parser.add_option("--live_dir", dest='live_dir', type='string', default="")

        (options, args) = parser.parse_args()
        if ((len(args) != 0)):
            parser.print_help()
            sys.exit(1)
        hydra = GL(options, False)
        hydra.start_appserver()
        hydra.start_init()
        base = TestBase(hydra)
        base.launch_clients(
            1, "inshaa0",
            "python /home/plumgrid/event-processing/event_extraction/compare_events.py -a /home/plumgrid/event-processing/event_extraction/sample_data/plumgrid_normal.log.gz -b /home/plumgrid/event-processing/event_extraction/sample_data/plumgrid_ha.log.gz -o /tmp/")
        #base.launch_clients(
        #    1, "inshab",
        #    "python /home/plumgrid/event-processing/event_extraction/compare_events.py -a ./sample_data/plumgrid_normal.log.gz -b ./sample_data/plumgrid_ha.log.gz -o /home/plumgrid/")
        time.sleep(300)

        l.info("===== Deleting all launched apps")
        hydra.delete_all_launched_apps()
        hydra.stop_appserver()

if '__main__' == __name__:
    argv = sys.argv
    print ("Running command : " + argv[0] + ' ' + '.'.join(argv[1:]))
    RunTest(argv)
