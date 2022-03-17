# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    queue_ssdb.py
   Description :
   Author :       Huahng
   date：          2020/11/20
-------------------------------------------------
"""
__author__ = 'Huahng'

import json
import time
import pickle

from lilian.config.config import config
from lilian.commonlib.logger import logger
from lilian.seed_queue.queue_base import queue_base
from lilian.dblib.db_provide import get_db_provide

class queue_ssdb(queue_base):

    def __init__(self, spider_name):
        self.config_inst = config()

        self.seed_db_config = self.config_inst.get_config('db_config', config_section='seed_db')

        self.seed_db_host = self.seed_db_config.pop('host', '')
        self.seed_db_port = self.seed_db_config.pop('port', '')

        self.seed_db_inst = get_db_provide('ssdb', self.seed_db_host, self.seed_db_port, **self.seed_db_config)

        self.spider_name = spider_name
        self.log = logger(self.spider_name)
        self.queue_suffix = self.config_inst.get_config('frame_config', config_section='seed_queue', config_item='suffix')

    def get_seed(self):
        for suff in self.queue_suffix:
            while True:
                queue_name = ''.join([self.spider_name, ":", suff])
                seed = self.seed_db_inst.qpop_front(queue_name)
                if seed:
                    self.log.info('从%s队列取出一条种子' % ''.join([self.spider_name, ":", suff]))
                    try:
                        try:
                            seed_dict = json.loads(seed)
                        except:
                            self.log.warning('seed使用json-loads失败, 尝试使用pickle-load')
                            seed_dict = pickle.loads(seed)
                        seed_dict['suffix'] = suff
                        return seed_dict
                    except:
                        self.log.warning('该种子json序列化失败, 即将存入error队列, {}'.format(str(seed)))
                        self.put_error(seed)
                else:
                    self.log.info('%s, 队列为空.' % ''.join([self.spider_name, ":", suff]))
                    break

    def put_seed(self, seed, front=True):
        # todo: if put in seed_inst
        seed_spider_name = seed.pop('spider_name', None)
        spider_name = seed_spider_name or self.spider_name
        if not seed is None:
            seed_type = seed.get('parser_func') if isinstance(seed, dict) else 'non_type'
            suffix = seed.pop('suffix', 'seed')
            queue_name = ''.join([spider_name, ":", suffix])
            queue_len = self._put_seed(seed, queue_name, front=front)
            self.log.info('[%s]往%s队列存入一条parser_func为%s的种子, 当前队列长度为%s.' %
                          (spider_name, queue_name, seed_type, queue_len))
        else:
            self.log.warning('spider_name=<%s>, put_data为None.' % spider_name)

    def _put_seed(self, seed, queue_name, front=True):
        if isinstance(seed, dict):
            try:
                seed = json.dumps(seed)
            except:
                self.log.warning('seed使用json序列化失败, 尝试使用pickle序列化')
                seed = pickle.dumps(seed)
        if front:
            return self.seed_db_inst.qpush_front(queue_name, seed)
        else:
            return self.seed_db_inst.qpush_back(queue_name, seed)

    def put_error(self, seed, sleep_time=5, resp=None):
        self.log.warning('将出错seed放入error队列，并休眠%dS' % sleep_time)
        suffix = 'error' if not resp else 'error_resp'
        if resp:
            seed['resp'] = resp.res_text
        seed['suffix'] = suffix
        self.put_seed(seed, front=False)
        time.sleep(sleep_time)

    def check_seed_is_empty(self, spider_name=None):
        spider_name = spider_name or self.spider_name
        for suff in self.queue_suffix:
            if 'error' == suff or 'retry' == suff:
                continue
            queue_name = ''.join([spider_name, ":" if suff else "", suff])
            if self.seed_db_inst.qsize(queue_name):
                return False
        return True

    def clear_queue(self, queue_list):
        for queue_item in queue_list:
            self.seed_db_inst.delete(queue_item)

if __name__ == '__main__':
    ssdb_inst = queue_ssdb('test')
    ssdb_inst.get_seed()

