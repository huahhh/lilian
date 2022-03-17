# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    spider_base.py
   Description :
   Author :       Huahng
   date：          2020/11/23
-------------------------------------------------
"""


__author__ = 'Huahng'

import os
import copy
import json
import time
import signal
import traceback

from collections import Iterable

from lilian.config.config import config
from lilian.monitor.monitor import monitor
from lilian.commonlib.logger import logger
from lilian.seed.spider_seed import spider_seed
from lilian.commonlib.duplicate import duplicate
from lilian.downloader.downloader import downloader
from lilian.seed_queue.seed_queue import seed_queue
from lilian.commonlib.catch_retry import catch_retry
from lilian.pipeline.pipeline_handler import pipeline_handler
from lilian.middleware.middleware_handler import middleware_handler


class spider_base(object):
    #todo: cookie enlable
    # todo: fast cookie
    #todo: 梳理请求结构图， 多出错节点的相关处理
    #todo: 梳理pipeline

    spider_name = None
    method = "get"
    encoding = None
    check_html_func = None
    base_headers = {}
    retry_http_code = []
    cookie_enable = False
    retry_error = False
    queue_none_time = None
    ua_pool_type = 'pc'   # pc or mobile
    spider_req_middleware = []
    spider_resp_middleware = []
    pipeline_type = ['result_data']



    def __init__(self):

        assert self.spider_name , 'Must be defined spider_name'

        self.log = logger(self.spider_name)
        self.config = config()
        self.downloader = downloader(user_agent_type=self.ua_pool_type)
        self.seed_queue = seed_queue(self.spider_name)
        self.result_pipeline = pipeline_handler(self.spider_name)
        self.monitor = monitor()
        self.dup = duplicate(spider_name=self.spider_name)
        self.base_req_middleware = ['seed_base']
        self.base_resp_middleware = ['html_encoding', 'check_status_code', 'check_html']
        self.middleware_handler_inst = middleware_handler(
            request_middleware_list = self.base_req_middleware + self.spider_req_middleware,
            response_middleware_list = self.base_resp_middleware + self.spider_resp_middleware
        )

        self.page_dict = {}
        self.global_dict = {}

        self._spider_init()
        self.spider_init()

        pass

    def _spider_init(self):
        self.log.info('spider=<%s>, 开始启动. ' % self.spider_name)
        self.signal_init()
        self._page_dict_reload()
        self._init_cookies()
        self._retry_error()

    def _init_cookies(self):
        if hasattr(self, 'get_cookies'):
            for item in self.get_cookies():
                item.seed_raw['suffix'] = 'cookies'
                self._func_result_handler(item)

    def spider_init(self):
        pass

    def spider_seed_handler(self, seed_inst):
        '''需复写函数，供于子类对seed_item做请求前的前序处理'''
        return seed_inst

    def run(self):
        while True:
            try:
                self._run_once()
            except:
                self.log.error('运行spider-%s, 出错.' % self.spider_name)
                self.log.error(traceback.format_exc())
                self.log.error('休眠5s')
                time.sleep(5)
            finally:
                self._run_once_after()

    def _run_once_before(self):
        pass

    def _run_once_after(self):
        self._page_dict_reload()

    def _page_dict_reload(self):
        self.page_dict = {
            'seed_inst': None,
            'resp': None
        }

    def _run_once(self):
        seed_inst = self._get_seed_inst()
        if not seed_inst:
            return

        seed_inst = self.spider_seed_handler(seed_inst)

        self.page_dict['seed_inst'] = seed_inst

        if not seed_inst.url:
            self.log.info('该种子无url, 故将seed直接传入parser_func处理, parser={}, seed_info={}'.format(
                seed_inst.parser_func, seed_inst.seed_raw
            ))
            self._seed_not_need_http(seed_inst)
            return

        seed_inst = self._request_middleware_handler(seed_inst)

        if seed_inst is None:
            self.log.warning('因request中间件返回None, 故中断此次运行')
            return

        try:
            resp = self._get_response(seed_inst)
        except:
            self.log.error('req retry error')
            self.log.error(traceback.format_exc())
            self.seed_queue.put_error(seed_inst.seed_raw)
            return

        if resp is None:
            self.log.warning('downloader or response_middleware返回None, 运行中断')
            return

        self.page_dict['resp'] = resp

        parser_func_inst = getattr(self, seed_inst.parser_func)

        try:
            parser_func_result = parser_func_inst(resp)
        except:
            self.log.error('parser func error')
            self.log.error(resp.res_text)
            self.log.error(traceback.format_exc())
            self.seed_queue.put_error(seed_inst.seed_raw)
            return

        self._parser_func_handler(parser_func_result)

    def _get_seed_inst(self):
        raw_seed = self.seed_queue.get_seed()
        if raw_seed:
            try:
                if 'method' not in raw_seed: raw_seed['method'] = self.method
                seed_inst = spider_seed(raw_seed)
                return seed_inst
            except:
                self.log.error('从队列拿到原始seed后生成seed对象出错, 即将把原始seed放入error队列.')
                self.seed_queue.put_error(raw_seed, sleep_time=0)
                self.log.error(traceback.format_exc())
        else:
            self.log.info('所有队列为空, 休眠{}秒.'.format(self.queue_none_time or 120))
            time.sleep(self.queue_none_time or 120)
            return

    @catch_retry
    def _get_response(self, seed):
        try:
            resp = self.downloader.req(seed)
        except:
            self.log.warning('请求出错, 即将将seed写入error队列')
            self.seed_queue.put_error(seed.seed_raw)
            return
        try:
            resp = self._response_middleware_handler(resp)
        except:
            self.log.info('response middleware报错, 更换代理重新请求.')
            self.downloader.change_proxy()
            if seed.cookies_func and seed.parser_func != "parser_cookies":
                self.reload_cookie(seed)
                return
            raise Exception('重新请求')

        return resp

    def _func_result_handler(self, item):
        if item:
            if isinstance(item, spider_seed):
                self.seed_queue.put_seed(item.seed_dict())
            elif isinstance(item, dict):
                self.seed_queue.put_seed(item)
            elif isinstance(item, list):
                for i in item:
                    self._func_result_handler(i)
            else:
                self.log.warning('不在预期范围内的seed处理类型, {}'.format(str(item)))
        else:
            self.log.warning('seed为空类型, {}'.format(str(item)))


    def _parser_func_handler(self, parser_func_result):
        try:
            if parser_func_result is None:
                self.log.info('parser_func, 未返回任何需处理对象')
            elif isinstance(parser_func_result, list):
                if not parser_func_result:
                    self.log.info('parser_func, 返回一个空列表')
                else:
                    for item in parser_func_result:
                        self._parser_func_handler(item)
            elif isinstance(parser_func_result, Iterable):
                for result_item in parser_func_result:
                    self._func_result_handler(result_item)
            elif isinstance(parser_func_result, spider_seed):
                self._func_result_handler(parser_func_result)
            else:
                self.log.info('parser_func, 不在预期范围内的返回, {}'.format(str(parser_func_result)))
        except:
            self.log.error('parser出错，即将写入error_html队列')
            self.log.error(traceback.format_exc())
            self.seed_queue.put_error(self.page_dict['seed_inst'].seed_raw, resp=self.page_dict['resp'])

    def _seed_not_need_http(self, seed):
        parser_func_inst = getattr(self, seed.parser_func)
        self._parser_func_handler(parser_func_inst(seed))

    def _request_middleware_handler(self, seed_inst):
        try:
            mid_seed_inst = self.middleware_handler_inst.res_middleware_handler(seed_inst, self)
            return mid_seed_inst
        except:
            self.seed_queue.put_error(seed_inst)

    def _response_middleware_handler(self, resp):
        mid_resp_inst = self.middleware_handler_inst.resp_middleware_handler(resp, self)
        return mid_resp_inst

    def debug_for_start_url(self, raw_seed=None):
        start_url_func = self.start_url(raw_seed)
        self._parser_func_handler(start_url_func)

    def start_url(self, raw_seed=None):
        pass

    def make_seed(self, url, parser_func, check_html_func=None, encoding=None, retry_http_code=None, meta=None,
                  suffix=None, method=None, params=None, data=None, headers=None, cookies=None, files=None, auth=None,
                  timeout=None, allow_redirects=None, proxies=None, hooks=None, stream=None, verify=None, cert=None,
                  json=None, cookies_func=None, *args, **kwargs):
        assert hasattr(parser_func, '__call__'), "parser_func must be function"
        seed_dict_tmp = {
            'url': url,
            'parser_func': parser_func.__name__,
            'method': method or self.method,
            'suffix': suffix or self._get_seed_suffix(),
            'check_html_func': check_html_func or self.check_html_func,
            'retry_http_code': retry_http_code or self.retry_http_code,
            'encoding': encoding or self.encoding,
            'params': params,
            'meta': meta or {},
            'data': data,
            'headers': headers or self.base_headers,
            'cookies': cookies,
            'files': files,
            'auth': auth,
            'timeout': timeout,
            'allow_redirects': allow_redirects,
            'proxies': proxies,
            'hooks': hooks,
            'stream': stream,
            'verify': verify,
            'cert': cert,
            'json': json,
            'cookies_func': cookies_func.__name__ if cookies_func else None
        }

        if seed_dict_tmp['check_html_func']:
            if hasattr(seed_dict_tmp['check_html_func'], '__call__'):
                seed_dict_tmp['check_html_func'] = seed_dict_tmp['check_html_func'].__name__

        seed_dict = {}
        for seed_item in seed_dict_tmp:
            if seed_dict_tmp[seed_item] is not None:
                seed_dict[seed_item] = seed_dict_tmp[seed_item]
        return spider_seed(seed_dict, *args, **kwargs)

    def _get_seed_suffix(self):
        suffix = 'seed'
        if 'seed_inst' in self.page_dict:
            try:
                suffix = self.page_dict['seed_inst'].seed_dict().get('suffix', "seed")
            except:
                pass
        return suffix

    def _retry_error(self):
        if self.retry_error:
            self.seed_queue.queue_suffix += ['error']

    def web_api_done(self, res):
        put_data = res.seed_raw.get('data') or res.seed_raw.get('json') or '{}'
        if put_data:
            if isinstance(put_data, list):
                put_data = {'data': put_data}
            self.save_result(put_data)
        self.log.info(res.res_text)

    def check_html_true(self, res):
        return True

    def parser_cookies(self, res):
        self.log.info("get cookies from <%s>" % res.response.cookies)

    def reload_cookie(self, seed):
        self.log.warning('请求出错, 且seed存在cookies_func, 尝试重新取得cookies')
        if 'cookie_last' in seed.meta:
            seed.meta['cookie_last'] -= 1
        else:
            seed.meta['cookie_last'] = 10

        if seed.meta['cookie_last'] == 0:
            self.seed_queue.put_error(seed.seed_raw)
            return

        self.downloader.clear_cookies()
        self.log.info('清理session的cookies')
        cookies_func = getattr(self, seed.cookies_func)
        self.log.info('使用cookies_func为<{}>'.format(seed.cookies_func))
        for cookies_seed_item in  cookies_func():
            cookies_seed_item.seed_raw['suffix'] = 'cookies'
            self._func_result_handler(cookies_seed_item)
        self._func_result_handler(seed)

    def save_result(self, result_dict, pipeline_type=None):
        pipeline_type = pipeline_type or self.pipeline_type
        if not pipeline_type or not (isinstance(pipeline_type, list) or isinstance(pipeline_type, str)):
            raise Exception('错误的pipeline_type, {}'.format(str(pipeline_type)))
        if isinstance(result_dict, dict):
            result_dict = copy.deepcopy(result_dict)
            result_monitor_name = result_dict.pop('result_monitor_name', None) or self.spider_name
            save_status = self.result_pipeline.pipeline_item_process(result_dict, self.page_dict['resp'], pipeline_type)
            if save_status:
                self.monitor.hincrby_spider_name(result_monitor_name)
        elif isinstance(result_dict, list):
            result_ = {'result': result_dict}
            self.save_result(result_)
        else:
            if result_dict:
                self.log.info('save的对象不为dict, 故被抛弃, %s' % str(result_dict))
            else:
                self.log.info('save了一个空对象, 故被抛弃')

    def clear_all_queue(self):
        pass

    def signal_handle(self, *args , **kwargs):
        self.log.info('进程退出，seed回灌.')
        seed_inst = self.page_dict['seed_inst']
        if isinstance(seed_inst, spider_seed):
            self.seed_queue.put_seed(seed_inst.seed_dict())
        elif isinstance(seed_inst, dict):
            self.seed_queue.put_seed(seed_inst)
        else:
            self.log.info('未确定的类型的seed, %s' % str(seed_inst))
        os._exit(0)

    def signal_init(self):
        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, self.signal_handle)
