# -*- coding: utf-8 -*-

"""
HTTP(s) monitoring webpage.
(c) Dung Nguyen (nhymxu)
https://www.journaldev.com/23494/python-string-templateÍ
"""

import argparse
import json
from configparser import ConfigParser
from os import path
import urllib.error
import urllib.parse
import urllib.request
from hashlib import md5
from datetime import datetime
from chevron.renderer import render


COMMON_CONFIG = []
TMP_RESULT = {
    'success': [],
    'failed': []
}


def make_request(url="", method="GET"):
    """
    Send API request ( json type )

    :param url:
    :param method:
    :return:
    """

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            resp_code = response.getcode()
            return resp_code
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())
    except urllib.error.URLError as e:
        print(e.reason)

    return False


def get_config(config_path='config.ini'):
    """
    Read and parsing config from ini file.

    :return:
    """
    global COMMON_CONFIG

    if not path.exists(config_path):
        raise RuntimeError("config file not found")

    config = ConfigParser()
    config.read(config_path)

    if "common" not in config:
        raise Exception("Common config not found.")

    COMMON_CONFIG = config['common']

    config_sections = config.sections()
    config_sections.remove("common")

    if not config_sections:
        raise Exception("Empty site to check")

    return config, config_sections


def write_to_file(url, display, is_valid):
    file_name = path.join(
        'tmp',
        '{}_{}.json'.format(is_valid, md5(url.encode('utf-8')).hexdigest())
    )
    data = {
        'title': display,
        'url': url,
        'is_valid': is_valid,
        'check_time': datetime.now()
    }

    with open(file_name, 'w') as fp:
        fp.write(json.dumps(data, indent=2))


def process_section(section_data):
    """
    Process all record in section

    :param section_data:
    :return:
    """
    url = section_data["url"].strip()
    display = section_data.get("display", url).strip()
    expected_code = section_data["expected_http_code"]

    resp_code = make_request(url)

    valid = 1
    if not resp_code or expected_code != resp_code:
        valid = 0

    write_to_file(
        url=url,
        display=display,
        is_valid=valid
    )


def build_html_output(file_path):
    with open('template.mustache', 'r') as f:
        render(
            template=f,
            data={'mustache': 'World'}
        )


def main(args):
    """
    Argument from input

    :param args:
    :return:
    """
    config, config_sections = get_config(config_path=args.config)

    for section in config_sections:
        print("")
        print("--- Checking {} ---".format(section))

        if "url" not in config[section] or not config[section]["url"]:
            print("Not found `url` config on section `{}`".format(section))
            continue

        if "expected_http_code" not in config[section] or not config[section]["expected_http_code"]:
            print("Not found `expected_http_code` config on section `{}`".format(section))
            continue

        process_section(section_data=config[section])

    build_html_output(file_path=args.output)


if __name__ == "__main__":
    nx_parser = argparse.ArgumentParser(
        prog='monitor',
        usage='%(prog)s [options] --config config_path --output output_path',
        description='HTTP monitoring.'
    )
    nx_parser.add_argument('--config', action='store', type=str, default='config.ini')
    nx_parser.add_argument('--output', action='store', type=str, default='index.html')

    input_args = nx_parser.parse_args()

    main(args=input_args)
