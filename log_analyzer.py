# coding=utf-8
# !/usr/bin/env python


import ConfigParser
import argparse
import datetime
import gzip
import json
import logging
import operator
import os
import re
import time
from collections import (defaultdict, namedtuple)
from string import Template


def is_file(file_path):
    return True if file_path and os.path.isfile(file_path) else False


def read_log_lines(log_path):
    if log_path.endswith('.gz'):
        log = gzip.open(log_path, 'rb')
    else:
        log = open(log_path)
    for line in log:
        yield line.decode()
    log.close()


def read_lines_from_file(f_name):
    try:
        with open(f_name, 'r') as fp:
            lines = fp.readlines()
    except Exception as error:
        logging.info("Reade error: {}".format(error))
        lines = []
    return lines


def save_string(string, f_name):
    try:
        with open(f_name, 'w') as fp:
            fp.write(string)
    except Exception as error:
        logging.info("Write error: {}".format(error))


date_regex = re.compile(r'[0-9]{4}[.]?[0-9]{2}[.]?[0-9]{2}')


def get_date_from_string(path):
    return datetime.datetime.strptime(re.findall(date_regex, path)[0], '%Y%m%d')


def get_last_created_file_from_dir(dir_path):
    Last = namedtuple('Last', ["file", "date"])

    try:
        last_file = last_date = None
        for file_name in os.listdir(dir_path):
            if is_file(os.path.join(dir_path, file_name)) and re.search(date_regex, file_name):
                current_date = get_date_from_string(file_name)

                if last_file is None:
                    last_file = os.path.join(dir_path, file_name)
                    last_date = current_date

                if last_date < current_date:
                    last_file = os.path.join(dir_path, file_name)
                    last_date = current_date
        return Last(file=last_file, date=last_date)
    except Exception as error:
        logging.info("Read error: {}".format(error))
        return None


def update_timestamp_file(timestamp_file):
    ts = str(int(time.time()))
    save_string(ts, timestamp_file)
    return ts


def parse_log_line(log_line):
    line_splits = log_line.split(' ')
    try:
        u = line_splits[7].strip()
        t = float(line_splits[-1].strip())
    except Exception as ignore:
        return None, None
    return u, t


def median(data):
    quotient, remainder = divmod(len(data), 2)
    return sorted(data)[quotient] if remainder else sum(sorted(data)[quotient - 1: quotient + 1]) / 2.0


def analyze_log(log, success_threshold=0.7):
    logs_count = total = times_sum = 0
    urls_agg = defaultdict()
    for log_line in log:
        u, t = parse_log_line(log_line)
        if u and t:
            urls_agg[u] = urls_agg.get(u, list()) + [t]
            times_sum += t
            logs_count += 1
        total += 1

    if float(logs_count) / total < success_threshold:
        raise Exception("Too many incorrect log lines")

    data = []
    for url, times in urls_agg.items():
        data.append({
            'url': url,
            'count': len(times),
            'count_perc': round(float(len(times)) / logs_count, 3),
            'time_avg': round(sum(times) / len(times), 3),
            'time_max': max(times),
            'time_med': median(times),
            'time_perc': round(sum(times) / times_sum, 3),
            'time_sum': sum(times)
        })

    data.sort(key=operator.itemgetter('time_avg'), reverse=True)
    return data


def render_data(data):
    return Template('$json_table').substitute(json_table=json.dumps(data))


def report_data(report_data, report_file):
    save_string(render_data(report_data), report_file)


def parse_config(config_path):
    conf = ConfigParser.RawConfigParser(allow_no_value=True)
    conf.read(config_path)
    return dict((name.upper(), value) for (name, value) in conf.items('default'))


def main(config):
    # find last log file
    last = get_last_created_file_from_dir(config['LOG_DIR'])
    if last.file:

        # create and check report file
        report_file = os.path.join(config['REPORT_DIR'], 'report-{}.html'.format(last.date.strftime("%Y.%m.%d")))

        if not os.path.exists(report_file):
            data = analyze_log(read_log_lines(last.file))
            if data:
                report_data(data[:int(config['REPORT_SIZE'])], report_file)
                logging.info('logs reported in {}'.format(report_file))
        else:
            logging.info('logs have already reported in {}'.format(report_file))
        update_timestamp_file(config['TS_FILE'])
    else:
        logging.info("log files are not exists")


# Default config
config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./logs/",
    "TS_FILE": "./timestamp/tmp/log_analyzer.ts"
}

if __name__ == "__main__":
    # parse args
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--config', type=str, nargs='?', dest='config', default='./configs/log_nalyzer.conf')
    args = argument_parser.parse_args()

    if is_file(args.config):
        # parse config file and update config
        config.update(parse_config(args.config))

        # set logging params
        logging.basicConfig(format='[%(asctime)s] %(levelname).1s %(message)s',
                            datefmt='%Y.%m.%d %H:%M:%S',
                            filename=config.get('LOGGING_FILE'),
                            filemode='a',
                            level=logging.INFO)
        main(config)
    else:
        raise ValueError("{} isn't config file".format(args.config))
