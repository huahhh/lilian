# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    middleware_handler.py
   Description :
   Author :       Huahng
   date：          2020/11/30
-------------------------------------------------
"""
__author__ = 'Huahng'

import copy
import importlib
import traceback

from lilian.commonlib.logger import logger
from lilian.commonlib.pathlib import get_file_in_path
from lilian.commonlib.constant import project_name
from lilian.seed.spider_seed import spider_seed
from lilian.downloader.resp import resp

class middleware_handler(object):

    def __init__(self, request_middleware_list, response_middleware_list):
        self.log = logger('middleware')
        self.request_middleware_list = request_middleware_list
        self.response_middleware_list = response_middleware_list
        self.middleware_dict = {'req': {},
                                'resp': {}}
        self.middleware_init(self.request_middleware_list, self.response_middleware_list)

    def middleware_init(self, request_middleware_list, response_middleware_list):
        for res_middleware_item in request_middleware_list:
            res_middleware_inst = self.load_middleware(res_middleware_item, 'request')
            if res_middleware_inst:
                self.middleware_dict['req'][res_middleware_item] = res_middleware_inst

        for resp_middleware_item in response_middleware_list:
            resp_middleware_inst = self.load_middleware(resp_middleware_item, 'response')
            if resp_middleware_inst:
                self.middleware_dict['resp'][resp_middleware_item] = resp_middleware_inst

    def load_middleware(self, middleware_item, middleware_type):
        try:
            assert get_file_in_path('middleware', '{middleware_item}_middleware.py'.format(
                middleware_item=middleware_item), res_bool=True), '{} middleware not fount'.format(middleware_item)
            return getattr(
                importlib.import_module(
                    '{}.middleware.{}_middleware.{}_middleware'.format(project_name, middleware_type, middleware_item)),
                '{}_middleware'.format(middleware_item))()
        except AssertionError:
            self.log.warning('因无此文件, 故无法初始化该middleware, {}'.format(middleware_item))
        except:
            self.log.warning('初始化middleware失败, {}'.format(middleware_item))
            self.log.warning(traceback.format_exc())

    def res_middleware_handler(self, seed_inst, spider_inst):
        for middleware_inst_item in self.request_middleware_list:
            if middleware_inst_item not in self.middleware_dict['req']:
                self.log.warning('该middleware未初始化, 故不处理, 请注意排查, {}'.format(middleware_inst_item))
                continue
            try:
                seed_inst_copy = copy.deepcopy(seed_inst)
                seed_inst = self.middleware_dict['req'][middleware_inst_item].middleware_process(
                    seed_inst, spider_inst)
                if seed_inst is None:
                    return
                if not isinstance(seed_inst, spider_seed):
                    return seed_inst_copy
            except Exception as e:
                self.log.warning('request_middleware出错, 即将把种子放入error队列, {}'.format(middleware_inst_item))
                self.log.warning(traceback.format_exc())
                raise e

        return seed_inst

    def resp_middleware_handler(self, resp_inst, spider_inst):
        for middleware_inst_item in self.response_middleware_list:
            if middleware_inst_item not in self.middleware_dict['resp']:
                self.log.warning('该middleware未初始化, 故不处理, 请注意排查, {}'.format(middleware_inst_item))
                continue
            try:
                resp_inst_copy = copy.deepcopy(resp_inst)
                resp_inst = self.middleware_dict['resp'][middleware_inst_item].middleware_process(
                    resp_inst, spider_inst
                )
                if resp_inst is None:
                    return
                if not isinstance(resp_inst, resp):
                    return resp_inst_copy
            except Exception as e:
                self.log.warning('response_middleware出错, 即将重新请求, {}'.format(middleware_inst_item))
                self.log.warning(traceback.format_exc())
                raise e

        return resp_inst




