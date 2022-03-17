# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    config_handler.py
   Description :
   Author :       Huahng
   date：          2021/7/28
-------------------------------------------------
"""
__author__ = 'Huahng'

from lilian.config.config_apollo import config_apollo_manager, config_apollo


def config_handler():
    # TODO unfinished code
    config_inst = config_apollo(host='*',
                                params='appid=lilian&cluster=online')
    print(config_inst.save_config())

    config_apollo_manager_inst = config_apollo_manager(host='*',
                                                       params="appid=lilian&token=*")
    config_apollo_manager_inst.upload_apollo(dir_name='online',
                                             cluster='test')
    config_apollo_manager_inst.release_apollo(cluster='test')

if __name__ == '__main__':
    config_handler()