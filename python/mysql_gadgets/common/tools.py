#
# Copyright (c) 2016, 2017, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#

"""
This module contains methods for working with mysql server tools.
"""
import shlex
from contextlib import closing
import logging
import os
import signal
import socket
import subprocess
import sys
import tempfile


from mysql_gadgets.exceptions import GadgetError

# pylint: disable=C0411
if sys.version_info > (3, 0):
    # Python 3
    import configparser  # pylint: disable=E0401,
else:
    # Python 2
    import ConfigParser as configparser  # pylint: disable=E0401

_LOGGER = logging.getLogger(__name__)


def _add_basedir(search_paths, path_str):
    """Add a basedir and all known sub directories

    This method builds a list of possible paths for a basedir for locating
    special MySQL files like mysqld (mysqld.exe), etc.

    Note: The resulting paths are append to the list passed by the
    'search_paths' parameter.

    :param search_paths: List of paths to append. The list passed by this
                         parameter is updated by this method.
    :type search_paths: list
    :param path_str:    The basedir path to append.
    :param path_str:    string
    """
    search_paths.append(path_str)
    search_paths.append(os.path.join(path_str, "sql"))       # for source trees
    search_paths.append(os.path.join(path_str, "client"))    # for source trees
    search_paths.append(os.path.join(path_str, "share"))
    search_paths.append(os.path.join(path_str, "scripts"))
    search_paths.append(os.path.join(path_str, "bin"))
    search_paths.append(os.path.join(path_str, "libexec"))
    search_paths.append(os.path.join(path_str, "mysql_utils"))


def get_tool_path(basedir, tool, fix_ext=True, required=True,
                  defaults_paths=None, search_path=False, quote=False,
                  check_tool_func=None):
    """Search for a MySQL tool and return the full path

    :param basedir:        The initial basedir (of a MySQL server) to search.
    :type basedir:         string or None
    :param tool:           The name of the tool to find
    :type tool:            string
    :param fix_ext:        If True (default is True), add .exe if running on
                           Windows.
    :type fix_ext:         boolean
    :param required:       If True (default is True) then an error will be
                           raised if the tool is not found.
    :type required:        boolean
    :param defaults_paths: Default list of paths to search for the tool.
                           By default (None) an empty list is assumed, i.e. [].
    :type defaults_paths:  list
    :param search_path:    Indicates if the paths specified by the PATH
                           environment variable will be used to search for the
                           tool. By default the PATH will not be searched,
                           i.e. search_path=False.
    :type search_path:     boolean
    :param quote:          if True then the resulting path is surrounded with
                           the OS quotes.
    :type quote:           boolean
    :param check_tool_func Function to verify the validity of the found tool.
                           This function must take the path of the tool as
                           parameter and return True or False depending if the
                           tool is valid or not (e.g., verify the version).
                           If this check tool function is specified, it will
                           continue searching for the tool in the provided
                           default paths until a valid one is found. By
                           default: None, meaning that it returns the first
                           location found with the tool (without any check).
    :type check_tool_func  function

    :return: the full path to tool or a list of paths where the tool was found
            if 'search_all' is set to True, or None if not found and 'required'
             is set to False.
    :rtype:  string

    :raises GadgetError: if the tool cannot be found and 'required' is set to
                         True.
    """
    if not defaults_paths:
        defaults_paths = []
    search_paths = []
    if quote:
        if os.name == "posix":
            quote_char = "'"
        else:
            quote_char = '"'
    else:
        quote_char = ''
    if basedir:
        # Add specified basedir path to search paths
        _add_basedir(search_paths, basedir)

    # Search in path from the PATH environment variable
    if search_path:
        for path in os.environ['PATH'].split(os.pathsep):
            search_paths.append(path)

    if defaults_paths and len(defaults_paths):
        # Add specified default paths to search paths
        for path in defaults_paths:
            search_paths.append(path)
    else:
        # Add default MySQL paths to search for tool
        if os.name == "nt":
            search_paths.append("C:/Program Files/MySQL/MySQL Server 5.7/bin")
            search_paths.append("C:/Program Files/MySQL/MySQL Server 8.0/bin")
        else:
            search_paths.append("/usr/sbin/")
            search_paths.append("/usr/local/mysql/bin/")
            search_paths.append("/usr/bin/")
            search_paths.append("/usr/local/bin/")
            search_paths.append("/usr/local/sbin/")
            search_paths.append("/opt/local/bin/")
            search_paths.append("/opt/local/sbin/")

    if os.name == "nt" and fix_ext:
        tool = "{0}.exe".format(tool)
    # Search for the tool
    for path in search_paths:
        norm_path = os.path.normpath(path)
        if os.path.isdir(norm_path):
            toolpath = os.path.normpath(os.path.join(norm_path, tool))
            if os.path.isfile(toolpath):
                if not check_tool_func or check_tool_func(toolpath):
                    return r"{0}{1}{0}".format(quote_char, toolpath)
            else:
                if tool == "mysqld.exe":
                    toolpath = os.path.normpath(
                        os.path.join(norm_path, "mysqld-nt.exe"))
                    if os.path.isfile(toolpath):
                        if not check_tool_func or check_tool_func(toolpath):
                            return r"{0}{1}{0}".format(quote_char, toolpath)

    # Tool not found, raise exception or return None.
    if required:
        raise GadgetError("Cannot find location of {0}.".format(tool))

    return None


