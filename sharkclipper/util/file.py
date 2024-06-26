import atexit
import os
import shutil
import tempfile

import sharkclipper.util.rand

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', '..'))

def get_root_dir():
    return ROOT_DIR

def get_temp_path(prefix = '', suffix = '', rm = True, mkdir = True):
    """
    Get a path to a valid temp dirent.
    mkdir will determine if this directory will exist on return.
    If rm is True, then the dirent will be attempted to be deleted on exit
    (no error will occur if the path is not there).
    """

    path = None
    while ((path is None) or os.path.exists(path)):
        path = os.path.join(tempfile.gettempdir(), prefix + sharkclipper.util.rand.get_uuid() + suffix)

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
