# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    duplicate.py
   Description :
   Author :       Huahng
   date：          2020/12/2
-------------------------------------------------
"""
__author__ = 'Huahng'


from lilian.config.config import config
from lilian.commonlib.utils import md5_sum
from lilian.commonlib.logger import logger
from lilian.dblib.db_provide import get_db_provide

class duplicate(object):

    def __init__(self, spider_name):
        self.spider_name = spider_name

        self.dup_config = config().get_config('db_config', config_section='dup_db')
        self.log = logger(self.spider_name)

        self.dup_db_type = self.dup_config.pop('dup_db_type', '')
        self.dup_db_host = self.dup_config.pop('host', '')
        self.dup_db_port = self.dup_config.pop('port', '')

        self.dup_db_inst = get_db_provide(self.dup_db_type, self.dup_db_host,
                                          self.dup_db_port, **self.dup_config)

        self.dup_name = ''.join([spider_name, ':', 'dup'])

    def duplicate(self, item, dup_name=None):
        dup_zset = ''.join([dup_name, ':', 'dup']) if dup_name else self.dup_name
        if not isinstance(item, str):
            item = str(item)
        dup_res = self.dup_db_inst.zset(dup_zset, md5_sum(item), 1)

        if dup_res:
            return True
        else:
            self.log.info('%s, 存在, 故被去重' % str(item))
            return False

    def remove_item(self, item, dup_name=None):
        dup_zset = ''.join([dup_name, ':', 'dup']) if dup_name else self.dup_name
        if int(self.dup_db_inst.ssdb_conn.zdel(dup_zset, md5_sum(item))) == 1:
            self.log.info('移除 %s' % str(item))

if __name__ == '__main__':
    dup = duplicate('test')
    print(dup.duplicate('aaa'))
    print(dup.duplicate('aaa'))
