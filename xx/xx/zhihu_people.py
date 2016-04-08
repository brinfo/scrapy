# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ZhihuPeople(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    bio = scrapy.Field()
    location = scrapy.Field()
    business = scrapy.Field()
    gender = scrapy.Field()
    employment = scrapy.Field()
    position = scrapy.Field()
    education = scrapy.Field()
    educationextra = scrapy.Field()
    content = scrapy.Field()
    marked = scrapy.Field()
    useragree = scrapy.Field()
    userthanks = scrapy.Field()
    asks = scrapy.Field()
    answers = scrapy.Field()
    posts = scrapy.Field()
    collections = scrapy.Field()
    logs = scrapy.Field()
    followees = scrapy.Field()
    followers = scrapy.Field()
    columnsfollowed = scrapy.Field()
    topics = scrapy.Field()
    browsers = scrapy.Field()

