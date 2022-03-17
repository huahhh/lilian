# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    config_ini.py
   Description :
   Author :       Huahng
   date：          2020/11/19
-------------------------------------------------
"""
__author__ = 'Huahng'

import os
import configparser

from lilian.commonlib.pathlib import get_path
from lilian.commonlib.constant import project_env
from lilian.config.config_base import config_base

class config_ini(config_base):

    def __init__(self):
       self.run_env = project_env

    def save_config(self):
        pass

    def read_config(self, config_type):
        ini_config_inst = configparser.ConfigParser()
        ini_config_inst.read(''.join([get_path(), self.run_env, os.path.sep, config_type, '.ini']), encoding='utf-8')
        return ini_config_inst

    def _parser_config_inst(self, ini_config_inst):

        def nested_set(dic, keys, value):
            for key in keys[:-1]:
                dic = dic.setdefault(key, {})
            dic[keys[-1]] = value

        def _parser_section(sections):
            tmp_dict = {i[0]: i[1] for i in sections}
            mu_dict = {}

            for key in tmp_dict:
                keys = key.split('.')
                nested_set(mu_dict, keys, tmp_dict[key])
            return mu_dict

        return {
            i: _parser_section(ini_config_inst.items(i))
                for i in ini_config_inst.sections()
        }

    def get_config(self, config_type, config_section=None, config_item=None, *args, **kwargs):
        ini_config_inst = self.read_config(config_type)
        config_dict = self._parser_config_inst(ini_config_inst)
        assert config_dict, '配置类 {} 未找到'.format(config_type)
        if config_section:
            assert config_section in config_dict, '配置组 {} 未找到'.format(config_section)
            if config_item:
                assert config_item in config_dict[config_section], '配置项 {} 未找到'.format(config_item)
                return config_dict[config_section][config_item]
            else:
                return config_dict[config_section]
        return config_dict

if __name__ == '__main__':
    config_inst = config_ini('')
    print(config_inst.get_config('frame_config'))