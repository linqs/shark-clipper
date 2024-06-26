import base64
import mimetypes

def data_url_to_bytes(data_url):
    extension = ''
    if (data_url.startswith('data:')):
        data_info, data_url = data_url.split(';', 1)
        mime = data_info.split(':')[-1]
        guess_extension = mimetypes.guess_extension(mime)
        if (guess_extension is not None):
            extension = guess_extension

    if (data_url.startswith('base64,')):
        data_url = data_url[7:]

    return base64.b64decode(data_url), extension
