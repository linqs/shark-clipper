import datetime
import json
import logging
import os
import re
import shutil
import subprocess

def is_available():
    if (shutil.which('ffmpeg') is None):
        return False

    if (shutil.which('ffprobe') is None):
        return False

    return True

# Get the metadata from a file.
# The metadata will be in a dict, but there are no guarentees on the structure,
# it will just be what ffprobe returns.
def get_all_metadata(path):
    args = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        path,
    ]

    result = subprocess.run(args, capture_output = True)
    if (result.returncode != 0):
        raise ValueError("ffmpeg did not exit cleanly.\n--- stdout ---\n%s\n---\n--- stderr ---%s\n---" % (result.stdout, result.stderr))

    stdout, _ = _run(args, 'ffprobe')
    return json.loads(stdout)

# Get metadata that we believe is important.
def get_key_metadata(path):
    data = {}
    all_metadata = get_all_metadata(path)

    if ('format' in all_metadata):
        tags = all_metadata['format'].get('tags', {})

        if ('location' in tags):
            text_location = tags['location'].strip()
            data['location_raw'] = text_location

            match = re.search(r'^((?:\+|-)?\d+\.\d+)((?:\+|-)?\d+\.\d+)/?$', text_location)
            if (match is not None):
                data['location'] = {
                    'latitude': match.group(1),
                    'longitude': match.group(2),
                }

        if ('creation_time' in tags):
            text_time = tags['creation_time'].strip()
            data['start_time_raw'] = text_time

            try:
                parsed_time = datetime.datetime.fromisoformat(text_time)
                data['start_time_unix'] = int(parsed_time.timestamp())
            except:
                pass

    return data

# Perform a low(ish) quality encoding so we can quickly work with with a video in a browser.
def transcode_for_web(in_path, out_path, video_id):
    if (not out_path.endswith('.mp4')):
        out_path = os.path.splitext(out_path)[0] + '.mp4'

    metadata = get_key_metadata(in_path)

    # Add additional metadata.
    metadata['video_id'] = video_id
    metadata['encoded_at_unix'] = int(datetime.datetime.now().timestamp())

    args = [
        'ffmpeg',
        # Input file.
        '-i', in_path,
        # Override any existing output.
        '-y',
        # Only map video streams.
        '-map', '0:v',
        # Use h.264
        '-c:v', 'libx264',
        # Scale down the video to 720p.
        '-vf', 'scale=1280x720',
        # Use fast presets.
        '-preset', 'ultrafast',
        # Use a lossy CRF.
        '-crf', '28',
        # MP4
        '-f', 'mp4',
        # Allow arbitrary metadata.
        '-movflags', '+use_metadata_tags',
        # Metadata
        '-metadata', "shark-clipper=%s" % (json.dumps(metadata)),
        # Output file.
        out_path,
    ]

    _run(args, 'ffmpeg')

    return out_path

def _run(args, name):
    result = subprocess.run(args, capture_output = True)
    if (result.returncode != 0):
        raise ValueError("%s did not exit cleanly.\n--- stdout ---\n%s\n---\n--- stderr ---%s\n---" % (name, result.stdout, result.stderr))

    return result.stdout, result.stderr
