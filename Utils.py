from datetime import datetime
import hashlib
import os


def dict_defaulter(item: dict, fields):
    for x in fields:
        item.setdefault(x, None)
    return item


def rear_replace(string, old, new, occurrence):
    li = string.rsplit(old, occurrence)
    return new.join(li)


def compute_file_hash(filename: str, sha: str = 'sha1', bytes_to_read=None):
    """Compute file hash.
    Result is expressed as hexdigest().
    :param filename: filename path
    :param sha: hashing function among the following in hashlib:
        md5(), sha1(), sha224(), sha256(), sha384(), and sha512()
        function name shall be passed as string, e.g. 'sha1'.
    :param bytes_to_read: only the first bytes_to_read will be considered;
        if file size is smaller, the whole file will be considered.
    :type bytes_to_read: None or int
    """
    if filename is None:
        return None
    if not os.path.isfile(filename):
        return None

    size = os.path.getsize(filename)
    if bytes_to_read is None:
        bytes_to_read = size
    else:
        bytes_to_read = min(bytes_to_read, size)
    step = 1 << 20

    shas = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
    assert sha in shas
    sha = getattr(hashlib, sha)()  # sha instance

    with open(filename, 'rb') as f:
        while bytes_to_read > 0:
            read_bytes = f.read(min(bytes_to_read, step))
            assert read_bytes  # make sure we actually read bytes
            bytes_to_read -= len(read_bytes)
            sha.update(read_bytes)
    return sha.hexdigest()


def get_hash_string(text):
    return hashlib.sha256(text.encode()).hexdigest()


def get_now_unix():
    return datetime.now().timestamp()
