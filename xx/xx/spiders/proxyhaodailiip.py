# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ProxyhaodailiipSpider(CrawlSpider):
    name = 'proxyhaodailiip'
    allowed_domains = ['haodailiip.com', 'baidu.com']
    start_url = 'http://www.haodailiip.com/'
    test_url = 'http://www.baidu.com/favicon.ico'
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'DOWNLOAD_TIMEOUT': 3,
        'COOKIES_DEBUG': True,
        'RETRY_TIMES': 1,
        'REFERER_ENABLED': False,
        'FEED_FORMAT': 'json',
        'FEED_URI': 'haodailiip.json',
    }

    def start_requests(self):
        start_url = self.start_url + "guonei"
        return [ scrapy.Request(url = start_url, callback = self.parse_pages) ]

    def parse_pages(self, response):
        pageslist = response.xpath('/html/body/center/table[2]/tr/td[1]/p/a/text()').extract()
        self.logger.info('pageslist = %s', pageslist)
        pages = int(pageslist[len(pageslist) - 2])
        self.logger.info('url = %s, pages = %d', response.url, pages)
        pages = 100
        for page in range(1, pages + 1):
            url = response.url + "/" + str(page)
            self.logger.info('get page: %s', url)
            request = scrapy.Request(url = url, callback = self.parse_page)
            yield request

    def parse_page(self, response):
        self.logger.info('parse_page url = %s.', response.url)
        iplist = response.xpath('/html/body/center/table[2]/tr/td[1]/table/tr/td[1]/text()').extract()
        portlist = response.xpath('/html/body/center/table[2]/tr/td[1]/table/tr/td[2]/text()').extract()
        typelist = response.xpath('/html/body/center/table[2]/tr/td[1]/table/tr/td[4]/text()').extract()
        for i, ip in enumerate(iplist):
            if typelist[i].lower() != 'http' or typelist[i].lower() != 'http':
                continue
            ip = re.sub('[\t\n\r]', '', iplist[i])
            port = re.sub('[\t\n\r]', '', portlist[i])
            proxy = typelist[i].lower() + "://" + ip + ":" + port
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

