#!/bin/bash
cd /home/spider/lilian
git pull origin master
python /home/spider/lilian/spider_manager.py -m
rm -rf /home/spider/lilian/log/*.log*
exec supervisord -c /home/spider/lilian/supervisor_lilian.conf