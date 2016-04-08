# -*- coding: utf-8 -*-
import scrapy
import sys
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class ProxyxicidailiSpider(CrawlSpider):
    name = 'proxyxicidaili'
    allowed_domains = ['xicidaili.com', 'baidu.com']
    start_url = 'http://www.xicidaili.com/'
    test_url = 'http://www.baidu.com/favicon.ico'
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'DOWNLOAD_TIMEOUT': 3,
        'COOKIES_DEBUG': True,
        'RETRY_TIMES': 1,
        'DOWNLOAD_TIMEOUT': 2,
        'REFERER_ENABLED': False,
        'FEED_FORMAT': 'json',
        'FEED_URI': 'xicidaili.json',
    }

    def start_requests(self):
        start_url = self.start_url + "nn"
        return [ scrapy.Request(url = start_url, callback = self.parse_pages) ]

    def parse_pages(self, response):
        pagestr = response.xpath('//*[@id="body"]/div[2]/a[10]/text()').extract()
        self.logger.info('pagestr = %s', pagestr)
        pages = int(pagestr[0])
        self.logger.info('url = %s, pages = %d', response.url, pages)
        for page in range(1, pages + 1):
            url = response.url + "/" + str(page)
            self.logger.info('get page: %s', url)
            request = scrapy.Request(url = url, callback = self.parse_page)
            yield request

    def parse_page(self, response):
        self.logger.info('parse_page url = %s.', response.url)
        iplist = response.xpath('//*[@id="ip_list"]/tr/td[3]/text()').extract()
        portlist = response.xpath('//*[@id="ip_list"]/tr/td[4]/text()').extract()
        typelist = response.xpath('//*[@id="ip_list"]/tr/td[7]/text()').extract()
        for i, ip in enumerate(iplist):
            if typelist[i].lower() != 'http' or typelist[i].lower() != 'http':
                continue
            proxy = typelist[i].lower() + "://" + iplist[i] + ":" + portlist[i]
            self.logger.info('check proxy = %s, starting...', proxy)
            request = scrapy.Request(url = self.test_url + '?' + str(i), callback = self.check_proxy)
            request.meta['proxy'] = proxy
            yield request

    def check_proxy(self, response):
        proxy = response.meta['proxy']
        if response.status == 200 and response.headers['Content-Type'] == 'image/x-icon':
            self.logger.info('check proxy = %s, OK.', proxy)
            yield {'addr': proxy }
        else:
            self.logger.info('check proxy = %s, FAILED.', proxy)

