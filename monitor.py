# -*- coding: utf-8 -*-

"""
Dynamic DNS record update utility for CloudFlare DNS service.
(c) Dung Nguyen (nhymxu)
https://www.journaldev.com/23494/python-string-templateÍ
"""

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from configparser import ConfigParser
from os import path


CF_API_TOKEN = ''
IS_DRYRUN = False


def _make_request(method="GET", url="", request_body=None):
    """
    Send API request ( json type )

    :param method:
    :param url:
    :param request_body:
    :return:
    """
    headers = {
        'Authorization': "Bearer {}".format(CF_API_TOKEN),
        'Content-Type': 'application/json'
    }

    data = None
    if request_body:
        # data = urllib.parse.urlencode(request_body)
        data = request_body.encode('ascii')

    try:
        req = urllib.request.Request(url, headers=headers, data=data, method=method)
        with urllib.request.urlopen(req) as response:
            resp_content = response.read()
            return resp_content
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())
    except urllib.error.URLError as e:
        print(e.reason)

    return False


def get_config(config_path='config.ini'):
    """
    Read and parsing config from ini file.
    Set global var CF_API_TOKEN

    :return:
    """
    global CF_API_TOKEN

    if not path.exists(config_path):
        raise RuntimeError("config file not found")

    config = ConfigParser()
    config.read(config_path)

    if "common" not in config:
        raise Exception("Common config not found.")

    if "CF_API_TOKEN" not in config['common'] or not config['common']['CF_API_TOKEN']:
        raise Exception("Missing CloudFlare API Token on config file")

    CF_API_TOKEN = config['common']['CF_API_TOKEN']

    config_sections = config.sections()
    config_sections.remove("common")

    if not config_sections:
        raise Exception("Empty site to update DNS")

    return config, config_sections


def process_section(section_data):
    """
    Process all record in section

    :param section_data:
    :return:
    """
    base_domain = section_data["base_domain"].strip()
    record_list = section_data["records"].strip().split("|")

    for record in record_list:
        record = record.strip()
        dns_record = base_domain
        if record != '@':
            dns_record = "{}.{}".format(record, base_domain)

        if IS_DRYRUN:
            print("[DRY RUN] Update record `{}` in zone id `{}`".format(dns_record, section_data['zone_id']))
            continue

        update_host(section_data['zone_id'], dns_record, public_ip)


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

        if "base_domain" not in config[section] or not config[section]["base_domain"]:
            print("Not found `base_domain` config on section `{}`".format(section))
            continue

        if "records" not in config[section] or not config[section]["records"]:
            print("Not found `records` config on section `{}`".format(section))
            continue

        process_section(section_data=config[section])


if __name__ == "__main__":
    nx_parser = argparse.ArgumentParser(
        prog='monitor',
        usage='%(prog)s [options] --config config_path',
        description='HTTP monitoring.'
    )
    nx_parser.add_argument('--config', action='store', type=str, default='config.ini')
    nx_parser.add_argument('--output', action='store', type=str, default='')

    input_args = nx_parser.parse_args()

    main(args=input_args)
