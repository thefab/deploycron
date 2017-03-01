# coding: utf-8

import subprocess
import os

def deploycron(filename="", content="", override=False):
    """install crontabs into the system if it's not installed.
    This will not remove the other crontabs installed in the system if not specified
    as override. It just merge the new one with the existing one. 
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
    retcode, err, out = _runcmd("crontab", installed_content)
    if retcode != 0:
        raise ValueError("failed to install crontab, check if crontab is valid")

def undeploycron_between(start_line, stop_line):
    """uninstall crontab parts between two lines (included).
    If the start_line or the stop_line is not found into the installed crontab,
    it won't be modified.
    start_line - start line to delimit the crontab block to remove
    stop_line - stop line to delimit the crontab block to remove
    """
    installed_content = _get_installed_content()
    if start_line not in installed_content:
        return False
    if stop_line not in installed_content:
        return False
    between = False
    installed_crontabs = []
    for crontab in installed_content.split("\n"):
        if not between and start_line.strip() in crontab:
            between = True
        elif between and stop_line.strip() in crontab:
            between = False
        else:
            if not between:
                installed_crontabs.append(crontab)
        print crontab, between, installed_crontabs
    if len(installed_crontabs) > 0:
        installed_crontabs.append("")
    installed_content = "\n".join(installed_crontabs)
    retcode, err, out = _runcmd("crontab", installed_content)
    if retcode != 0:
        raise ValueError("failed to install crontab, check if crontab is valid")
    return True

def _get_installed_content():
    retcode, err, installed_content = _runcmd("crontab -l")
    if retcode != 0 and 'no crontab for' not in err:
        raise OSError("crontab not supported in your system")
    installed_content = installed_content.rstrip("\n")
    return installed_content

def _runcmd(cmd, input=None):
    '''run shell command and return the a tuple of the cmd's return code, std error and std out
    WARN: DO NOT RUN COMMANDS THAT NEED TO INTERACT WITH STDIN WITHOUT SPECIFY INPUT,
         (eg cat), IT WILL NEVER TERMINATE.
    '''

    if input is not None:
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True, preexec_fn=os.setsid)
    else:
        p = subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True, preexec_fn=os.setsid)

    stdoutdata, stderrdata = p.communicate(input)
    return p.returncode, stderrdata, stdoutdata


