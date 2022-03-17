# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    spider_seed.py
   Description :
   Author :       Huahng
   date：          2020/11/26
-------------------------------------------------
"""
__author__ = 'Huahng'


class spider_seed(object):

    url = None
    parser_func = None
    suffix = None
    meta = None
    table_name = None

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], dict):
            kwargs.update(args[0])
        assert 'parser_func' in kwargs, "无parser_func, 不符合seed对象基本格式"

        if kwargs.get('url') and kwargs.get('method'):
            assert kwargs.get('method').upper() in ('GET',
                                                    'OPTIONS',
                                                    'HEAD',
                                                    'POST',
                                                    'PUT',
                                                    'PATCH',
                                                    'DELETE'), 'http method error'

        self.http_params_field_list = ['params', 'data', 'headers', 'cookies', 'files', 'auth', 'timeout',
                                       'allow_redirects', 'proxies', 'hooks', 'stream', 'verify', 'cert', 'json']
        self.seed_field_list = ['url', 'parser_func', 'suffix', 'meta', 'check_html_func', 'retry_http_code', 'method',
                                'cookies_func']
        self.seed_raw = kwargs
        for seed_field_item in self.seed_field_list:
            setattr(self, seed_field_item, kwargs.get(seed_field_item))

        self.http_params = self._merger_http_params(kwargs)

    def _merger_http_params(self, kw):
        return {i: kw[i] for i in self.http_params_field_list if i in kw}

    def seed_dict(self):
        return self.seed_raw


if __name__ == '__main__':
    seed_inst = spider_seed({'parser_func': 'test'})
    print(seed_inst)
