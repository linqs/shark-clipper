import http
import http.server
import json
import os
import re
import traceback

import handlers
import util

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

DEFAULT_PORT = 12345
ENCODING = 'utf-8'

# Routes for the server.
# First matching route will be used.
# Handler functions should take two arguments: the handler, the path.
# (route regex, handler function, **kwarags)
ROUTES = [
    (r'^/$', handlers.redirect('/static/index.html')),
    (r'^/index.html$', handlers.redirect('/static/index.html')),
    (r'^/static$', handlers.redirect('/static/index.html')),
    (r'^/static/$', handlers.redirect('/static/index.html')),

    (r'^/favicon.ico$', handlers.redirect('/static/favicon.ico')),

    (r'^/static/', handlers.static),
    (r'^/temp/', handlers.temp),
    (r'^/video$', handlers.video),
]

class Handler(http.server.BaseHTTPRequestHandler):
    _temp_dir = util.get_temp_path(prefix = 'shark-clipper', rm = True)

    def log_message(self, format, *args):
        return

    def do_GET(self):
        self._do_request()

    def do_POST(self):
        params = self._read_post_file()
        self._do_request(**params)

    def _read_post_file(self):
        filename = self.headers.get('shark-clipper-filename', '')
        if (filename == ''):
            return {}

        length = int(self.headers.get('content-length', 0))
        if (length <= 0):
            return {}

        video_id = util.get_uuid()
        temp_dir = os.path.join(Handler._temp_dir, 'raw', video_id)
        os.makedirs(temp_dir, exist_ok = True)

        temp_path = os.path.join(temp_dir, filename)
        with open(temp_path, 'wb') as file:
            file.write(self.rfile.read(length))

        return {
            'video_id': video_id,
            'filename': filename,
            'uploaded_relpath': '/'.join([video_id, filename]),
            'uploaded_path': temp_path,
        }

    def _do_request(self, **kwargs):
        # TEST
        print(self.path)

        code = http.HTTPStatus.OK
        headers = {}

        result = self._route(self.path, **kwargs)
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

    def _route(self, path, **kwargs):
        path = path.strip()

        target = handlers.not_found
        for (regex, handler_func) in ROUTES:
            if (re.search(regex, path) is not None):
                target = handler_func
                break

        try:
            return target(self, path, temp_dir = Handler._temp_dir, **kwargs)
        except:
            print("Error on path '%s', handler '%s'.", path, str(target))
            traceback.print_exc()

            return None, http.HTTPStatus.INTERNAL_SERVER_ERROR, None

def run(port = DEFAULT_PORT, **kwargs):
    print("Serving on 127.0.0.1:%d ." % (port))

    server = http.server.HTTPServer(('', port), Handler)
    server.serve_forever()
