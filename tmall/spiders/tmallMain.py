# -*- coding: utf-8 -*-
import hashlib
import sys
import json
import time
import re

import requests
import scrapy
from scrapy.loader import ItemLoader

from ..items import TmallItem


index_all = 0

class TmallmainSpider(scrapy.Spider):
    name = 'tmallMain'
    allowed_domains = ['tmall.com']
    start_urls = ["https://rate.tmall.com/list_detail_rate.htm?itemId=545129870941&spuId=722445115&sellerId=554185355&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&_ksTS=1560173759587_1857&callback=jsonp1858"]

    def __init__(self, url_lists):
        super(TmallmainSpider, self).__init__()
        # print("__init__:  "+url_lists)
        # print(type(url_lists))
        self.url_lists = url_lists
    
    
    def start_requests(self):
        """
        根据提供的URL得到seller的相关信息，然后探测评论总页数
        :yield: scrapy.Request
        """
        print("进来了start_requests方法")
        for item_url in self.getPageURLs():
            try:
                yumingzidaun = item_url.split("/")[2]
            except:
                yumingzidaun = ""
            if "tmall" in yumingzidaun:
                yield scrapy.Request(url=item_url, callback=self.parse_TmallPages,meta={"url":item_url})
            elif "taobao" in yumingzidaun:
                yield scrapy.Request(url=item_url, callback=self.parse_TaobaoPages,meta={"url":item_url})
            else:
                with open("wrongURL.txt","a",encoding="utf-8") as fw:
                    fw.write(str(item_url))
                print("网址出现错误，非淘宝、天猫域名URL")
                print("错误网址为： %s"%item_url)
    
    
    # 获取评论页数的方法
    
    def getPageURLs(self):
        """
        将spider初始化时候获取的URL字符串转化为列表
        :return:
        """
        return self.url_lists.split(",")
        
    
    def getCommentNums(self,response):
        html = response.text.encode("gbk", "ignore").decode("gbk")[12:-1]
        datas_ = json.loads(html)
        pages_num = datas_['rateDetail']['paginator']['lastPage']
        sellerMeta = response.meta["sellerMeta"]
        for index in range(pages_num):
            item_itemId = sellerMeta['itemId']
            item_sellerId = sellerMeta['sellerId']
            item_spuId = sellerMeta['spuId']
            url_aim = "https://rate.tmall.com/list_detail_rate.htm?itemId=" + item_itemId + "&spuId=" + item_spuId + "&sellerId=" +\
                      item_sellerId + "&order=3&currentPage=" + str(index + 1) + \
                      "&append=0&content=1&tagId=&posi=&picture=&groupId=&_ksTS=1560173759587_1857&callback=jsonp1858"
            yield scrapy.Request(url=url_aim, callback=self.parse_Commentdata,meta={"sellerMeta":sellerMeta},dont_filter=True)
    
    # 如果判定是taobao.com域名的话，运用处理淘宝的办法获取卖家信息，并且抛出Scrapy.Request对象获取具体评论数据
    def parse_TaobaoPages(self,response):
        html = response.text
        search_ = re.search(r'feedRateList.htm\?userNumId=(.*?)&amp;auctionNumId=(.*?)&amp;siteId=(.*?)&amp;spuId=(.*?)"',html)
        sellerId = search_.group(1)
        itemId = search_.group(2)
        spuId = search_.group(4)
        url_aim = "https://rate.tmall.com/list_detail_rate.htm?itemId=" + itemId + "&spuId=" + spuId+ \
                  "&sellerId=" + sellerId + "&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&_ksTS=1560173759587_1857&callback=jsonp1858"
        hash_url = response.meta["url"]
        yield scrapy.Request(url=url_aim, callback=self.getCommentNums, meta={"sellerMeta":{'sellerId':sellerId,'itemId':itemId,'spuId':spuId,'url':hash_url}})
    
    #如果判断是tmall.com域名的话，运用处理天猫的办法获取卖家信息，并且抛出Scrapy.Request对象获取具体评论数据
    def parse_TmallPages(self,response):
        html = response.text
        search_1 = re.search(r'"itemId":([0-9]{4,}),"sellerId":([0-9]{4,}),"rateScoreCacheDisable', html)
        search_2 = re.search(r'"spuId":"([0-9]+)",', html)
        # print(search_1)
        itemId = ''
        sellerId = ''
        spuId = ''
        try:
            itemId = search_1.group(1)
            sellerId = search_1.group(2)
            spuId = search_2.group(1)
        except:
            print("网址有误")
            return
        url_aim = "https://rate.tmall.com/list_detail_rate.htm?itemId=" + itemId + "&spuId=" + spuId + \
                  "&sellerId=" + sellerId + "&order=3&currentPage=1&append=0&content=1&tagId=&posi=&picture=&groupId=&_ksTS=1560173759587_1857&callback=jsonp1858"
        hash_url = response.meta["url"]
        yield scrapy.Request(url=url_aim, callback=self.getCommentNums,
                             meta={"sellerMeta": {'sellerId': sellerId, 'itemId': itemId, 'spuId': spuId,'url':hash_url}})

    
    
    # 最终分析数据的地方
    def parse_Commentdata(self, response):
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        datav = response.text.translate(non_bmp_map)[12:-1]
        datas = json.loads(datav)
        rateList = datas['rateDetail']['rateList']
        sellerMeta = response.meta["sellerMeta"]
        # index_ = 0
        #print(rateList)
        #print("++"*30)
        for item in rateList:
            # ItemLoader方式
            goods_item_loader = ItemLoader(item=TmallItem(), response=response)
            goods_item_loader.add_value("url",sellerMeta["url"])
            goods_item_loader.add_value("itemId",sellerMeta["itemId"])
            goods_item_loader.add_value("spuId",sellerMeta["spuId"])
            goods_item_loader.add_value("sellerId",sellerMeta["sellerId"] )   #2765010761
            goods_item_loader.add_value("usernick",item['displayUserNick'] ) # 买家姓名
            goods_item_loader.add_value("golduser",item['goldUser'])  # 是否超级会员
            goods_item_loader.add_value("anony",item['anony'])  # 是否匿名评论
            goods_item_loader.add_value("rateContent",item['rateContent'])  # 初次评价内容
            goods_item_loader.add_value("rateDate", item['rateDate'])  # 初次评价时间
            goods_item_loader.add_value("ratepics", item['pics'])  # 初次评论上传的图片
            goods_item_loader.add_value("useful","True" if item['useful'] else "False")  # 此评论是有有效
            if item['appendComment']==None:
                goods_item_loader.add_value("appendComment", "")  # 追加评论内容
                goods_item_loader.add_value("appendTime", "")  # 追加评论时间
                goods_item_loader.add_value("appendDays", "")  # 过了多少天后追加评论
                goods_item_loader.add_value("appendPics", "")  # 追评添加的图片
            else:
                goods_item_loader.add_value("appendComment", item['appendComment']['content'])  # 追加评论内容
                goods_item_loader.add_value("appendTime", item['appendComment']['commentTime'])  # 追加评论时间
                goods_item_loader.add_value("appendDays", item['appendComment']['days'])  # 过了多少天后追加评论
                goods_item_loader.add_value("appendPics", item['appendComment']['pics'])  # 追评添加的图片
            global index_all
            print("第 %s 个item被跑过去pipeline"%(index_all))
            index_all = index_all+1
            yield goods_item_loader.load_item()


















