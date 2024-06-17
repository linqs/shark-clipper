#!/usr/bin/env python3

import argparse
import sys

import server
import ffmpeg

def check_requirements(**kwargs):
    result = True

    if (not ffmpeg.is_available()):
        print("Could not locate 'ffmpeg'.")
        result = False

    return result

def main():
    args = vars(_get_parser().parse_args())

    if (not check_requirements(**args)):
        print("Not all requirements to run tool are met.")
        return 1

    server.run(**args)

    return 0

def _get_parser():
    parser = argparse.ArgumentParser(description = 'Run a web GUI for clipping fin images from shark videos.')

    parser.add_argument('--port', dest = 'port',
        action = 'store', type = int, default = server.DEFAULT_PORT,
        help = 'Port to launch the web GUI on (default: %(default)s).')

    parser.add_argument('--out', dest = 'out_dir',
        action = 'store', type = str, default = server.DEFAULT_OUT_DIRNAME,
        help = 'Where to store output files (default: %(default)s).')

    parser.add_argument('--no-cleanup', dest = 'cleanup_temp',
        action = 'store_false', default = True,
        help = 'Do not cleanup any intermitent results (good for debugging) (default: %(default)s).')

    return parser

if __name__ == '__main__':
    sys.exit(main())
