# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    proxy_yiniu.py
   Description :
   Author :       Huahng
   date：          2020/11/27
-------------------------------------------------
"""
__author__ = 'Huahng'

import json
import time
import requests

from lilian.config.config import config
from lilian.commonlib.logger import logger
from lilian.proxy.proxy_base import proxy_base
from lilian.commonlib.catch_retry import catch_retry

class proxy_yiniu(proxy_base):

    def __init__(self):
        self.log = logger('proxy_yiniu')
        self.config = config()

        self.proxy_base = 'http://%s/%s'

        self.proxy_server = self.config.get_config('frame_config',
                                                   config_section='proxy_config', config_item='proxy_server')
        self.proxy_path = self.config.get_config('frame_config',
                                                       config_section='proxy_config', config_item='proxy_path')

        self.proxy_url = self.proxy_base % (self.proxy_server, self.proxy_path)



    @property
    def get_proxy(self):
        proxy_result = self._get_proxy()
        while not proxy_result:
            proxy_result = self._get_proxy()
        proxy_ = json.loads(proxy_result).get('ProxyIp')
        return {
            'http': ''.join(['http://', proxy_]),
            'https': ''.join(['https://', proxy_])
        }

    @catch_retry
    def _get_proxy(self):
        proxy_result = requests.get(self.proxy_url).text
        if 'ProxyIp' not in proxy_result:
            raise Exception('代理服务不可用,即将重试连接,请检查代理服务.')
        end_time = json.loads(proxy_result).get('EndTime', 0)
        now_time = int(time.time())
        if end_time - now_time < 0:
            self.log.warning('代理过期, 休眠0.5秒后重新获取')
            time.sleep(0.5)
            return None
        return proxy_result