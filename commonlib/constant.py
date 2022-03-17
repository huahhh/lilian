# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    constant.py
   Description :
   Author :       Huahng
   date：          2020/11/23
-------------------------------------------------
"""
__author__ = 'Huahng'

import os

from urllib.parse import urlparse


def _get_config_server_env(env_params):
    try:
        return {i.split('=')[0]: i.split('=')[1] for i in env_params.split('&')}.get('cluster')
    except:
        return

def _get_env():
    uri = urlparse(os.environ.get('config_env', ''))
    return _get_config_server_env(uri.query) or os.environ.get('env', 'debug')

project_name = os.environ.get('project_name',
                              'lilian')

project_env = _get_env()
