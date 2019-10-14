# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, Join


def parse_field(list_):
    return str(list_).strip()

# 用于存储数据到Pipeline
class TmallItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    #这部分是关于卖家信息
    url = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )
    
    itemId = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )
    spuId = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )
    sellerId = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )
    
    # 这部分是关于买家的相关信息
    usernick = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )   #买家姓名
    golduser = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )   #是否超级会员
    anony = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )  #是否匿名评论
    rateContent = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )    #初次评价内容
    rateDate = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )   #初次评价时间
    
    ratepics = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(";")
    )        #初次评论上传的图片
    
    appendComment = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )  #追加评论内容
    appendTime = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )    #追加评论时间
    appendDays = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )    #过了多少天后追加评论
    
    appendPics = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(";"),
    )     #追评添加的图片
    
    useful = scrapy.Field(
        input_processor=MapCompose(parse_field),
        output_processor=Join(),
    )     #此评论是有有效
    

# class SellerMeta():
#     # def __init__(self,sellerId,itemId,spuId):
#         # self
#     pass