import http
import http.server
import json
import logging
import os
import re

import sharkclipper.api.handlers
import sharkclipper.util.file
import sharkclipper.util.rand

DEFAULT_PORT = 12345
ENCODING = 'utf-8'

DEFAULT_OUT_DIRNAME = 'out'

# Routes for the server.
# First matching route will be used.
# Handler functions should take two arguments: the handler, the path.
# (route regex, handler function, **kwarags)
ROUTES = [
    (r'^/$', sharkclipper.api.handlers.redirect('/static/index.html')),
    (r'^/index.html$', sharkclipper.api.handlers.redirect('/static/index.html')),
    (r'^/static$', sharkclipper.api.handlers.redirect('/static/index.html')),
    (r'^/static/$', sharkclipper.api.handlers.redirect('/static/index.html')),

    (r'^/favicon.ico$', sharkclipper.api.handlers.redirect('/static/favicon.ico')),

    (r'^/static/', sharkclipper.api.handlers.static),
    (r'^/temp/', sharkclipper.api.handlers.temp),
    (r'^/version$', sharkclipper.api.handlers.version),
    (r'^/video$', sharkclipper.api.handlers.video),
    (r'^/save$', sharkclipper.api.handlers.save),
]

class Handler(http.server.BaseHTTPRequestHandler):
    _temp_dir = None
    _out_dir = None

    @classmethod
    def init(cls, out_dir = DEFAULT_OUT_DIRNAME, cleanup_temp = True, **kwargs):
        cls._temp_dir = sharkclipper.util.file.get_temp_path(prefix = 'shark-clipper', rm = cleanup_temp)
        cls._out_dir = os.path.abspath(out_dir)

    def log_message(self, format, *args):
        return

    def handle(self):
        """
        Override handle() to ignore dropped connections.
        """

        try:
            return http.server.BaseHTTPRequestHandler.handle(self)
        except BrokenPipeError as ex:
            logging.info("Connection closed on the client side.")

    def do_GET(self):
        self._do_request()

    def do_POST(self):
        params = {}

        if (self.headers.get('shark-clipper-upload', False)):
            params = self._read_post_file()
        elif (self.headers.get('shark-clipper-save', False)):
            params = self._read_json_body()

        self._do_request(**params)

    def _read_json_body(self):
        length = int(self.headers.get('content-length', 0))
        if (length <= 0):
            return {}

        data = json.loads(self.rfile.read(length))

        return {
            'data': data,
        }

    def _read_post_file(self):
        filename = self.headers.get('shark-clipper-filename', '')
        if (filename == ''):
            return {}

        length = int(self.headers.get('content-length', 0))
        if (length <= 0):
            return {}

        video_id = sharkclipper.util.rand.get_uuid()
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
        logging.debug("Serving: " + self.path)

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

        target = sharkclipper.api.handlers.not_found
        for (regex, handler_func) in ROUTES:
            if (re.search(regex, path) is not None):
                target = handler_func
                break

        try:
            return target(self, path,
                    temp_dir = Handler._temp_dir, out_dir = Handler._out_dir,
                    **kwargs)
        except Exception as ex:
            logging.error("Error on path '%s', handler '%s'.", path, str(target), exc_info = ex)

            return str(ex), http.HTTPStatus.INTERNAL_SERVER_ERROR, None

def run(port = DEFAULT_PORT, **kwargs):
    logging.info("Serving on http://127.0.0.1:%d ." % (port))

    Handler.init(**kwargs)

    server = http.server.ThreadingHTTPServer(('', port), Handler)
    server.serve_forever()
