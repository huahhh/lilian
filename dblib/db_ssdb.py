# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    db_ssdb.py
   Description :
   Author :       Huahng
   date：          2020/11/18
-------------------------------------------------
"""
__author__ = 'Huahng'

import pyssdb

from lilian.commonlib.catch_retry import catch_retry


class db_ssdb(object):

    def __init__(self, ssdb_host, ssdb_port, **kwargs):
        self.ssdb_conn = pyssdb.Client(host=ssdb_host,
                                       port=ssdb_port,
                                       socket_timeout=kwargs.get('socket_timeout') or 120)

    def __getattr__(self, item):

        ssdb_func = getattr(self.ssdb_conn, item)

        @catch_retry
        def _decode_res(*args, **kwargs):
            '''result decode wraps'''
            res = ssdb_func(*args, **kwargs)
            if res:
                try:
                    if isinstance(res, bytes):
                        return res.decode()
                    elif isinstance(res, list):
                        return [i.decode() if isinstance(i, bytes) else i for i in res]
                    else:
                        return res
                except:
                    return res

        return _decode_res

if __name__ == '__main__':
    ssdb_inst = db_ssdb('182.150.116.30', 25002)
    res = ssdb_inst.hgetall('amap_poi_for_id:monitor')
    print(res)