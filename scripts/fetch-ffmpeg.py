#!/usr/bin/env python3

import argparse
import platform
import os
import shutil
import sys
import tarfile
import urllib.request
import zipfile

import util

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(THIS_DIR, '..'))

LINUX_TARGET = 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
MAC_TARGET_FFMPEG = 'https://evermeet.cx/ffmpeg/ffmpeg-7.0.1.zip'
MAC_TARGET_FFPROBE = 'https://evermeet.cx/ffmpeg/ffprobe-7.0.1.zip'
WIN_TARGET = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip'

def _fetch_linux():
    temp_dir = util.get_temp_path(prefix = 'shark-clipper-fetch-ffmpeg-')

    response = urllib.request.urlopen(LINUX_TARGET)

    archive_path = os.path.join(temp_dir, 'ffmpeg-release-amd64-static.tar.xz')
    with open(archive_path, 'wb') as file:
        file.write(response.read())

    extract_dir = os.path.join(temp_dir, 'extract')
    with tarfile.open(archive_path) as archive:
        archive.extractall(path = extract_dir, filter = 'data')

    versioned_dirname = os.listdir(extract_dir)[0]

    for name in ['ffmpeg', 'ffprobe']:
        in_path = os.path.join(extract_dir, versioned_dirname, name)
        out_path = os.path.join(ROOT_DIR, name)

        shutil.copy2(in_path, out_path)

    return 0

def _fetch_mac():
    temp_dir = util.get_temp_path(prefix = 'shark-clipper-fetch-ffmpeg-')
    extract_dir = os.path.join(temp_dir, 'extract')

    for (name, target) in [('ffmpeg', MAC_TARGET_FFMPEG), ('ffprobe', MAC_TARGET_FFPROBE)]:
        response = urllib.request.urlopen(target)

        archive_path = os.path.join(temp_dir, name + '.zip')
        with open(archive_path, 'wb') as file:
            file.write(response.read())

        with zipfile.ZipFile(archive_path, 'r') as archive:
            archive.extractall(extract_dir)

        in_path = os.path.join(extract_dir, name)
        out_path = os.path.join(ROOT_DIR, name)

        shutil.copy2(in_path, out_path)

    return 0

def _fetch_windows():
    temp_dir = util.get_temp_path(prefix = 'shark-clipper-fetch-ffmpeg-')

    response = urllib.request.urlopen(WIN_TARGET)

    archive_path = os.path.join(temp_dir, 'ffmpeg-master-latest-win64-gpl.zip')
    with open(archive_path, 'wb') as file:
        file.write(response.read())

    extract_dir = os.path.join(temp_dir, 'extract')
    with zipfile.ZipFile(archive_path, 'r') as archive:
        archive.extractall(extract_dir)

    versioned_dirname = os.listdir(extract_dir)[0]

    for name in ['ffmpeg', 'ffprobe']:
        in_path = os.path.join(extract_dir, versioned_dirname, 'bin', name + '.exe')
        out_path = os.path.join(ROOT_DIR, name)

        shutil.copy2(in_path, out_path)

    return 0

def fetch():
    os_name = platform.system()

    if (os_name == 'Darwin'):
        return _fetch_mac()
    elif (os_name == 'Linux'):
        return _fetch_linux()
    elif (os_name == 'Windows'):
        return _fetch_windows()

    print("Unknown operating system: '%s'." % (os_name))
    return 1

def main():
    args = _get_parser().parse_args()
    return fetch()

def _get_parser():
    parser = argparse.ArgumentParser(description = "Get the sverer's version.")
    return parser

if __name__ == '__main__':
    sys.exit(main())
