# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    spider_dongqiudi.py
   Description :
   Author :       Huahng
   date：          2021/6/18
-------------------------------------------------
"""
__author__ = 'Huahng'

import json

from lilian.core.spider_base import spider_base

class spider_dongqiudi(spider_base):

    spider_name = 'dongqiudi'
    base_url = "https://*/sport-data/soccer/biz/data/person_ranking?season_id=2018&app=dqd&version=0&" \
               "platform=web&type=goals"

    def spider_init(self):
        self.web_api_host = self.config.get_config('frame_config', config_section='web_api_host', config_item='host')

    def start_url(self, raw_seed=None):
        yield self.make_seed(self.base_url,
                             parser_func=self.parser)

    def parser(self, res):
        data = res.res_json.get('content', {}).get('data', [])
        assert data, "data is empty list"
        result_list = []
        for item in data:
            person_count = item.get('count', '')
            if '(' in person_count:
                goals_num, penalty_num = person_count.split('(')
            else:
                goals_num, penalty_num = person_count, '0'
            result_list.append({
                "player_name": item.get('person_name', ''),
                "player_avatar": item.get('person_logo', ''),
                "player_team": item.get('team_name', ''),
                'goals_num': int(goals_num),
                'penalties_num': int(penalty_num.strip(')'))
            })
        result = {"datas": result_list}
        yield self.save_result(result)

if __name__ == '__main__':
    spider_inst = spider_dongqiudi()
    # spider_inst.debug_for_start_url()
    spider_inst.run()