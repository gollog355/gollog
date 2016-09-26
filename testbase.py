__author__ = 'TahirRauf'

import sys
from pprint import pprint, pformat  # NOQA
import logging
import websocket
import json
import time
import yaml
import os
from random import randint
import threading
from hydra.lib import util

l = util.createlogger('TestBase', logging.INFO)
# l.setLevel(logging.DEBUG)


class TestBase(object):
    """
    PGKrakenTestBase Class.
    Expected to hold all common methods to be used by derived test classes
    """
    def __init__(self, hydra):
        """
        Initiate Test:
        @args:
        name:    Name of current test deriving from this
        hydra:   hydra handle
        """
        # Dictionary to hold results of some particular group. Key would be group_name.
        self.hydra = hydra
        self.group_results = {}

    def launch_clients(self, num_clients, app_name, app_script):
        """
        Launches num_client number of clients equally distributed among slave nodes.
        Function will first delete any existing client.
        Args:
            num_clients: Number of hermes clients to launch.
            app_name:    Name of the app
        Returns:
        """
        self.hydra.delete_app(app_name, timeout=5)  # delete_app will remove the app if already exists.
        self.hydra.add_appid(app_name)
        constraints = []
        l.info("Creating binary app with name %s " % app_name)
        self.hydra.create_binary_app(name=app_name,
                                     app_script=app_script,
                                     cpus=0.01, mem=32,
                                     ports=[0],
                                     constraints=constraints)
        self.hydra.scale_and_verify_app(app_name, int(num_clients * 1.1), ping=True,
                                        sleep_before_next_try=5)