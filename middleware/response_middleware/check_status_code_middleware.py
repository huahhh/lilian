# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    check_status_code_middleware.py
   Description :
   Author :       Huahng
   date：          2020/12/2
-------------------------------------------------
"""
__author__ = 'Huahng'


class check_status_code_middleware(object):

    def middleware_process(self, resp_inst, spider_inst):
        retry_http_code = resp_inst.seed_inst.retry_http_code or spider_inst.retry_http_code
        if not retry_http_code:
            return resp_inst
        if resp_inst.response.status_code in retry_http_code:
            spider_inst.log.warning('因response返回的http_status_code为%s, 在retry_http_code中，故重新请求' %
                            resp_inst.response.status_code)
            raise Exception('http_status_code in retry_http_code')
        return resp_inst