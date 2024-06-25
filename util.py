import atexit
import base64
import logging
import mimetypes
import os
import re
import shutil
import tempfile
import uuid

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

PACKAGE_CONFIG_PATH = os.path.join(THIS_DIR, 'pyproject.toml')
UNKNOWN_VERSION = '?.?.?'
VERSION_REGEX = r'^version\s*=\s*["\'](\d+\.\d+\.\d+)["\']$'

def get_uuid():
    return str(uuid.uuid4())

def get_version():
    if (not os.path.isfile(PACKAGE_CONFIG_PATH)):
        logging.error("Could not find version file: '%s'." % (PACKAGE_CONFIG_PATH))
        return UNKNOWN_VERSION

    with open(PACKAGE_CONFIG_PATH, 'r') as file:
        for line in file:
            line = line.strip()
            if (line == ''):
                continue

            match = re.search(VERSION_REGEX, line)
            if (match is not None):
                return match.group(1)

    return UNKNOWN_VERSION

def get_temp_path(prefix = '', suffix = '', rm = True, mkdir = True):
    """
    Get a path to a valid temp dirent.
    mkdir will determine if this directory will exist on return.
    If rm is True, then the dirent will be attempted to be deleted on exit
    (no error will occur if the path is not there).
    """

    path = None
    while ((path is None) or os.path.exists(path)):
        path = os.path.join(tempfile.gettempdir(), prefix + str(uuid.uuid4()) + suffix)

    if (mkdir):
        os.makedirs(path, exist_ok = True)

    if (rm):
        atexit.register(remove_dirent, path)

    return path

def remove_dirent(path):
    if (not os.path.exists(path)):
        return

    if (os.path.isfile(path) or os.path.islink(path)):
        os.remove(path)
    elif (os.path.isdir(path)):
        shutil.rmtree(path)
    else:
        raise ValueError("Unknown type of dirent: '%s'." % (path))

def data_url_to_bytes(data_url):
    extension = ''
    if (data_url.startswith('data:')):
        data_info, data_url = data_url.split(';', 1)
        mime = data_info.split(':')[-1]
        guess_extension = mimetypes.guess_extension(mime)
        if (guess_extension is not None):
            extension = guess_extension

    if (data_url.startswith('base64,')):
        data_url = data_url[7:]

    return base64.b64decode(data_url), extension
