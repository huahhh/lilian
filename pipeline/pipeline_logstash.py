# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    pipeline_logstash.py
   Description :
   Author :       Huahng
   date：          2020/11/30
-------------------------------------------------
"""
__author__ = 'Huahng'

import json
import uuid

import requests

from lilian.commonlib.catch_retry import catch_retry
from lilian.pipeline.pipeline_base import pipeline_base

class pipeline_logstash(pipeline_base):

    def __init__(self):
        super(pipeline_logstash, self).__init__()
        self.logstash_addr = self.config.get_config('db_config',
                                                    config_section='logstash', config_item='logstash_addr')
        self.logstash_to_es_addr = self.config.get_config('db_config',
                                                          config_section='logstash', config_item='logstash_to_es_addr')

    def item_process(self, item):
        self._check_id(item)
        item['table_name'] = item.get('table_name') or item.get('spider_name')
        return self.put_to_logstash(item)

    @catch_retry
    def put_to_logstash(self, item):
        if item.get('to_es'):
            item.pop('to_es', '')
            item.pop('_id', '')
            res = requests.post(self.logstash_to_es_addr, data=json.dumps(item).encode('utf-8'), timeout=120)
        else:
            res = requests.post(self.logstash_addr, data=json.dumps(item).encode('utf-8'), timeout=120)
        if res.status_code != 200:
            raise Exception
        else:
            return True

    def _check_id(self, item):
        if '_id' not in item:
            item['_id'] = str(uuid.uuid4())
