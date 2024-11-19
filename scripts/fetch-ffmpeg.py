#!/usr/bin/env python3

"""
Fetch FFmpeg binaries from our resources repository and put them in the root directory.
"""

import argparse
import gzip
import platform
import os
import shutil
import sys
import urllib.request

import util

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(THIS_DIR, '..'))

OS_DIRNAME_MAPPING = {
    'Darwin': 'mac',
    'Linux': 'linux',
    'Windows': 'windows',
}

# Contains format strings for: (os dir, bin name).
BASE_URL = 'https://github.com/linqs/shark-clipper-resources/raw/refs/heads/main/ffmpeg/%s/%s.gz'

def fetch():
    temp_dir = util.get_temp_path(prefix = 'sharkclipper-fetch-ffmpeg-')
    os_name = platform.system()

    dirname = OS_DIRNAME_MAPPING.get(os_name, None)
    if (dirname is None):
        print("Unknown operating system: '%s'." % (os_name))
        return 1

    for bin_name in ['ffmpeg', 'ffprobe']:
        # Note that this is a URL, not a system path.
        url = BASE_URL % (dirname, bin_name)

        response = urllib.request.urlopen(url)

        out_gz_path = os.path.join(temp_dir, bin_name + '.gz')
        with open(out_gz_path, 'wb') as file:
            file.write(response.read())

        out_path = os.path.join(ROOT_DIR, bin_name)
        _gunzip(out_gz_path, out_path)
        os.chmod(out_path, 0o775)

    return 0

def _gunzip(source, dest):
    with gzip.open(source, 'rb') as in_file:
        with open(dest, 'wb') as out_file:
            shutil.copyfileobj(in_file, out_file)

def main():
    args = _get_parser().parse_args()
    return fetch()

def _get_parser():
    parser = argparse.ArgumentParser(description = __doc__.strip())
    return parser

if __name__ == '__main__':
    sys.exit(main())
