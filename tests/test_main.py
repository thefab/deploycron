#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import subprocess
import os.path
from deploycron import deploycron, undeploycron_between

class MainTestCase(unittest.TestCase):

    def tearDown(self):
        subprocess.call(["rm /tmp/buffer"], shell=True)
        subprocess.call(["sudo crontab -u florian -l | grep -v '* * * * * echo [a-zA-z0-9] > /tmp/'  | sudo crontab -u florian -"], shell=True)

    def test_deploy_none(self):
        # Nothing specified
        with self.assertRaises(ValueError):
            deploycron()

    def test_deploy_filename(self):
        # specify a filename with content
        subprocess.call(["echo '* * * * * echo file > /tmp/buffer' > /tmp/youcrontab.tab"], shell=True)
        deploycron(filename="/tmp/youcrontab.tab")
        subprocess.call(["crontab -l > /tmp/test_filename"], shell=True)
        with open("/tmp/test_filename") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/youcrontab.tab"], shell=True)
        subprocess.call(["rm /tmp/test_filename"], shell=True)
        self.assertEqual(file_content, "* * * * * echo file > /tmp/buffer\n")

    def test_deploy_content(self):
        # specify content
        deploycron(content="* * * * * echo hello > /tmp/buffer")
        subprocess.call(["crontab -l > /tmp/test_crontab"], shell=True)
        with open("/tmp/test_crontab") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_crontab"], shell=True)
        self.assertEqual(file_content, "* * * * * echo hello > /tmp/buffer\n")

    def test_deploy_override(self):
        # override existing crontab
        deploycron(content="* * * * * echo hello > /tmp/buffer")
        deploycron(content="* * * * * echo greetings > /tmp/buffer", override=True)
        subprocess.call(["crontab -l > /tmp/test_crontab"], shell=True)
        with open("/tmp/test_crontab") as f:
            file_content = f.read()
        self.assertEqual(file_content, "* * * * * echo greetings > /tmp/buffer\n")
        
    def test_undeploy(self):
        # remove cron instructions
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        undeploycron_between("* * * * * echo day > /tmp/buffer","* * * * * echo mate > /tmp/buffer")
        subprocess.call(["crontab -l > /tmp/test_undeploy"], shell=True)
        with open("/tmp/test_undeploy") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)
        self.assertEqual(file_content, "* * * * * echo Good > /tmp/buffer\n")
        
        
        
        