def get_abs_path(path_string, relative_to=None):
    """ Get the absolute path for a file
    This function is used to get the absolute path for the argument provided
    via the path_string parameter. If the provided path_string is an
    absolute path, we return it as is, otherwise we will assume it is a
    relative path relative to the relative_to parameter and use that to
    calculate the absolute path.
    :param path_string: Absolute or relative path to which we want to
                        obtain an absolute path.
    :param path_string: string.
    :param relative_to: absolute path to a directory or file which will be used
                        as the path to which the path_string argument is
                        relative.
    :type relative_to: string
    :return: Absolute path for the path specified in path_string.
    :rtype:  string
    :raises GadgetError: if path_string is not an absolute path and the
                 provided relative_dir parameter is not an absolute path.
    """
    if os.path.isabs(os.path.expanduser(path_string)):
        return os.path.expanduser(path_string)
    else:
        if not os.path.isabs(relative_to):
            raise GadgetError("{0} is not a valid absolute path.".format(
                relative_to))
        else:
            if os.path.isfile(relative_to):
                relative_to = os.path.dirname(relative_to)
            return os.path.normpath(os.path.expanduser(
                os.path.join(relative_to, path_string)))


def create_option_file(section_dict, name=None, prefix_dir=None):
    """ Create an option file from a dictionary of dictionaries.

    :param section_dict: dictionary of dictionaries. The keys in the top level
                         dictionary are sections and the values are
                         dictionaries whose keys and values are the key:value
                         pairs of the section.
    :type section_dict:  {section1: {key: val, key2: val},
                          section2: {key: val..}
                          ..}
    :param name: name of the config file. If no name is provided, a randomly
                named option file is created.
    :type name: str or None
    :param prefix_dir: full path to a directory where we want the temporary
                       file to be created. By default it uses the $HOME of the
                       user.
    :type prefix_dir: str
    :return: string with full path to the created config file.
    :rtype: str
    """
    if prefix_dir is None:
        prefix_dir = os.path.expanduser("~")
    else:  # check if prefix points to a valid folder
        # normalize path and expand possible ~
        prefix_dir = os.path.normpath(os.path.expanduser(prefix_dir))
        if not os.path.isdir(prefix_dir):
            raise GadgetError("prefix_dir '{0}' is not a valid folder. Check "
                              "if it exists.".format(prefix_dir))
    _LOGGER.debug("Creating option file under directory %s ...",
                  prefix_dir)
    if name:
        f_path = os.path.join(prefix_dir, name)
        if os.path.exists(f_path):
            raise GadgetError("Unable to create option file '{0}' since a "
                              "file of the same already exists."
                              "".format(f_path))
        try:
            f_handler = os.open(f_path, os.O_CREAT | os.O_WRONLY | os.O_EXCL,
                                0o600)
        except (OSError, IOError) as err:
            raise GadgetError("Unable to create named configuration "
                              "file '{0}': {1}.".format(f_path, str(err)))
    else:
        try:
            # create temporary file under prefix_dir
            f_handler, f_path = tempfile.mkstemp(dir=prefix_dir, suffix=".cnf")
        except (OSError, IOError) as err:
            raise GadgetError("Unable to create randomly named configuration "
                              "file in directory '{0}': {1}."
                              "".format(prefix_dir, str(err)))
    _LOGGER.debug("Config file %s created successfully ", f_path)
    # Create configuration file
    config = configparser.RawConfigParser(allow_no_value=True)

    _LOGGER.debug("Filling config parser object...")
    # Fill it with contents from options
    for section, section_d in section_dict.items():
        config.add_section(section)
        for key, val in section_d.items():
            config.set(section, key, val)
    _LOGGER.debug("Config parser object created.")
    _LOGGER.debug("Writing contents of the configuration file")
    with closing(os.fdopen(f_handler, 'w')) as cnf_file:
        config.write(cnf_file)
    _LOGGER.debug("Config file %s successfully written.", f_path)
    return f_path


