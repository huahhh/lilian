# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    downloader.py
   Description :
   Author :       Huahng
   date：          2020/11/26
-------------------------------------------------
"""
__author__ = 'Huahng'

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import time
import random

from requests import session

from lilian.config.config import config
from lilian.commonlib.logger import logger
from lilian.proxy.proxy_handler import proxy
from lilian.commonlib.catch_retry import catch_retry
from lilian.downloader.resp import resp


pc_user_agent_pool = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36",
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 GTB6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36'
]

mobile_user_agent_pool = [
    'Mozilla/5.0 (Linux; Android 4.4.4; MI 2 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 2.2; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
    'Mozilla/5.0 (Linux; U; Android 4.2.1; zh-cn; HUAWEI G700-U00 Build/HuaweiG700-U00) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (Linux; U; Android 5.0.2; zh-CN; Redmi Note 3 Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 OPR/11.2.3.102637 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (Linux; Android 6.0.1; OPPO R9sk Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.76 Mobile Safari/537.36 JsSdk/2 joke_essay_6.3.3',
    'Mozilla/5.0 (Linux; U; Android 4.3; zh-cn; Coolpad 8720L Build/JSS15Q) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (Linux; Android 4.4.4; R8107 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/33.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0; vivo Y67 Build/MRA58K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 4.2.2; zh-cn; VANHON-A60 Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30 ImgoTV-aPhone/5.3.1'
    'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'Mozilla/5.0 (iPhone; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
    'Mozilla/5.0 (iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/6.0 MQQBrowser/4.3 Mobile/9B206 Safari/7534.48.3',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'Mozilla/5.0 (iPad; CPU OS 8_0_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A405 Safari/600.1.4',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Version/10.0 Mobile/14D27 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.0 Mobile/14F89 Safari/602.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
]

ua_pool_dict = {
    'pc': pc_user_agent_pool,
    'mobile': mobile_user_agent_pool,
}


class downloader(object):
    #todo: spider级别的http默认参数

    def __init__(self, user_agent_type='pc'):
        self.config = config()
        self.use_proxy = self.config.get_config('frame_config', config_section='proxy_config', config_item='use_proxy')

        self.log = logger('downloader')
        self.ss = session()

        self.ua_pool = ua_pool_dict.get(user_agent_type, pc_user_agent_pool)
        self.proxy_interface = proxy()
        self.http_proxy = self.get_proxy()

    @catch_retry(retry_count=10)
    def req(self, seed):
        try:
            self.log.info('开始请求方法为 : [{method}], url : {url}, proxy : {proxy}'.format(
                url=seed.url,
                method=seed.method.upper(),
                proxy=self.http_proxy.get('http', '') if self.http_proxy else self.http_proxy
                ))
            now_time = time.time()


            http_params = self.merger_http_params(seed.http_params)

            raw_resp = self.ss.request(seed.method, seed.url, **http_params)

            resp_inst = resp(raw_resp, seed)

            self.log.info('请求成功, 即将返回至spider. ')
            self.log.info('本次请求耗时<%.3fs>' % (time.time() - now_time))

            return resp_inst
        except Exception as e:
            self.http_error_callback(seed)
            raise e

    def http_error_callback(self, seed):
        if not seed.http_params.get('use_proxy') is False and self.use_proxy:
            self.log.info('请求失败，尝试更换代理进行重试')
            self.change_proxy()

    def get_proxy(self):
        return self.proxy_interface.get_proxy if self.use_proxy else None

    def change_proxy(self):
        self.http_proxy = self.get_proxy()
        if self.http_proxy:
            self.log.info('downloader切换代理为%s' % self.http_proxy.get('http', ''))

    def merger_http_params(self, http_params):
        seed_proxies = None

        if isinstance(http_params.get('proxies'), dict):
            if 'http' in http_params.get('proxies') and 'https' in http_params.get('proxies'):
                seed_proxies = http_params.get('proxies')
            else:
                self.log.warning('seed传入代理, 但代理格式不正确, 故不做使用, {}'.format(str(http_params.get('proxies'))))

        return {
            'params': http_params.get('params'),
            'data': http_params.get('data'),
            'headers': self.generate_header(http_params.get('headers')),
            'cookies': http_params.get('cookies'),
            'files': http_params.get('files'),
            'auth': http_params.get('auth'),
            'timeout': http_params.get('timeout') or 30,
            'allow_redirects': http_params.get('allow_redirects') or True,
            'proxies': seed_proxies or self.http_proxy,
            'hooks': http_params.get('hooks'),
            'stream': http_params.get('stream'),
            'verify': http_params.get('verify') or False,
            'cert': http_params.get('cert'),
            'json':  http_params.get('json'),
        }

    def generate_header(self, seed_headers):
        base_header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self._get_ua()
        }
        if isinstance(seed_headers, dict):
            base_header.update(seed_headers)
        return base_header


    def _get_ua(self):
        return random.choice(self.ua_pool)

    def clear_cookies(self):
        self.ss.cookies.clear()

    def generate_cookie(self):
        pass


if __name__ == '__main__':
    d = downloader()
    d.req('1')