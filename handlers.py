import datetime
import http
import json
import mimetypes
import os
import shutil

import ffmpeg
import util

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
STATIC_DIR = os.path.join(THIS_DIR, 'static')

METADATA_FILENAME = 'metadata.json'

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
        video_id = None, temp_dir = None,
        filename = None, uploaded_path = None, metadata = None,
        **kwargs):
    new_filename = video_id + '.mp4'
    new_path = os.path.join(temp_dir, 'webencode', new_filename)
    os.makedirs(os.path.dirname(new_path), exist_ok = True)

    new_path, key_metadata, all_metadata = ffmpeg.transcode_for_web(uploaded_path, new_path, video_id)

    response = {
        'video_id': video_id,
        'original_name': os.path.splitext(filename)[0],
        'path': '/'.join(['/temp', 'webencode', new_filename]),
        'type': 'video/mp4',
        'key_metadata': key_metadata,
        'all_metadata': all_metadata,
    }

    return response, None, None

# Save the temp video and any screenshots to disk.
def save(handler, path, temp_dir = None, data = None, out_dir = None, **kwargs):
    # Suffix the base out dir for this specific video.
    out_dir = os.path.join(out_dir, data['video']['id'])
    os.makedirs(out_dir, exist_ok = True)

    # Save (copy) web-encoded video.
    old_path = os.path.join(temp_dir, 'webencode', data['video']['id'] + '.mp4')
    new_path = os.path.join(out_dir, data['video']['name'] + '.mp4')
    shutil.copy2(old_path, new_path)

    # Save screenshots.
    for screenshot in data.get('screenshots', {}).values():
        image_bytes, extension = util.data_url_to_bytes(screenshot['dataURL'])

        path = os.path.join(out_dir, screenshot['name'] + extension)
        with open(path, 'wb') as file:
            file.write(image_bytes)

    # Save metadata.
    metadata_path = os.path.join(out_dir, METADATA_FILENAME)
    with open(metadata_path, 'w') as file:
        metadata = {
            'saved_at_unix': int(datetime.datetime.now().timestamp()),
            'key': data.get('key_metadata', {}),
            'all': data.get('all_metadata', {}),
        }
        json.dump(metadata, file, indent = 4)

    return {}, None, None

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
