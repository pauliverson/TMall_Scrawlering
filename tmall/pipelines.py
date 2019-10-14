# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import hashlib
import time

from pymysql import cursors
from twisted.enterprise import adbapi
from .settings import *


class TmallPipeline(object):
    def __init__(self):
        dbparams = {
            'host': MYSQL_HOST,
            'port': MYSQL_PORT,
            'user': MYSQL_USER,
            'password': MYSQL_PASSWORD,
            'database': MYSQL_DBNAME,
            'charset': MYSQL_ENCODING,
            'cursorclass': cursors.DictCursor
        }

        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        self._comment_sql = None
        self._detial_sql = None
        self.url_data = {}

    @property
    def commentsql(self):
        if not self._comment_sql:
            self._comment_sql = """
                insert into taobaocomment3(hashurl,usernick,golduser,anony,
                            rateContent,rateDate,ratepics,appendComment,appendTime,appendDays,appendPics,useful) values (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)
                """
            return self._comment_sql
        return self._comment_sql

    @property
    def detialsql(self):
        if not self._detial_sql:
            self._detial_sql = """
                    insert into urldetials3(hashurl,detial,creattime) values (%s, %s, %s)
                    """
            return self._detial_sql
        return self._detial_sql

    def process_item(self, item, spider):
        defer = self.dbpool.runInteraction(self.insert_item, item)
        defer.addErrback(self.handle_error, "process_item is wrong!")

    def insert_item(self, cursor, item):
        if item.get('ratepics') ==None:
            item['ratepics'] = "[]"
        if item.get('appendPics') ==None:
            item['appendPics'] = "[]"
        hash_url = self.url_encrypt(item['url'])
        cursor.execute(self.commentsql, (hash_url, item['usernick'], item['golduser'], item['anony'], item['rateContent'], item['rateDate'],
                                         str(item['ratepics']), item['appendComment'], item['appendTime'], item['appendDays'], str(item['appendPics']), item['useful']))
        #print("储存的HashURL为： %s"%hash_url)
        # if hash_url not in self.url_data:
        #     self.url_data[hash_url] = '{"hash_url":'+item['url']+',"itemId":'+item['itemId']+',"spuId":'+item['spuId']+',"sellerId":'+item['sellerId']+'}'
        

    def handle_error(self, error):
        print('='*10)
        print(error)
        print('='*10)
        
        
    def close_spider(self,spider):
        print("close_spider被调用")
        # defer = self.dbpool.runInteraction(self.insert_detial)
        # defer.addErrback(self.handle_error,"close_spider is wrong!")
        
        
    def insert_detial(self, cursor):
        for key,value in self.url_data.items():
            creattime = time.strftime('%Y.%m.%d %H:%M:%S ', time.localtime(time.time()))
            cursor.execute(self.detialsql, (key, value, creattime))
        print("spider关闭，爬虫获取数据程序结束 ")

    def url_encrypt(self, url):
        """
        使用sha1加密算法，返回str加密后的字符串
        """
        sha = hashlib.sha1(url.encode('utf-8'))
        encrypts = sha.hexdigest()
        return encrypts