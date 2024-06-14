import http
import mimetypes
import os

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
STATIC_DIR = os.path.join(THIS_DIR, 'static')

# Handler funcs should take as arguments: (http handler, http (url) path).
# Handler funcs should return: (payload, http code (int), headers (dict)).
# Any return value can be None and it will be defaulted.

def not_found(handler, path):
    return "404 route not found: '%s'." % (path), http.HTTPStatus.NOT_FOUND, None

def redirect(target):
    def handler_func(handler, path):
        return None, http.HTTPStatus.MOVED_PERMANENTLY, {'Location': target}

    return handler_func

def static(handler, path):
    # TEST
    print('Static: ', path)

    # Note that the path is currently a URL path, and therefore separated with slashes.
    parts = path.strip().split('/')

    # Build the static path skipping the '/static' part of the URL path.
    static_path = os.path.join(STATIC_DIR, *parts[2:])

    # TEST
    print("TEST2: ", static_path)

    if (not os.path.isfile(static_path)):
        return "404 static path not found: '%s'." % (path), http.HTTPStatus.NOT_FOUND, None

    with open(static_path, 'rb') as file:
        data = file.read()

    # TEST
    print("Mime: ", mimetypes.guess_type(static_path))

    headers = {}

    mime_info = mimetypes.guess_type(static_path)
    if (mime_info is not None):
        headers['Content-Type'] = mime_info[0]

    return data, None, headers
