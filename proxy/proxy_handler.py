# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    proxy_handler.py
   Description :
   Author :       Huahng
   date：          2020/11/27
-------------------------------------------------
"""
__author__ = 'Huahng'

import importlib


from lilian.config.config import config
from lilian.commonlib.constant import project_name
from lilian.commonlib.pathlib import get_file_in_path

def proxy(proxy_type=None):
    proxy_type = proxy_type or config().get_config(
        'frame_config', config_section='proxy_config', config_item='proxy_type')
    assert proxy_type, 'proxy_type undefined'
    assert get_file_in_path('proxy', 'proxy_{proxy_type}.py'.format(
        proxy_type=proxy_type), res_bool=True), '{} proxy not fount'.format(proxy_type)
    return getattr(
        importlib.import_module(
            '{}.proxy.proxy_{}'.format(project_name, proxy_type)),
        'proxy_{}'.format(proxy_type))()



if __name__ == '__main__':
    proxy_inst = proxy()
    print(proxy_inst)
