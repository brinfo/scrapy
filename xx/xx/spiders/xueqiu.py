# -*- coding: utf-8 -*-
import scrapy
import json


class XueqiuSpider(scrapy.Spider):
    name = "xueqiu"
    allowed_domains = ["xueqiu.com"]
    # 'http://xueqiu.com/stock/cata/stocklist.json?order=desc&orderby=percent&type=11%2C12&size=30&page=1'
    prefix_pageurl = 'http://xueqiu.com/stock/cata/stocklist.json?size=30&order=desc&orderby=percent&type=11%2C12'
    # prefix_stockurl = 'http://xueqiu.com/S/'
    prefix_stockurl = 'http://xueqiu.com/recommend/pofriends.json?type=1&code='
    page_size = 30
    pages = 1
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'COOKIES_DEBUG': True,
        'FEED_FORMAT': 'json',
        # 'FEED_URI': 'file:///Users/et.c/work/python/scrapy/xueqiu/xueqiu.json',
        'FEED_URI': 'xueqiu.json',
    }

    def get_stockurl(self, stock):
        url = self.prefix_stockurl + stock['symbol']
        return url
        
    def get_pageurl(self, page):
        url = self.prefix_pageurl + "&size=" + str(self.page_size) + "&"
        return url
        
    def start_requests(self):
        start_url = 'http://xueqiu.com/hq#exchange=CN&firstName=1&secondName=1_0'
        return [ scrapy.Request(url = start_url, callback = self.parse_start_page) ]

    def parse_start_page(self, response):
        self.logger.info('---CALL parse_start_page()---')
        self.pages = 2

        url = self.get_pageurl(1) + "&order=desc"
        yield scrapy.Request(url = url, callback = self.parse_pages)

    def parse_pages(self, response):
        self.logger.info('---CALL parse_pages()---')

        try:
            ajson = json.loads(response.body)
        except ValueError, e:
            self.logger.info('---Exception: %s---', e)
            self.logger.info('---response.status = %s', response.status)
            self.logger.info('---response.body = %s', response.body)
            return
        
        if ajson['success'] == 'true':
            count = ajson['count']['count']
            self.logger.info('---count = %d', count)
            self.pages = int((count + self.page_size - 1) / self.page_size)

        self.logger.info('---pages = %d', self.pages)
        for pageno in range(1, self.pages + 1):
            url = self.get_pageurl(pageno)
            # yield scrapy.Request(url = url)

    def parse(self, response):
        self.logger.info('---CALL parse()---')

        try:
            ajson = json.loads(response.body)
        except ValueError, e:
            self.logger.info('---Exception: %s---', e)
            self.logger.info('---response.status = %s', response.status)
            self.logger.info('---response.body = %s', response.body)
            return

        if ajson['success'] == 'true':
            for stock in ajson['stocks']:
                if False:
                    url = self.get_stockurl(stock)
                    request = scrapy.Request(url = url, callback = self.parse_follows)
                    request.meta['stock'] = stock
                    yield request
                yield stock
        else:
            self.logger.info('---PARSE url = %s', self.pages)

    def parse_follows(self, response):
        self.logger.info('---CALL parse_follows()---')
        self.logger.info('---response.body = %s', response.body)

        stock = response.meta['stock']
        try:
            ajson = json.loads(response.body)
        except ValueError, e:
            self.logger.info('---Exception: %s---', e)
            self.logger.info('---response.status = %s', response.status)
            self.logger.info('---response.body = %s', response.body)
            return

        if 'totalcount' in ajson:
            stock['follows'] = ajson['totalcount']

        return stock


