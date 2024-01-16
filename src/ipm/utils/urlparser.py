from urllib.parse import urlparse


def is_valid_url(uri: str):
    parsed_uri = urlparse(uri)
    return parsed_uri.scheme and parsed_uri.netloc
