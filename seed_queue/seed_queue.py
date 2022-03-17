# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    seed_queue.py
   Description :
   Author :       Huahng
   date：          2020/11/20
-------------------------------------------------
"""
__author__ = 'Huahng'

import importlib

from lilian.config.config import config
from lilian.commonlib.constant import project_name
from lilian.commonlib.pathlib import get_file_in_path

def seed_queue(spider_name):
    queue_type = config().get_config('frame_config', config_section='module_type', config_item='queue_type')
    assert queue_type, 'queue type is none'
    assert get_file_in_path('seed_queue', 'queue_{queue_type}.py'.format(
        queue_type=queue_type), res_bool=True), '{} queue not fount'.format(queue_type)
    return getattr(
            importlib.import_module(
                '{}.seed_queue.queue_{}'.format(project_name, queue_type)),
            'queue_{}'.format(queue_type))(spider_name)

if __name__ == '__main__':
    queue_inst = seed_queue('test')
    print(queue_inst)
