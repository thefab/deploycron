import unittest
import subprocess
from getpass import getuser
from deploycron import deploycron, undeploycron_between, \
    _get_installed_content, _install_content


def deploycron_duplicates(filename="", content="", override=False):
    """Same as deploycron but can add duplicates for testing purpose"""

    if not filename and not content:
        raise ValueError("neither filename or crontab must be specified")

    if filename:
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except Exception as e:
            raise ValueError("cannot open the file: %s" % str(e))
    if override:
        installed_content = ""
    else:
        installed_content = _get_installed_content()
        installed_content = installed_content.rstrip("\n")
    for crontab in content.split("\n"):
        if crontab:
            if not installed_content:
                installed_content += crontab
            else:
                installed_content += "\n%s" % crontab
    if installed_content:
        installed_content += "\n"
    # install back
    _install_content(installed_content)


class MainTestCase(unittest.TestCase):

    def tearDown(self):
        subprocess.call(["sudo crontab -u " + getuser() + " -l | grep -v '* * "
                         "* * * echo [a-zA-z0-9] > /tmp/'  | sudo crontab -u"
                         " " + getuser() + " -"], shell=True)

    def test_deploy_none(self):
        # Nothing specified
        with self.assertRaises(ValueError):
            deploycron()

    def test_deploy_filename(self):
        # specify a filename with content
        subprocess.call(["echo '* * * * * echo file > /tmp/buffer' > "
                         "/tmp/youcrontab.tab"], shell=True)
        deploycron(filename="/tmp/youcrontab.tab")
        subprocess.call(["crontab -l > /tmp/test_filename"], shell=True)
        with open("/tmp/test_filename") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/youcrontab.tab"], shell=True)
        subprocess.call(["rm /tmp/test_filename"], shell=True)
        self.assertEqual(file_content, "* * * * * echo file > /tmp/buffer\n")

    def test_deploy_filename_error(self):
        # file doesn't exist
        with self.assertRaises(Exception):
            deploycron(filename="/tmp/idonotexist.tab")

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
        deploycron(content="* * * * * echo greetings > /tmp/buffer",
                   override=True)
        subprocess.call(["crontab -l > /tmp/test_crontab"], shell=True)
        with open("/tmp/test_crontab") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_crontab"], shell=True)
        self.assertEqual(file_content, "* * * * * echo greetings > "
                         "/tmp/buffer\n")

    def test_deploy_duplicates(self):
        # duplicates are not added
        deploycron(content="* * * * * echo greetings > /tmp/buffer")
        deploycron(content="* * * * * echo greetings > /tmp/buffer")
        subprocess.call(["crontab -l > /tmp/test_crontab"], shell=True)
        with open("/tmp/test_crontab") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_crontab"], shell=True)
        self.assertEqual(file_content, "* * * * * echo greetings > "
                         "/tmp/buffer\n")

    def test_undeploy(self):
        # remove cron instructions
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        undeploycron_between("* * * * * echo day > /tmp/buffer",
                             "* * * * * echo mate > /tmp/buffer")
        subprocess.call(["crontab -l > /tmp/test_undeploy"], shell=True)
        with open("/tmp/test_undeploy") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)
        self.assertEqual(file_content, "* * * * * echo Good > /tmp/buffer\n")

    def test_undeploy_start_not_found(self):
        # start_line is not found
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        undeploycron_between("* * * * * echo not_found > /tmp/buffer",
                             "* * * * * echo mate > /tmp/buffer")
        result = subprocess.call(["crontab -l > /tmp/test_undeploy"],
                                 shell=True)
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)
        self.assertFalse(result)

    def test_undeploy_stop_not_found(self):
        # stop_line is not found
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        undeploycron_between("* * * * * echo day > /tmp/buffer",
                             "* * * * * echo not_found > /tmp/buffer")
        result = subprocess.call(["crontab -l > /tmp/test_undeploy"],
                                 shell=True)
        self.assertFalse(result)
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)

    def test_undeploy_inverted_indices(self):
        # stop_line is before start_line in the parameters
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        undeploycron_between("* * * * * echo mate > /tmp/buffer",
                             "* * * * * echo day > /tmp/buffer")
        subprocess.call(["crontab -l > /tmp/test_undeploy"], shell=True)
        with open("/tmp/test_undeploy") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)
        self.assertEqual(file_content, "* * * * * echo Good > /tmp/buffer\n")

    def test_undeploy_2_occur_start(self):
        # remove where there are multiple occurences of start_line
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron_duplicates(content="* * * * * echo Good > /tmp/buffer")
        deploycron_duplicates(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        undeploycron_between("* * * * * echo Good > /tmp/buffer",
                             "* * * * * echo mate > /tmp/buffer",
                             2)
        subprocess.call(["crontab -l > /tmp/test_undeploy"], shell=True)
        with open("/tmp/test_undeploy") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)
        print(file_content)
        self.assertEqual(file_content, "* * * * * echo Good > /tmp/buffer\n")

    def test_undeploy_2_occur_stop(self):
        # remove where there are multiple occurences of stop_line
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron_duplicates(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        undeploycron_between("* * * * * echo Good > /tmp/buffer",
                             "* * * * * echo you > /tmp/buffer",
                             1,
                             2)
        subprocess.call(["crontab -l > /tmp/test_undeploy"], shell=True)
        with open("/tmp/test_undeploy") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)
        self.assertEqual(file_content, "* * * * * echo mate > /tmp/buffer\n")

    def test_undeploy_2_occur_start_error(self):
        # start_line occurence not found
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        self.assertFalse(undeploycron_between("* * * * * echo Good > "
                                              "/tmp/buffer",
                                              "* * * * * echo mate > "
                                              "/tmp/buffer",
                                              2))
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)

    def test_undeploy_2_occur_stop_error(self):
        # stop_line occurence not found
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        self.assertFalse(undeploycron_between("* * * * * echo Good > "
                                              "/tmp/buffer",
                                              "* * * * * echo mate > "
                                              "/tmp/buffer",
                                              1,
                                              2))
        subprocess.call(["rm /tmp/test_undeploy"], shell=True)

    def test_undeploy_wrong_occur_start(self):
        # invalid parameter
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        self.assertFalse(undeploycron_between("* * * * * echo Good > "
                                              "/tmp/buffer",
                                              "* * * * * echo day > "
                                              "/tmp/buffer",
                                              0))

    def test_undeploy_none_occur_start(self):
        # invalid parameter
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        self.assertFalse(undeploycron_between("* * * * * echo Good > "
                                              "/tmp/buffer",
                                              "* * * * * echo day > "
                                              "/tmp/buffer",
                                              None))

    def test_undeploy_wrong_occur_stop(self):
        # invalid parameter
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        self.assertFalse(undeploycron_between("* * * * * echo Good > "
                                              "/tmp/buffer",
                                              "* * * * * echo day > "
                                              "/tmp/buffer",
                                              1,
                                              0))

    def test_undeploy_none_occur_stop(self):
        # invalid parameter
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        self.assertFalse(undeploycron_between("* * * * * echo Good > "
                                              "/tmp/buffer",
                                              "* * * * * echo day > "
                                              "/tmp/buffer",
                                              1,
                                              None))

    def test_deploy_argparse(self):
        subprocess.call(["echo '* * * * * echo argparse > /tmp/buffer' > "
                         "/tmp/youcrontab.tab"], shell=True)
        subprocess.call(["python ../deploycron/cli_deploycron_file.py "
                         "/tmp/youcrontab.tab"], shell=True)
        subprocess.call(["crontab -l > /tmp/test_filename_argparse"],
                        shell=True)
        with open("/tmp/test_filename_argparse") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/youcrontab.tab"], shell=True)
        subprocess.call(["rm /tmp/test_filename_argparse"], shell=True)
        self.assertEqual(file_content, "* * * * * echo argparse > "
                         "/tmp/buffer\n")

    def test_undeploy_argparse(self):
        deploycron(content="* * * * * echo Good > /tmp/buffer")
        deploycron(content="* * * * * echo day > /tmp/buffer")
        deploycron(content="* * * * * echo to > /tmp/buffer")
        deploycron(content="* * * * * echo you > /tmp/buffer")
        deploycron(content="* * * * * echo mate > /tmp/buffer")
        subprocess.call(["python ../deploycron/cli_undeploycron_between.py "
                         "'* * * * * echo day > /tmp/buffer' "
                         "'* * * * * echo mate > /tmp/buffer'"], shell=True)
        subprocess.call(["crontab -l > /tmp/test_undeploy_argparse"],
                        shell=True)
        with open("/tmp/test_undeploy_argparse") as f:
            file_content = f.read()
        subprocess.call(["rm /tmp/test_undeploy_argparse"], shell=True)
        self.assertEqual(file_content, "* * * * * echo Good > /tmp/buffer\n")
