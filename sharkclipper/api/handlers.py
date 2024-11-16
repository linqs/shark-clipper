import datetime
import http
import io
import json
import logging
import mimetypes
import os

import PIL.ExifTags
import PIL.Image

import sharkclipper.util.ffmpeg
import sharkclipper.util.file
import sharkclipper.util.net
import sharkclipper.util.version

STATIC_DIR = os.path.join(sharkclipper.util.file.get_root_dir(), 'static')

METADATA_FILENAME_SUFFIX = '_metadata.json'

EXIF_DATETIME_FORMAT = '%Y:%m:%d %H:%M:%S'

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

    return _serve_file(static_path, "static path not found: '%s'." % (path), **kwargs)

# Get a temp file that we create/work with.
def temp(handler, path, temp_dir = None, **kwargs):
    # Note that the path is currently a URL path, and therefore separated with slashes.
    parts = path.strip().split('/')

    # Build the temp path skipping the '/temp' part of the URL path.
    temp_path = os.path.join(temp_dir, *parts[2:])

    return _serve_file(temp_path, "temp path not found: '%s'." % (path), **kwargs)

# Get the server version.
def version(handler, path, **kwargs):
    return sharkclipper.util.version.get_version(), None, None

# Prep a video for work, and get metadata about it.
def video(handler, path,
        video_id = None, temp_dir = None,
        filename = None, uploaded_path = None, metadata = None,
        **kwargs):
    new_filename = video_id + '.mp4'
    new_path = os.path.join(temp_dir, 'webencode', new_filename)
    os.makedirs(os.path.dirname(new_path), exist_ok = True)

    try:
        new_path, key_metadata, all_metadata = sharkclipper.util.ffmpeg.transcode_for_web(uploaded_path, new_path, video_id)
    except Exception as ex:
        message = "Failed to encode video '%s' for web." % (filename)
        logging.error(message, exc_info = ex)
        return message, http.HTTPStatus.INTERNAL_SERVER_ERROR, None

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
    now = datetime.datetime.now()

    # Out directory name is video name plus prefix of id.
    id_prefix = data['video']['id'].split('-')[0]
    out_dir = os.path.join(out_dir, data['video']['name'] + '-' + id_prefix)

    # If directory already exists, remake to avoid conflicts.
    if (os.path.exists(out_dir)):
        sharkclipper.util.file.remove_dirent(out_dir)

    os.makedirs(out_dir, exist_ok = True)

    # Save screenshots.
    screenshots_metadata = []
    for screenshot in data.get('screenshots', {}).values():
        image_bytes, extension = sharkclipper.util.net.data_url_to_bytes(screenshot['dataURL'])
        path = os.path.join(out_dir, screenshot['name'] + extension)

        metadata = {
            'video': data.get('key_metadata', {}).copy(),
            'image': screenshot.copy(),
        }
        del metadata['image']['dataURL']

        screenshots_metadata.append(metadata)

        image = PIL.Image.open(io.BytesIO(image_bytes))
        exif = _set_exif_data(image, metadata, now)
        image.save(path, exif = exif)

    # Save web-encoded video with new metadata.
    video_metadata = data['video'].copy()
    video_metadata['screenshots'] = [metadata['image'] for metadata in screenshots_metadata]
    old_path = os.path.join(temp_dir, 'webencode', data['video']['id'] + '.mp4')
    new_path = os.path.join(out_dir, data['video']['name'] + '.mp4')
    sharkclipper.util.ffmpeg.copy_with_metadata(old_path, new_path, video_metadata)

    # Save all metadata.
    metadata = {
        'saved_at_unix': int(now.timestamp()),
        'video': data['video'],
        'screenshots': screenshots_metadata,
        'key': data.get('key_metadata', {}),
        'all': data.get('all_metadata', {}),
    }
    metadata_path = os.path.join(out_dir, data['video']['name'] + METADATA_FILENAME_SUFFIX)
    with open(metadata_path, 'w') as file:
        json.dump(metadata, file, indent = 4)

    return {}, None, None

def _set_exif_data(image, metadata, now):
    exif = image.getexif()

    # Write all metadata as a JSON string in the user comment.
    # This seems correct, but some tools will complain about the encoding:
    # https://github.com/python-pillow/Pillow/issues/5254
    exif[PIL.ExifTags.Base.UserComment] = json.dumps(metadata)

    # Set original (taken) time.
    if ('time' in metadata['image']):
        create_time = datetime.datetime.fromtimestamp(metadata['image']['time'], tz = datetime.timezone.utc)
        exif[PIL.ExifTags.Base.DateTimeOriginal] = _get_exif_timestamp(create_time)
        exif[PIL.ExifTags.Base.DateTimeDigitized] = _get_exif_timestamp(create_time)

    # Set creation time (now).
    exif[PIL.ExifTags.Base.DateTime] = _get_exif_timestamp(now)

    return exif

def _get_exif_timestamp(time):
    # Set timezone to utc.
    time = time.astimezone(datetime.timezone.utc)

    # Format.
    return time.strftime(EXIF_DATETIME_FORMAT)

def _serve_file(path, not_found_message = None, range_header = None, **kwargs):
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

    code = http.HTTPStatus.OK

    data_length = len(data)
    range_parts = _parseRange(range_header, data_length)
    if (range_parts is not None):
        data = data[range_parts[0]:(range_parts[1] + 1)]
        code = http.HTTPStatus.PARTIAL_CONTENT
        headers['Content-Range'] = "bytes %d-%d/%d" % (range_parts[0], range_parts[1], data_length)

    return data, code, headers

# Parse the range header.
# Return None if a single byte range could not be parsed (multi-ranges are not supported),
# else return [startByteIndex, endByteIndex] (inclusive).
# Note that the inclusivity means that these are not the same as a Python list slice
# (you will need to add one to the end index).
# If not present, startByteIndex will be defaulted to 0 and endByteIndex will be data_length.
def _parseRange(raw_range_header, data_length):
    try:
        return _parseRangeHelper(raw_range_header, data_length)
    except Exception as ex:
        logging.warn("Cannot parse range header '%s': '%s'." % (raw_range_header, ex))
        return None

def _parseRangeHelper(raw_range_header, data_length):
    if (raw_range_header is None):
        return None

    text = str(raw_range_header).strip().lower()

    parts = [part.strip() for part in text.split('=')]
    if (len(parts) != 2):
        raise ValueError('Bad unit split.')

    units, ranges = parts
    if (units != 'bytes'):
        raise ValueError('Units is not bytes.')

    parts = [part.strip() for part in ranges.split(',')]
    if (len(parts) != 1):
        raise ValueError('Multipart ranges not supported.')

    parts = [part.strip() for part in parts[0].split('-')]
    if (len(parts) != 2):
        raise ValueError('Range does not have exactly two components.')

    start = parts[0]
    if (start == ''):
        start = 0
    start = int(start)

    end = parts[1]
    if (end == ''):
        end = (data_length - 1)
    end = int(end)

    return [start, end]
