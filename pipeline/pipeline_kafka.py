# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    pipeline_kafka.py
   Description :
   Author :       Huahng
   date：          2021/6/21
-------------------------------------------------
"""
__author__ = 'Huahng'

import msgpack

from kafka import KafkaProducer

from lilian.pipeline.pipeline_base import pipeline_base

class pipeline_kafka(pipeline_base):

    def __init__(self):
        #TODO need test
        super(pipeline_kafka, self).__init__()
        self.kafka_config = self.config.get_config(config_type="db_config", config_section="kafka")
        kafka_bootstrap_servers_config = self.kafka_config.pop('kafka_bootstrap_servers')
        assert kafka_bootstrap_servers_config, "kafka_bootstrap_servers is None"
        self.kafka_bootstrap_servers = eval(kafka_bootstrap_servers_config)
        self.kafka_producer = KafkaProducer(bootstrap_servers = self.kafka_bootstrap_servers,
                                            value_serializer=msgpack.dumps,
                                            max_request_size=40 * 1000 * 1000,
                                            **self.kafka_config)

    def item_process(self, item):
        spider_name = item.get('table_name') or item.get('spider_name')
        kafka_producer_stats = self.kafka_producer.send('-'.join([spider_name, 'raw_data']),
                                                        key=None,
                                                        value=item)
        kafka_producer_stats.get(timeout=10)
        return True

