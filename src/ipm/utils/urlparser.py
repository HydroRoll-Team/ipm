from urllib.parse import urlparse


def is_valid_url(uri: str) -> bool:
    parsed_uri = urlparse(uri)
    return bool(parsed_uri.scheme and parsed_uri.netloc)
