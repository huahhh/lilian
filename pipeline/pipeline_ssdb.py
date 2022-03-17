# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    pipeline_ssdb.py
   Description :
   Author :       Huahng
   date：          2020/11/30
-------------------------------------------------
"""
__author__ = 'Huahng'

from uuid import uuid4

import pyssdb

from lilian.dblib.db_provide import get_db_provide
from lilian.pipeline.pipeline_base import pipeline_base


class pipeline_ssdb(pipeline_base):

    def __init__(self):
        super(pipeline_ssdb, self).__init__()
        self.ssdb_config = self.config.get_config(config_type='db_config', config_section='raw_data_db')
        self._make_ssdb_inst(self.ssdb_config)
        self.db_type_key = 'raw_data_db_type'
        self.db_queue_suffix = 'raw_data'

    def _make_ssdb_inst(self, ssdb_config):
        raw_data_db_type = ssdb_config.pop(self.db_type_key)
        raw_data_db_host = ssdb_config.pop('host')
        raw_data_db_port = ssdb_config.pop('port')
        self.ssdb_inst = get_db_provide(raw_data_db_type, raw_data_db_host, raw_data_db_port, **ssdb_config)

    def item_process(self, item):
        self._check_id(item)
        queue_name = ':'.join([item.get('table_name') or item.get('spider_name'), self.db_queue_suffix])
        item['table_name'] = queue_name
        self.put_to_ssdb(item)

    def put_to_ssdb(self, item):
        table_name = item.pop('table_name')
        try:
            self.ssdb_inst.qpush_front(table_name, item)
            return True
        except Exception as e:
            self.log.error(str(e))
            self.log.error('插入数据到ssdb失败, {}'.format(str(item)))

    def _check_id(self, item):
        if '_id' not in item:
            item['_id'] = str(uuid4())