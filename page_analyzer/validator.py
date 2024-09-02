from urllib.parse import urlparse


def validate(url):
    valid_schemes = ['http', 'https']
    errors = {}
    parse_url = urlparse(url["name"])
    scheme = parse_url.scheme
    netloc = parse_url.netloc
    if not (scheme in valid_schemes and netloc):
        errors['name'] = "Некорректный URL"
    return errors
