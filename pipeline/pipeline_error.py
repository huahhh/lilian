# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    pipeline_error.py
   Description :
   Author :       Huahng
   date：          2021/7/27
-------------------------------------------------
"""
__author__ = 'Huahng'

from lilian.pipeline.pipeline_ssdb import pipeline_ssdb


class pipeline_error(pipeline_ssdb):

    def __init__(self):
        super(pipeline_error, self).__init__()
        self.ssdb_config = self.config.get_config(config_type='db_config', config_section='seed_db')
        self._make_ssdb_inst(self.ssdb_config)
        self.db_type_key = 'seed_db_type'
        self.db_queue_suffix = 'error_raw_data'