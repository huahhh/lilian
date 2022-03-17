# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    spider_manager.py
   Description :
   Author :       Huahng
   date：          2020/12/8
-------------------------------------------------
"""
__author__ = 'Huahng'

import os

import argparse
import configparser

from lilian.config.config import config
from lilian.commonlib.logger import logger
from lilian.commonlib.pathlib import get_file_in_path

class spider_manager(object):

    def __init__(self):
        self.config = config()
        self.load_config()
        self.log = logger('spider_manager')

        self.cmd_parser = argparse.ArgumentParser()
        self.cmd_parser.add_argument('-m', action='store_true', help='make spider_run.ini')
        self.cmd_parser.add_argument('-su', type=str, default='')
        self.cmd_parser.add_argument('-cs', type=str, default='')
        self.cmd_parser.add_argument('-l', action='store_true', help='load from configserver')

        self.mk_conf_inst = configparser.ConfigParser(interpolation=None)

        self.spider_group = []
        self.base_config = {
            'autostart': 'true',
            'startsecs': '5',
            'autorestart': 'true',
            'startretries': '3',
            'user': 'root',
            'stdout_logfile': 'none',
            'stderr_logfile': "none",
            'numprocs_start': '1',
            # 'environment': "xiaoming_env=%s" % os.environ.get('xiaoming_env', 'debug')
        }


    def main(self):
        args = self.cmd_parser.parse_args()
        if args.m:
            try:
                self.make_spiders_config()
            except:
                self.log.warning('生成spiders配置失败')
            try:
                self.make_timers_config()
            except:
                self.log.warning('生成timers配置失败')
            try:
                self.write_run_ini()
            except:
                self.log.warning('写入ini文件失败')
            self.log.info('已重新生成spider_run配置')
        # todo:
        # if args.su:
        #     self._call_start_url(args.su)
        # if args.cs:
        #     self.clear_spider(args.cs)
        if args.l:
            self.load_config()

    def load_config(self):
        self.config.config_server.save_config()

    def write_run_ini(self):
        with open('./config/lilian_run.ini', 'w') as f:
            self.mk_conf_inst.write(f)


    def make_timers_config(self):
        timer_config = self.config.get_config('timer_config')
        for timer_item in timer_config:
            try:
                self.mk_conf_inst['program:%s' % timer_item] = {}
                now_timer_section = self.mk_conf_inst['program:%s' % timer_item]
                file_name = get_file_in_path('timers', 'timer_%s.py' % timer_item, res_bool=False)
                assert file_name, '无此timer code 文件, {}'.format(timer_item)
                now_timer_section['directory'] = os.path.sep.join(file_name.split(os.path.sep)[:-1])
                now_timer_section['command'] = 'python3 timer_%s.py' % timer_item
                now_timer_section['numprocs'] = '1'
                now_timer_section.update(self.base_config)
                now_timer_section['process_name'] = '%(program_name)s_%(process_num)02d'
            except:
                self.mk_conf_inst.pop('program:%s' % timer_item, None)
                self.log.warning('timer={}, 生成run配置失败'.format(timer_item))



    def make_spiders_config(self):
        spider_config = self.config.get_config('spider_config', config_section='spiders')
        self._add_memmon_restart()
        for spider_item in spider_config:
            try:
                self.log.info(f'{spider_item} = {spider_config[spider_item]}')
                self._make_conf_from_spider_item(spider_item, spider_config[spider_item])
            except:
                self.mk_conf_inst.pop('program:%s' % spider_item, None)
                if spider_item in self.spider_group:
                    self.spider_group.remove(spider_item)
                self.log.warning('spider={}, 生成run配置失败'.format(spider_item))
        self._add_spider_group()


    def _add_memmon_restart(self):
        self.mk_conf_inst['eventlistener:memmon'] = {}
        now_spider_section = self.mk_conf_inst['eventlistener:memmon']
        now_spider_section['command'] = 'memmon -g spider=300MB'
        now_spider_section['events'] = 'TICK_60'

    def _make_conf_from_spider_item(self, spider_name, process_num):
        self.spider_group.append(spider_name)
        self.mk_conf_inst['program:%s' % spider_name] = {}
        now_spider_section = self.mk_conf_inst['program:%s' % spider_name]
        file_name = get_file_in_path('spiders', 'spider_%s.py' % spider_name, res_bool=False)
        assert file_name, '无此spider code 文件, {}'.format(spider_name)
        now_spider_section['directory'] = os.path.sep.join(file_name.split(os.path.sep)[:-1])
        now_spider_section['command'] = 'python3 spider_%s.py' % spider_name
        now_spider_section['numprocs'] = str(process_num)
        now_spider_section.update(self.base_config)
        now_spider_section['process_name'] = '%(program_name)s_%(process_num)02d'

    def _add_spider_group(self):
        self.mk_conf_inst['group:spider'] = {}
        now_spider_section = self.mk_conf_inst['group:spider']
        now_spider_section['programs'] = ','.join(self.spider_group)


if __name__ == "__main__":
    spider_run = spider_manager()
    # spider_run.make_spiders_config()
    # spider_run.make_timers_config()
    # spider_run.write_run_ini()
    spider_run.main()