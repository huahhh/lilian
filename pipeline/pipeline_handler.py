# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    pipeline_handler.py
   Description :
   Author :       Huahng
   date：          2020/11/30
-------------------------------------------------
"""
import time

__author__ = 'Huahng'

import importlib

from lilian.config.config import config
from lilian.commonlib.logger import logger
from lilian.commonlib.constant import project_name
from lilian.commonlib.pathlib import get_file_in_path
from lilian.commonlib.utils import now_time, now_time_stamp

class pipeline_handler(object):
    # todo: 梳理多pipeline写入逻辑，并实现写入失败后使用pipeline_error写入作为back up, 并考虑error_raw_data的恢复逻辑

    def __init__(self, spider_name):
        self.spider_name = spider_name
        self.log = logger(spider_name)
        self.config = config()
        self.pipeline_inst = self._make_pipelines_inst_dict()

    def _make_pipelines_inst_dict(self):
        pipeline_config_dict = self.config.get_config('frame_config' ,config_section='pipeline_config')
        for pipeline_item in pipeline_config_dict:
            pipeline_config_dict[pipeline_item] = self._make_pipelines_inst(pipeline_config_dict[pipeline_item])
        return pipeline_config_dict

    def _make_pipelines_inst(self, pipeline_type):
        assert get_file_in_path('pipeline', 'pipeline_{pipeline_type}.py'.format(
            pipeline_type=pipeline_type), res_bool=True), '{} pipeline not fount'.format(pipeline_type)
        return getattr(
            importlib.import_module(
                '{}.pipeline.pipeline_{}'.format(project_name, pipeline_type)),
            'pipeline_{}'.format(pipeline_type))()

    def _merge_result(self, result_item, resp_inst):
        url = resp_inst.url if resp_inst else None
        result_item.update({'url': result_item.get('url', '') or url,
                            'update_time': now_time(),
                            'update_time_stamp': now_time_stamp(),
                            'spider_name': self.spider_name})
        return result_item

    def pipeline_item_process(self, item, resp_inst, pipeline_type):
        if isinstance(pipeline_type, str):
            result = self._merge_result(item, resp_inst)
            if pipeline_type not in self.pipeline_inst:
                self.log.warning('无该pipeline_type, {}'.format(pipeline_type))
                return False
            else:
                data_stat = self.pipeline_inst[pipeline_type].item_process(result)
                self.log.info('spider={spider_name}, 往result_db={pipeline_type}存入一条结果数据. '.format(
                    spider_name = self.spider_name, pipeline_type=pipeline_type))
                return data_stat
        else:
            data_states = [self.pipeline_item_process(item, resp_inst, pipeline_type_item)
                           for pipeline_type_item in pipeline_type]
            return any(data_states)
