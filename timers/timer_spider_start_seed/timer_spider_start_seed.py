# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    timer_spider_start_seed.py
   Description :
   Author :       Huahng
   date：          2020/12/9
-------------------------------------------------
"""
__author__ = 'Huahng'

from lilian.core.timer_base import timer_base

class timer_spider_start_seed(timer_base):

    timer_name = 'spider_start_seed'

    def spider_start_seed(self, *args):
        assert args, 'args is empty'
        spider_name = args[0]
        self.call_spider_start_url(spider_name)

    def call_spider_start_url(self, spider_name):
        if self.queue_inst.check_seed_is_empty(spider_name):
            self.queue_inst.put_seed({"parser_func": "start_url", "spider_name": spider_name})
            self.log.info('{spider_name}, 灌入初始种子。'.format(spider_name=spider_name))
        else:
            self.log.info('spider=<%s>种子队列不为空，故将忽略定时灌入初始种子.' % spider_name)

if __name__ == '__main__':
    timer_inst = timer_spider_start_seed()
    timer_inst.run()