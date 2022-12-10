import gzip
import bz2
import re


def meta_open(file_name, mode, file_format=None, file_compression=None):
    if re.match(r".*\.(t?gz)$", file_name):
        return gzip.open(file_name, mode)
    elif re.match(r".*\.(t?bz2?)$", file_name):
        return bz2.open(file_name, mode)
    else:
        return open(file_name, mode)

    
