# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    logger.py
   Description :
   Author :       Huahng
   date：          2019/10/18
-------------------------------------------------
"""
__author__ = 'Huahng'

import os
import logging

from lilian.config.config import config
from lilian.commonlib.pathlib import get_path, make_dirs
from lilian.commonlib.singleton import singleton

@singleton
class _logger(object):

    def __init__(self, log_name, *args, **kwargs):
       self.log_name = log_name
       self.pid = os.getpid()
       self.log_config = config().get_config('frame_config', config_section='log_config', flash_log=False)

       self.stream_flag = self.log_config.get('stream_flag', True)
       self.file_flag = self.log_config.get('file_flag', False)
       self.log_level = self.log_config.get('log_level', 'debug')
       self.log_interval = self.log_config.get('log_interval', 1)
       self.log_backup_count = self.log_config.get('log_backup_count', 2)
       self.log_path = self.log_config.get('log_path')

       self.log_fmt = '%(asctime)s||%(name)s(%(process)d)||%(filename)s->%(module)s->%(funcName)s %(lineno)d||%(levelname)s||%(message)s'

       self.level_getter = lambda x: eval('.'.join(['logging', x]))

       self.logger_inst = logging.getLogger(self.log_name)
       self.logger_inst.setLevel(self.level_getter(self.log_level.upper()))
       self.get_logger()
       self.logger_inst.propagate = False

    def get_logger(self):
        if self.logger_inst.handlers:
            return self.logger_inst
        if self.stream_flag:
            self.logger_inst.addHandler(self.stream_logger_handler())
        if self.file_flag:
            self.logger_inst.addHandler(self.file_logger_handler())
        return self.logger_inst

    def file_logger_handler(self):
        log_path = self.log_path or get_path(flag='log')
        make_dirs(log_path)
        log_file_name = ''.join([self.log_name , '_' , str(self.pid) , '.log'])

        from logging.handlers import TimedRotatingFileHandler

        file_name = os.path.sep.join([log_path, log_file_name])
        log_file_handler = TimedRotatingFileHandler(file_name, 'D', self.log_interval,
                                                    self.log_backup_count, encoding='utf-8')
        log_file_handler.suffix = '%Y-%m-%d'
        log_file_handler.setLevel(self.level_getter(self.log_level.upper()))
        log_fmt_inst = logging.Formatter(fmt=self.log_fmt)
        log_file_handler.setFormatter(log_fmt_inst)
        return log_file_handler

    def stream_logger_handler(self):
        log_stream_handler = logging.StreamHandler()
        log_stream_handler.setLevel(self.level_getter(self.log_level.upper()))
        log_fmt_inst  = logging.Formatter(fmt=self.log_fmt)
        log_stream_handler.setFormatter(log_fmt_inst)
        return log_stream_handler

def logger(log_name, *args, **kwargs):
    log_inst = _logger(log_name, *args, **kwargs)
    return log_inst.logger_inst



if __name__ == '__main__':
    logger_inst = logger('test')
    logger_inst.info('aaa')
    logger_inst.debug('cvccc')
    logger_inst_1 = logger('aaa')
    logger_inst_1.warning('asfasdf')