# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    monitor.py
   Description :
   Author :       Huahng
   date：          2020/11/30
-------------------------------------------------
"""
__author__ = 'Huahng'


import time

from lilian.commonlib.logger import logger
from lilian.config.config import config
from lilian.dblib.db_provide import get_db_provide

class monitor(object):

    def __init__(self):
        #make db inst
        self.config = config()
        self._monitor_db_config = self.config.get_config("db_config", config_section="monitor_db")
        self.monitor_db_type = self._monitor_db_config.pop('monitor_db_type', '')
        self.monitor_db_host = self._monitor_db_config.pop('host', '')
        self.monitor_db_port = self._monitor_db_config.pop('port', '')

        self.monitor_db_inst = get_db_provide(self.monitor_db_type, self.monitor_db_host,
                                           self.monitor_db_port, **self._monitor_db_config)

        self.log = logger('monitor')

        self.parser_func_count_dict = {}
        self.http_status_code_dict = {}

    def hincrby_spider_name(self, spider_name):
        now_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        spider_monitor_hash = ''.join([spider_name, ':', 'monitor'])
        self.monitor_db_inst.hincr(spider_monitor_hash, now_date)

    def monitor_info(self, spider_name, parser_func, http_status_code):
        self.monitor_queue_size_info(spider_name)
        self.monitor_parser_func_info(parser_func)
        self.monitor_http_status_code_info(http_status_code)

    def monitor_http_status_code_info(self, http_status_code):
        log_str = ''
        if http_status_code in self.http_status_code_dict:
            self.http_status_code_dict[http_status_code] += 1
        else:
            self.http_status_code_dict[http_status_code] = 1
        for http_status_code_item in self.http_status_code_dict:
            log_str += "\n response_http_status_code=<%s>的个数为%s" % (
                http_status_code_item, self.http_status_code_dict[http_status_code_item])
        self.log.info('response_http_status_code统计信息如下' + log_str)

    def monitor_parser_func_info(self, parser_func):
        log_str = ''
        if parser_func in self.parser_func_count_dict:
            self.parser_func_count_dict[parser_func] += 1
        else:
            self.parser_func_count_dict[parser_func] = 1
        for parser_func_item in self.parser_func_count_dict:
            log_str += "\n 已处理parser_func=<%s>的seed个数为%s" % (
                parser_func_item, self.parser_func_count_dict[parser_func_item])
        self.log.info('处理种子的parser_func统计信息如下' + log_str)

    def monitor_queue_size_info(self, spider_name):
        seed_count, error_count, error_html_count = 0, 0, 0
        queue_suffix = eval(self.config.get_frame_config('seed_queue', 'suffix'))
        if 'error' in queue_suffix:
            queue_suffix.pop(queue_suffix.index('error'))
        for suff in queue_suffix:
            seed_count += self.monitor_db_inst.queue_llen(''.join([spider_name, ':', suff]))
        error_count = self.monitor_db_inst.queue_llen(''.join([spider_name, ':', 'error']))
        error_html_count = self.monitor_db_inst.queue_llen(''.join([spider_name, ':', 'error_html']))
        self.log.info('当前spider=<%s>, seed队列长度为%s, error队列长度为%s, error_html长度为%s' % (
            spider_name, seed_count, error_count, error_html_count))



if __name__ == "__main__":
    a = monitor()
    now = time.time()
    for i in range(100):
        a.monitor_queue_size_info('wanfang_patent')
    print(time.time() - now)




