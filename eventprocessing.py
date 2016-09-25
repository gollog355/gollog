#!/usr/bin/env python
__author__ = 'TahirRauf'

import sys
# TODO: Use some other path
sys.path.insert(0, '/opt/pg/kraken')
from pprint import pprint, pformat  # NOQA
from optparse import OptionParser
import logging
from hydra.lib import util
from hydra.lib.runtestbase import RunTestBase
from testbase import TestBase

try:
    # Python 2.x
    from ConfigParser import ConfigParser
except ImportError:
    # Python 3.x
    from configparser import ConfigParser

l = util.createlogger('ep', logging.INFO)
# l.setLevel(logging.DEBUG)


class EP(RunTestBase):
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
        hydra = EP(options, False)
        hydra.start_appserver()
        hydra.start_init()
        base = TestBase(hydra)
        base.launch_clients(6, "insha")

        l.info("===== Deleting all launched apps")
        hydra.delete_all_launched_apps()
        hydra.stop_appserver()

if '__main__' == __name__:
    argv = sys.argv
    print ("Running command : " + argv[0] + ' ' + '.'.join(argv[1:]))
    RunTest(argv)
