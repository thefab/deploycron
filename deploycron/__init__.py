# coding: utf-8

import subprocess
import os


def deploycron(filename="", content="", override=False):
    """install crontabs into the system if it's not installed.
    This will not remove the other crontabs installed in the system if not
    specified as override. It just merge the new one with the existing one.
    If you provide `filename`, then will install the crontabs in that file
    otherwise install crontabs specified in content

    filename - file contains crontab, one crontab for a line
    content  - string that contains crontab, one crontab for a line
    override - override the origin crontab
    """
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
    installed_crontabs = installed_content.split("\n")
    for crontab in content.split("\n"):
        if crontab and crontab not in installed_crontabs:
            if not installed_content:
                installed_content += crontab
            else:
                installed_content += "\n%s" % crontab
    if installed_content:
        installed_content += "\n"
    # install back
    _install_content(installed_content)


def undeploycron_between(start_line, stop_line, occur_start=1, occur_stop=1):
    """uninstall crontab parts between two lines (included).
    If the start_line or the stop_line is not found into the installed crontab,
    it won't be modified.
    `start_line` - start crontab line (the actual line, not the line number)
    to delimit the crontab block to remove
    `stop_line` - stop crontab line (the actual line, not the line number)
    to delimit the crontab block to remove
    `occur_start` - nth occurence you want to consider as start_line (ex :
    choose 2 if you want the 2nd occurence to be chosen as start_line)
    `occur_stop` - nth occurence you want to consider as stop_line (ex :
    choose 2 if you want the 2nd occurence to be chosen as stop_line)
    """
    lines_installed = [x.strip() for x in
                       _get_installed_content().splitlines()]
    start_line = start_line.strip()
    stop_line = stop_line.strip()
    if start_line not in lines_installed:
        return False
    if stop_line not in lines_installed:
        return False
    if occur_start is None or occur_start <= 0:
        return False
    if occur_stop is None or occur_stop <= 0:
        return False

    # Check if stop_line is before start_line by getting their indices
    index_start = -1
    index_stop = -1
    try:
        # Find the occurence we are interested in
        for j in range(occur_start):
            index_start = lines_installed.index(start_line, index_start + 1)
    except ValueError:
        # If the occurence number is too high (nth occurrence not found)
        return False
    try:
        for j in range(occur_stop):
            index_stop = lines_installed.index(stop_line, index_stop + 1)
    except ValueError:
        return False

    # If stop is before start, we switch them
    if index_stop < index_start:
        buffer_var = index_start
        index_start = index_stop
        index_stop = buffer_var

    lines_to_install = []
    for i in range(len(lines_installed)):
        if i < index_start or i > index_stop:
            lines_to_install.append(lines_installed[i])

    if len(lines_to_install) > 0:
        lines_to_install.append("")
    content_to_install = "\n".join(lines_to_install)
    _install_content(content_to_install)
    return True


def _get_installed_content():
    """get the current installed crontab.
    """
    retcode, err, installed_content = _runcmd("crontab -l")
    if retcode != 0 and b'no crontab for' not in err:
        raise OSError("crontab not supported in your system")
    return installed_content.decode("utf-8")


def _install_content(content):
    """install (replace) the given (multilines) string as new crontab...
    """
    retcode, err, out = _runcmd("crontab", content)
    if retcode != 0:
        raise ValueError("failed to install crontab, check if crontab is "
                         "valid")


def _runcmd(cmd, input=None):
    '''run shell command and return the a tuple of the cmd's return code, std
    error and std out.
    WARN: DO NOT RUN COMMANDS THAT NEED TO INTERACT WITH STDIN WITHOUT SPECIFY
    INPUT, (eg cat), IT WILL NEVER TERMINATE.
    '''

    if input is not None:
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True, preexec_fn=os.setsid)
        input = input.encode()
    else:
        p = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True, preexec_fn=os.setsid)

    stdoutdata, stderrdata = p.communicate(input)
    return p.returncode, stderrdata, stdoutdata
