# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    dingding_talk.py
   Description :
   Author :       Huahng
   date：          2020/12/22
-------------------------------------------------
"""
__author__ = 'Huahng'

from dingtalkchatbot.chatbot import DingtalkChatbot


class dingding_talk(object):

    def __init__(self, web_hook, secret):
        self.web_hook = web_hook
        self.secret = secret

    def dingding_talk(self, msg):
        xiaoding = DingtalkChatbot(self.web_hook, secret=self.secret)
        xiaoding.send_text(msg=msg)