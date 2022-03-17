# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    check_html_middleware.py
   Description :
   Author :       Huahng
   date：          2020/12/2
-------------------------------------------------
"""
__author__ = 'Huahng'

from inspect import isfunction

class check_html_middleware(object):

    def middleware_process(self, resp_inst, spider_inst):
        check_html_function = resp_inst.seed_inst.check_html_func or spider_inst.check_html_func
        if not check_html_function:
            return resp_inst

        if isinstance(check_html_function, str):
            if not hasattr(spider_inst, resp_inst.seed_inst.check_html_func):
                spider_inst.log.warning('spider缺少配置的check_html_func方法=<%s>，请检查. ' %
                                   resp_inst.seed_inst.check_html_func)
            check_html_res = getattr(spider_inst, resp_inst.seed_inst.check_html_func)(resp_inst)
        elif isfunction(check_html_function):
            check_html_res = check_html_function(resp_inst)
        else:
            spider_inst.log.warning('不正确的check_html_func类型, {}'.format(str(check_html_function)))
            return resp_inst

        if check_html_res is False:
            raise Exception('check_html检查未通过')
        return resp_inst