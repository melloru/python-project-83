from urllib.parse import urlparse
import re


VALID_SCHEMES = ['http', 'https']
PATTERN = r"[^a-zA-Z]"


def validate(url):
    parse_result = {}
    parse_url = urlparse(url)
    scheme = parse_url.scheme
    netloc = parse_url.netloc
    tld = netloc.split('.')[-1]
    if scheme not in VALID_SCHEMES or re.search(PATTERN, tld) or len(tld) < 2:
        parse_result['error_name'] = "Некорректный URL"
    else:
        parse_result['netloc'] = f"{scheme}://{netloc}"
    return parse_result
