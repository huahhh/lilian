# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    catch_retry.py
   Description :
   Author :       Hu Hang
   date：          2018/3/31
-------------------------------------------------
"""
__author__ = 'HuHang'

import traceback

from tenacity import retry, wait_fixed, stop_after_attempt

def catch_retry(*dargs, **dkw):
    if len(dargs) == 1 and callable(dargs[0]):
        return catch_retry()(dargs[0])
    def decorator(func):
        @retry(
            wait=wait_fixed(1),
            stop=stop_after_attempt(dkw.get("retry_count", 10)),
               )
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                from lilian.commonlib.logger import logger
                logger = logger('catch_retry')
                logger.error('执行函数{func}出错,error_info:{error_info}'.format(func=func.__name__,
                                                                           error_info=traceback.format_exc()))
                raise e
        return wrapper
    return decorator


if __name__ == '__main__':
    @catch_retry(5)
    def t():
        print('a')
        raise
    t()
