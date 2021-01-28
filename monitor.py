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


TMP_RESULT = {
    'success': [],
    'failed': {}
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
            return resp_code, ''
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())
        return e.code, e.reason
    except urllib.error.URLError as e:
        return 0, e.reason

    return 0, ''


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

    config_sections = config.sections()

    if not config_sections:
        raise Exception("Empty site to check")

    return config, config_sections


def process_section(section_data):
    """
    Process all record in section

    :param section_data:
    :return:
    """
    global TMP_RESULT

    url = section_data["url"].strip()
    display = section_data.get("display", url).strip()
    expected_code = section_data.getint('expected_http_code')

    url_hash = md5(url.encode('utf-8')).hexdigest()
    retry_attempt = 0
    if url_hash in TMP_RESULT['failed']:
        retry_attempt += 1

    start_time = datetime.now()
    resp_code, msg = make_request(url)
    end_time = datetime.now()

    duration = end_time - start_time
    elapsed_seconds = round(duration.microseconds * .000001, 6)

    result = {
        'name': display,
        'url': url,
        'duration': duration,
        'elapsed_seconds': elapsed_seconds,
        'actual_status': resp_code,
        'expected_status': expected_code,
        'time_check': end_time,
        'error': msg,
        'retry_attempt': retry_attempt
    }

    if not resp_code or expected_code != resp_code:
        if resp_code and msg == '':
            result['error'] = 'Status code does not match expected code'

        TMP_RESULT['failed'][url_hash] = result
    else:
        TMP_RESULT['success'].append(result)


def build_html_output(file_path):
    data = {
        'has_failed': True,
        'fail_count': 1,
        'check_date': '2021-01-20',
        'total_durations': 1000,
        'sites_error': [
            {
                'name': 'Google',
                'url': 'https://google.com',
                'expected_status': 200,
                'actual_status': 500,
                'error': 'xxx',
                'duration': 200,
            },
            {
                'name': 'Google CN',
                'url': 'https://google.cn',
                'expected_status': 200,
                'actual_status': 500,
                'error': 'Status code does not match expected code',
                'duration': 200,
            }
        ],
        'sites_success': [
            {
                'name': 'Google VN',
                'url': 'https://google.com.vn',
                'duration': 200,
            },
            {
                'name': 'DungNT',
                'url': 'https://dungnt.net',
                'duration': 400,
            }
        ]
    }

    with open('template.mustache', 'r') as f:
        html = render(template=f, data=data)

    with open(file_path, 'w') as fp:
        fp.write(html)


def main(args):
    """
    Argument from input

    :param args:
    :return:
    """
    config, config_sections = get_config(config_path=args.config)

    max_concurrent_thread = config['DEFAULT']['max_concurrent_thread']

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

    print(TMP_RESULT)
    # build_html_output(file_path=args.output)


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
