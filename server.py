# TEST
import argparse
import http
import http.server
import json
import os
import re
import sys
import time
import traceback
import urllib.parse

# TEST
import handlers

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

DEFAULT_PORT = 12345
ENCODING = 'utf8'

# Routes for the server.
# First matching route will be used.
# Handler functions should take two arguments: the handler, the path.
# (route regex, handler function)
ROUTES = [
    (r'^/$', handlers.redirect('/static/index.html')),
    (r'^/index.html$', handlers.redirect('/static/index.html')),
    (r'^/static$', handlers.redirect('/static/index.html')),
    (r'^/static/$', handlers.redirect('/static/index.html')),

    (r'^/favicon.ico$', handlers.redirect('/static/favicon.ico')),

    (r'^/static/', handlers.static),
]

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        raw_content = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(raw_content)

        # TEST
        print('---')
        print(self.path)
        print('---')

        code = http.HTTPStatus.OK
        headers = {}

        result = self._route(self.path)
        if (result is None):
            # All handling was done internally, the response is complete.
            return

        # A standard response structure was returned, continue processing.
        payload, response_code, response_headers = result

        if (isinstance(payload, dict)):
            payload = json.dumps(payload)
            headers['Content-Type'] = 'application/json'

        if (isinstance(payload, str)):
            payload = payload.encode(ENCODING)

        if (payload is not None):
            headers['Content-Length'] = len(payload)

        if (response_headers is not None):
            for key, value in response_headers.items():
                headers[key] = value

        if (response_code is not None):
            code = response_code

        self.send_response(code)

        for (key, value) in headers.items():
            self.send_header(key, value)
        self.end_headers()

        if (payload is not None):
            self.wfile.write(payload)

    def do_POST(self):
        self.do_GET()

    def _route(self, path):
        path = path.strip()

        target = handlers.not_found
        for (regex, handler_func) in ROUTES:
            if (re.search(regex, path) is not None):
                target = handler_func
                break

        try:
            return target(self, path)
        except:
            print("Error on path '%s', handler '%s'.", path, str(target))
            traceback.print_exc()

            return None, http.HTTPStatus.INTERNAL_SERVER_ERROR, None

def run(args):
    print("Serving on 127.0.0.1:%d ." % (args.port))

    server = http.server.HTTPServer(('', args.port), Handler)
    server.serve_forever()

    return 0

def main():
    return run(_get_parser().parse_args())

def _get_parser():
    parser = argparse.ArgumentParser(description = 'Run a web GUI for clipping fin images from shark videos.')

    parser.add_argument('--port', dest = 'port',
        action = 'store', type = int, default = DEFAULT_PORT,
        help = 'Port to launch the web GUI on (default: %(default)s).')

    return parser

if __name__ == '__main__':
    sys.exit(main())
