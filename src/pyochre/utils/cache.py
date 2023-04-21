import os.path
import requests


def fetch_from_url(url, ochre_path):
    """
    Download the url as a file and save it to the cache.
    Return the path.
    """
    ofname = os.path.join(
        ochre_path,
        "cache",
        os.path.basename(url)
    )
    if not os.path.exists(ofname):
        with requests.get(
                url,
                stream=True
        ) as resp, open(ofname, "wb") as ofd:
            for chunk in resp.iter_content(100000):
                ofd.write(chunk)
    return ofname
