# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    timer_base.py
   Description :
   Author :       Huahng
   date：          2020/11/23
-------------------------------------------------
"""
__author__ = 'Huahng'

import copy
import time
import json
import traceback
from os import environ

from apscheduler.schedulers.blocking import BlockingScheduler

from lilian.config.config import config
from lilian.commonlib.logger import logger
from lilian.commonlib.constant import project_env
from lilian.dblib.db_provide import get_db_provide
from lilian.seed_queue.seed_queue import seed_queue

class timer_base(object):

    timer_name = 'timer_base'

    def __init__(self):
        self.operating_env = project_env

        self.queue_inst = seed_queue(self.timer_name)

        self.scheduler = BlockingScheduler(timezone='Asia/Shanghai')
        self.scheduler_ar = ''
        self.scheduler_kw = {}

        self.config = config()
        self.timer_config = self.config.get_config('timer_config', config_section=self.timer_name)

        self.log = logger(self.timer_name)

        self._timer_init()
        self.timer_init()

    def timer_init(self):
        pass

    def _timer_init(self):
        self.log.info('timer=<%s>, 开始启动. ' % self.timer_name)

    def run(self):
        try:
            if len(self.timer_config) == 1 and 'etl' in self.timer_config: #etl具有独占性
                self.log.info('timer为etl型定时器, {}'.format(self.timer_name))
                self._etl_handler()
            else:
                self.log.info('timer为普通定时器, {}'.format(self.timer_name))
                self._timer_handler()
            self.scheduler.start()
        except:
            self.log.error('运行timer-%s, 出错.' % self.timer_name)
            self.log.error(traceback.format_exc())


    def _etl_handler(self):
        aps_trigger, aps_kwargs, func_config = self._unzip_timer_config(
            'etl', self.timer_config['etl'])
        self.log.info('添加etl定时器, aps_trigger={}, aps_kwargs={}, func_config={}'.format(
            str(aps_trigger), str(aps_kwargs), str(func_config)
        ))
        self.scheduler.add_job(
            self.etl_once,
            trigger=aps_trigger,
            args=func_config,
            **aps_kwargs
        )

    def _timer_handler(self):
        for timer_item in self.timer_config:
            try:
                aps_trigger, aps_kwargs, func_config = self._unzip_timer_config(
                    timer_item, self.timer_config[timer_item])
                if hasattr(self, timer_item):
                    self.log.info('添加timer_func定时器, timer_item={}, aps_trigger={}, aps_kwargs={}, func_config={}'
                                  .format(str(timer_item), str(aps_trigger), str(aps_kwargs), str(func_config)))
                    self.scheduler.add_job(
                        getattr(self, timer_item),
                        trigger=aps_trigger,
                        args=func_config,
                        **aps_kwargs
                    )

                elif hasattr(self, self.timer_name):
                    self.log.info('添加timer_global定时器, aps_trigger={}, aps_kwargs={}, func_config={}'
                                  .format(str(aps_trigger), str(aps_kwargs), str(func_config)))
                    self.scheduler.add_job(
                        getattr(self, self.timer_name),
                        trigger=aps_trigger,
                        args=func_config,
                        **aps_kwargs
                    )

                else:
                    self.log.warning('该timer未找到同名函数及timer及函数, 请检查相关配置, {}'.format(timer_item))
                    self.log.warning('该timer未找到同名函数及timer及函数, 请检查相关配置, {}'.format(timer_item))
                    self.log.warning('该timer未找到同名函数及timer及函数, 请检查相关配置, {}'.format(timer_item))
            except:
                self.log.error(traceback.format_exc())
                self.log.error('添加timer失败, {}'.format(timer_item))

    def _unzip_timer_config(self, timer_item, timer_config):
        if isinstance(timer_config, str):
            timer_config = json.loads(timer_config)
        assert 'aps_config' in timer_config, 'timer配置不正确'
        aps_config, func_config = timer_config.get('aps_config', {}), timer_config.get('func_config', [])
        aps_trigger = aps_config.pop('trigger', 'cron')
        aps_kwargs = aps_config
        assert any([isinstance(func_config, list),
                        isinstance(func_config, dict)]), 'timer配置不正确'
        if timer_item != 'etl':
            if isinstance(func_config, list):
                func_config.append(timer_item)
            else:
                func_config['timer_item'] = timer_item
        return aps_trigger, aps_kwargs, func_config


    def etl_once(self, *args):
        data = self.extract(*args)
        if data:
            c_data = copy.deepcopy(data)
            data_result = self.transform(c_data)
            if data_result:
                c_data_result = copy.deepcopy(data_result)
                self.load(c_data_result)

    def extract(self, *args):
        pass

    def transform(self, data):
        pass

    def load(self, data):
        pass