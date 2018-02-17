import unittest

import datetime

import log_analyzer

logs = [
    u'1.168.65.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/internal/banner/24294027/info HTTP/1.1" 200 407 "-" "-" "-" "1498697422-2539198130-4709-9928846" "89f7f1be37d" 0.146',
    u'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/1769230/banners HTTP/1.1" 200 1020 "-" "Configovod" "-" "1498697422-2118016444-4708-9752747" "712e90144abee9" 0.628',
    u'1.194.135.240 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/group/7786679/statistic/sites/?date_type=day&date_from=2017-06-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/2.13.0" "-" "1498697422-3979856266-4708-9752772" "8a7741a54297568b" 0.067',
    u'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" "1498697422-2118016444-4708-9752771" "712e90144abee9" 0.138',
    u'1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/appinstall_raw/2017-06-29/ HTTP/1.0" 200 28358 "-" "Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12) Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" "-" "-" "-" 0.003',
    u'1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/4822/groups HTTP/1.1" 200 22 "-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-4708-9752773" "2a828197ae235b0b3cb" 0.157',
    u'scdscdsdc',
    u'scdsdsddc'
]


def logs_gen():
    for log in logs:
        yield log


class LogAnalyzerTest(unittest.TestCase):

    def setUp(self):
        self.config = {
            "REPORT_SIZE": 100,
            "REPORT_DIR": "./reports",
            "LOG_DIR": "./logs",
            "LOGGING_FILE": "./logging/tmp/logging.log",
            "TS_FILE": "./timestamp/tmp/log_analyzer.ts"
        }

    def test_should_not_return_last_create_file_from_dir(self):
        self.assertIsNone(log_analyzer.get_last_created_file_from_dir('some_dit'))

    def test_should_not_returned_logs(self):
        self.assertRaises(log_analyzer.read_log_lines('some_file'))

    def test_should_build_analyze_data(self):
        self.assertIsNotNone(log_analyzer.analyze_log(logs_gen()))

    def test_should_not_build_analyze_data(self):
        self.assertRaises(log_analyzer.analyze_log(logs_gen(), 0.999))

    def test_should_report_analyze_data(self):
        report_file = '{}/report-{}.html'.format(self.config['REPORT_DIR'], datetime.date.today().strftime("%Y.%m.%d"))
        data = log_analyzer.analyze_log(logs_gen())
        log_analyzer.report_data(data, report_file)
        report_data = log_analyzer.read_lines_from_file(report_file)
        self.assertGreater(len(report_data), 0)

    def test_should_created_ts_file(self):
        test_ts = log_analyzer.update_timestamp_file(self.config['TS_FILE'])
        ts_from_file = log_analyzer.read_lines_from_file(self.config['TS_FILE'])
        self.assertEquals(test_ts, ts_from_file[0])


if __name__ == '__main__':
    unittest.main()
