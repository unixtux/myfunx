#!/bin/env python3

import re
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0'
}
def parse_la_repubblica() -> list[tuple[str, str]]:
    url = 'https://www.repubblica.it/'
    html = requests.get(url, headers=HEADERS).text
    links = re.findall(r'<.*?class="entry__title">(.|\n)*?<\s*a\s*href\s*=\s*"\s*(.*?)\s*"\s*>\s*\n\s*(\w.*)', html)
    all_the_links = []
    for tp in links:
        tp = tp[1:]
        all_the_links.append(tp)
    return all_the_links