def get_subclass_dict(cls):
    """Get a dictionary with the subclasses of class 'cls'.

    This method returns a dictionary with all the classes that inherit from
    class cls.
    Note that this method only works for new style classes

    :param cls: class to which we want to find all subclasses
    :type cls: class object
    :return: dictionary whose keys are the names of the subclasses and values
             are the subclass objects.
    :rtype: dict
    """
    subclass_dict = {}

    for subclass in cls.__subclasses__():
        subclass_dict[subclass.__name__] = subclass
        subclass_dict.update(get_subclass_dict(subclass))

    return subclass_dict


def is_listening(host, port):
    """Try to check if a given port on a given host is bound and listening.

    :param host: hostname we want to check
    :type host: str
    :param port: port number to check if is bound
    :type port: int
    :return: True if port is bound and listening, False otherwise
    :rtype: bool
    """
    # Socket Initialization
    port = port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        return True
    except socket.error:
        return False


def is_executable(exec_path):
    """ Checks if a given path belongs to an executable file

    :param exec_path: absolute path to the file we want to test is executable.
    :type exec_path: str

    :return: True if file exists and is executable, False otherwise
    :rtype: bool
    """
    _LOGGER.debug("Checking if file '%s' is executable.", exec_path)
    is_file = os.path.isfile(exec_path)
    if not is_file:
        _LOGGER.debug("File '%s' could not be found.", exec_path)
        return False
    elif os.access(exec_path, os.X_OK):
        _LOGGER.debug("File '%s' exists and is executable.", exec_path)
        return True
    else:
        _LOGGER.debug("File '%s' exists but is not executable.", exec_path)
        return False


def run_subprocess(cmd_str, **kwargs):
    """Runs the provided command in a subprocess.

    This method takes the provided argument cmd_str, splits it into a argument
    list  and then feeds it to a subprocess.Popen constructor along with any
    extra keyword argument provided. It return the subprocess.Popen instance.

    :param cmd_str: string with the command to be executed.
    :type cmd_str: str
    :param kwargs: dictionary of extra parameters to be passed to the
                   subprocess.Popen call
    :type kwargs: dict
    :return: the subprocess.Popen instance
    :rtype: subprocess.Popen
    """
    _LOGGER.debug("Spawning subprocess with command '%s'", cmd_str)
    if os.name == "nt":
        # on windows we can use the string directly
        cmd_list = cmd_str
    else:
        cmd_list = shlex.split(cmd_str)
    proc = subprocess.Popen(cmd_list, **kwargs)
    return proc


def stop_process_with_pid(pid, force=False):
    """Terminates or kills a process with a given pid.

    This method attempts to stop a process with the provided pid.
    If force parameter is False, this it attempts to gracefully terminate
    the process. Otherwise, if force parameter is True it attempts to
    forcefully terminate the process.

    :param pid: pid of the process we want to terminate/kill.
    :type pid: int
    :param force: If True process is forcefully killed, otherwise it is
                  gracefully terminated.
    :type force: bool
    :raises GadgetError: if unable to kill or terminate the process.
    """
    error_msg = "Unable to {0} process '{1}': '{2}'"
    if force:
        if os.name == "nt":
            # windows doesn't have sigkill, we need to use taskkill
            # to terminate a process.
            kill_proc = run_subprocess("taskkill /PID {0} /F".format(pid),
                                       shell=False, stderr=subprocess.PIPE,
                                       universal_newlines=True)
            _, err = kill_proc.communicate()
            if kill_proc.returncode:
                raise GadgetError(error_msg.format("kill", pid, str(err)))
        else:  # posix
            try:
                # send SIGKILL
                # pylint: disable=E1101
                os.kill(pid, signal.SIGKILL)
            except OSError as err:
                raise GadgetError(error_msg.format("kill", pid, str(err)))
    else:
        try:
            # send SIGTERM
            os.kill(pid, signal.SIGTERM)
        except OSError as err:
            raise GadgetError(error_msg.format("terminate", pid, str(err)))
