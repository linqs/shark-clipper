import http
import mimetypes
import os

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
STATIC_DIR = os.path.join(THIS_DIR, 'static')

# Handler funcs should take as arguments: (http handler, http (url) path, **kwargs).
# Handler funcs should return: (payload, http code (int), headers (dict)).
# Any return value can be None and it will be defaulted.

def not_found(handler, path, **kwargs):
    return "404 route not found: '%s'." % (path), http.HTTPStatus.NOT_FOUND, None

def redirect(target):
    def handler_func(handler, path, **kwargs):
        return None, http.HTTPStatus.MOVED_PERMANENTLY, {'Location': target}

    return handler_func

# Get a static (bundled) file.
def static(handler, path, **kwargs):
    # Note that the path is currently a URL path, and therefore separated with slashes.
    parts = path.strip().split('/')

    # Build the static path skipping the '/static' part of the URL path.
    static_path = os.path.join(STATIC_DIR, *parts[2:])

    return _serve_file(static_path, "static path not found: '%s'." % (path))

# Get a temp file that we create/work with.
def temp(handler, path, temp_dir = None, **kwargs):
    # Note that the path is currently a URL path, and therefore separated with slashes.
    parts = path.strip().split('/')

    # Build the temp path skipping the '/temp' part of the URL path.
    temp_path = os.path.join(temp_dir, *parts[2:])

    return _serve_file(temp_path, "temp path not found: '%s'." % (path))

# Prep a video for work, and get metadata about it.
def video(handler, path,
        temp_id = None, uploaded_path = None, uploaded_relpath = None, **kwargs):
    # TODO - encode

    # TEST
    print("TEST - video")

    response = {
        'id': temp_id,
        'path': '/temp/' + uploaded_relpath,
        'type': 'video/mp4',
    }

    # TEST
    print(response)

    return response, None, None

def _serve_file(path, not_found_message = None):
    if (not os.path.isfile(path)):
        if (not_found_message is None):
            not_found_message = "path not found: '%s'." % (path)
        return "404 %s" % not_found_message, http.HTTPStatus.NOT_FOUND, None

    with open(path, 'rb') as file:
        data = file.read()

    headers = {}

    mime_info = mimetypes.guess_type(path)
    if (mime_info is not None):
        headers['Content-Type'] = mime_info[0]

    return data, None, headers
