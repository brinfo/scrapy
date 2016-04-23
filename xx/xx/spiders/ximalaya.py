# -*- coding: utf-8 -*-
import scrapy
import json
from datetime import datetime

from xx.zhihu_people import ZhihuPeople

class ZhihuSpider(scrapy.Spider):
    name = "ximalaya"
    allowed_domains = ["ximalaya.com", "xmcdn.com"]
    template_url = "http://mobile.ximalaya.com/mobile/playlist/album?albumId=%d&device=android"
    data_root = "mp3"
    albums = [552, 704, 215922]
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'DOWNLOAD_DELAY': 2,
        'COOKIES_DEBUG': True,
        'FEED_FORMAT': 'json',
        'FEED_URI': 'ximalaya.json',
        'MONGO_URI': 'syslog-1',
        'MONGO_DATABASE': 'test',
        'MONGO_COLLECTION': 'ximalaya',
        'RETRY_TIMES': 3,
        'ITEM_PIPELINES': {
            'xx.mongodb.MongoPipeline': 300,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 333,
        }
    }

    def start_requests(self):
        self.logger.info('---CALL start_requests()---')

        requests = []
        for album in self.albums:
            album_url = self.template_url % album
            request = scrapy.Request(url = album_url, callback = self.parse_page)
            requests.append(request)
        return requests

    def parse_page(self, response):
        self.logger.info('---CALL parse_page()---')
        self.logger.info('---response.url = %s', response.url)
        # self.logger.info('---response.body = %s', response.body)
        try:
            j = json.loads(response.body)
            self.logger.info('ret = %s', j["ret"])
            if (j["ret"] == 0):
                for i, track in enumerate(j["data"]):
                    self.logger.info('%03d: %s --- %s', i, track["playUrl64"], track["title"])
                    mp3_url = track["playUrl64"]
                    request = scrapy.Request(url = mp3_url, callback = self.parse_mp3_page)
                    request.meta['track'] = track
                    yield request
        except ValueError, e:
            self.logger.info('---Exception: %s---', e)

    def parse_mp3_page(self, response):
        self.logger.info('---CALL parse_page()---')
        self.logger.info('---response.url = %s', response.url)
        # self.logger.info('---response.body = %s', response.body)
        track = response.meta['track']
        fname =self.data_root + "/" + track["title"] + ".mp3"
        with open(fname, "w") as f:
            f.write(response.body)
