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

    return parser

if __name__ == '__main__':
    sys.exit(main())
