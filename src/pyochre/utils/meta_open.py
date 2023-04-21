import gzip
import bz2
import re
import os.path
from io import BytesIO, StringIO
import requests


def meta_open(file_name, mode, file_format=None, file_compression=None):
    is_url = re.match(r"^https?://.*$", file_name)
    IO = StringIO if "t" in mode else BytesIO
    if is_url:
        resp = requests.get(file_name, stream=True)
        if resp.status_code == 404:
            return None
        fd = IO(resp.content.decode("utf-8")) if "t" in mode else IO(resp.content)
    else:
        if "w" not in mode and not os.path.exists(file_name):
            raise Exception("Cannot read from or append to non-existent file '{}'".format(file_name))
        fd = open(file_name, mode=mode)
    if re.match(r".*\.(t?gz)$", file_name):
        return gzip.open(file_name, mode=mode)
    elif re.match(r".*\.(t?bz2?)$", file_name):
        return bz2.open(file_name, mode=mode)
    else:
        return fd

    
