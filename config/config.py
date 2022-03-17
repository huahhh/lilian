# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    config.py
   Description :
   Author :       Huahng
   date：          2020/11/19
-------------------------------------------------
"""
__author__ = 'Huahng'

import os
import importlib
from urllib.parse import urlparse

from lilian.config.config_ini import config_ini
from lilian.commonlib.pathlib import get_file_in_path
from lilian.commonlib.constant import project_name
from lilian.commonlib.singleton import singleton

def c_str_decode(item):
    if item.isdigit():
        return int(item)
    elif 'true' == item.lower() or 'false' == item.lower():
        return eval(item.capitalize())
    elif item.startswith('[') or item.startswith('{'):
        try:
            return eval(item)
        except:
            return item
    else:
        return item

def c_decode(item):
    if isinstance(item, str):
        return c_str_decode(item)
    elif isinstance(item, list):
        return [c_decode(i) for i in item]
    elif isinstance(item, dict):
        return {i: c_decode(item[i]) for i in item}
    else:
        return item

def config_decode(func):
    def wrapper(*args, **kwargs):
        return c_decode(func(*args, **kwargs))
    return wrapper


@singleton
class config(object):

    def __init__(self):
        self._make_config_inst()

    def _make_config_inst(self):
        config_server_uri = os.environ.get('config_env')
        self.config_server = self._get_config_for_uri(config_server_uri) if config_server_uri else None
        self.config_ini = config_ini()

    @config_decode
    def get_config(self, config_type, online=False, config_section=None, config_item=None, flash_log=True, *args, **kwargs):
        config_res = None
        if online and self.config_server:
            try:
                config_res = self.config_server.get_config(config_type,
                                                           config_section=config_section,
                                                           config_item=config_item,
                                                           *args,
                                                           **kwargs)
            except:
                pass

        if not config_res:
            config_res =  self.config_ini.get_config(config_type,
                                              config_section=config_section,
                                              config_item=config_item,
                                              *args,
                                              **kwargs)
        if flash_log:
            if not hasattr(self, 'log_inst'):
                from lilian.commonlib.logger import logger
                self.log_inst = logger('config')
            self.log_inst.info('[CONFIG]-提取config, config_type={}, config={}.'.format(config_type, str(config_res)))
        return config_res


    def _check_config_server(self, config_server):
        return get_file_in_path('config',
                                'config_{config_server}.py'.format(config_server=config_server),
                                res_bool=True)

    def _get_config_for_uri(self, uri):
        parser_uri = urlparse(uri)
        config_server_type = parser_uri.scheme
        assert self._check_config_server(config_server_type), "config_server not fount"
        config_server_inst = getattr(
            importlib.import_module(
                '{}.config.config_{}'.format(project_name, config_server_type)),
            'config_{}'.format(config_server_type))(parser_uri.netloc, parser_uri.query)
        return config_server_inst


if __name__ == '__main__':
    os.environ['config_env'] = 'apollo://*?appid=lilian&cluster=online'
    config_inst = config()
    config_inst.config_server.save_config()
